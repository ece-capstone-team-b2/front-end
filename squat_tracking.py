from scipy.stats import linregress

from data_processing import DerivedLegMetrics
from data_processor import DataProcessor


def sliding_average(data, window=5):
    if window < 1:
        raise ValueError("Window size must be at least 1")
    smoothed = []
    for i in range(len(data)):
        start = max(0, i - window + 1)
        window_slice = data[start : i + 1]
        avg = sum(window_slice) / len(window_slice)
        smoothed.append(avg)
    return smoothed


class SquatTracker:
    def __init__(
        self,
        data_processor: DataProcessor,
        ma_window=10,
        slope_window=10,
        squat_threshold=40,
        stand_threshold=20,
        slope_threshold=0.5,
    ):
        self.data_processor = data_processor
        self.data_processor.add_callback(self.new_data)
        self.angles = []
        self.smoothed = []
        self.ma_window = ma_window
        self.slope_window = slope_window
        self.squat_threshold = squat_threshold
        self.stand_threshold = stand_threshold
        self.slope_threshold = slope_threshold
        self.reset()
        self.run = False
        self.callbacks = []

    def request_callback(self, callback):
        self.callbacks.append(callback)

    def start(self):
        self.run = True

    def reset(self):
        self.run = False
        # Rep tracking state
        self.state = "Init"
        self.last_state = "Init"
        self.rep_count = 0
        self.rep_in_progress = False

        # Metrics
        self.l_pressures = []
        self.r_pressures = []
        self.l_knee_angles = []
        self.r_knee_angles = []
        self.l_cy = []
        self.r_cy = []
        self.thigh_angles = []

    def new_data(self, metrics: DerivedLegMetrics):
        if not self.run:
            return
        self.thigh_angles.append(metrics.thigh_relative_angle_degrees)
        self.l_cy.append(metrics.l_force_cy)
        self.r_cy.append(metrics.r_force_cy)
        self.l_pressures.append(metrics.l_foot_force)
        self.r_pressures.append(metrics.r_foot_force)
        self.l_knee_angles.append(metrics.l_knee_angle)
        self.r_knee_angles.append(metrics.r_knee_angle)
        self.update((metrics.l_knee_angle + metrics.r_knee_angle) / 2)

    def moving_average(self, data):
        if len(data) < self.ma_window:
            return data[-1]
        return sum(data[-self.ma_window :]) / self.ma_window

    def get_slope(self, data):
        if len(data) < self.slope_window:
            return 0
        y = data[-self.slope_window :]
        x = list(range(len(y)))
        slope, _, _, _, _ = linregress(x, y)
        return slope

    def update(self, angle):
        self.angles.append(angle)
        self.angles = self.angles[-(self.ma_window + 1) :]
        ma_value = self.moving_average(self.angles)
        self.smoothed.append(ma_value)
        self.smoothed = self.smoothed[-(self.slope_window + 1) :]
        slope = self.get_slope(self.smoothed)
        current_angle = self.smoothed[-1]

        # Classify state
        if slope > self.slope_threshold:
            new_state = "Descending"
        elif slope < -self.slope_threshold:
            if current_angle <= self.stand_threshold:
                new_state = "Completed"
            else:
                new_state = "Ascending"
        else:
            if current_angle >= self.squat_threshold:
                new_state = "At bottom"
            elif current_angle <= self.stand_threshold:
                new_state = "Standing still"
            else:
                new_state = "Transition"
        if self.state != new_state:
            self.last_state = self.state
            self.state = new_state
        print(self.rep_count)
        self.detect_rep()

    def publish_squat_metrics(self):
        avg_l_knee_angles = sliding_average(self.l_knee_angles, 5)
        print("Average left knee angle over last 5 readings:", avg_l_knee_angles)

        avg_r_knee_angles = sliding_average(self.r_knee_angles, 5)
        print("Average right knee angle over last 5 readings:", avg_r_knee_angles)

        max_l_angle = max(avg_l_knee_angles)
        print("Maximum averaged left knee angle:", max_l_angle)

        max_r_angle = max(avg_r_knee_angles)
        print("Maximum averaged right knee angle:", max_r_angle)

        average_thigh_angle = sum(self.thigh_angles) / len(self.thigh_angles)
        print("Average thigh angle:", average_thigh_angle)

        avg_r_foot_force = sum(self.r_pressures) / len(self.r_pressures)
        print("Average force under the right foot:", avg_r_foot_force)

        avg_l_foot_force = sum(self.l_pressures) / len(self.l_pressures)
        print("Average force under the left foot:", avg_l_foot_force)

        avg_r_foot_cy = sum(self.r_cy) / len(self.r_cy)
        print(
            "Average center of pressure Y-position for the right foot:", avg_r_foot_cy
        )

        avg_l_foot_cy = sum(self.l_cy) / len(self.l_cy)
        print("Average center of pressure Y-position for the left foot:", avg_l_foot_cy)

        results = {
            "avg_l_knee_angles": avg_l_knee_angles,
            "avg_r_knee_angles": avg_r_knee_angles,
            "max_l_angle": max_l_angle,
            "max_r_angle": max_r_angle,
            "average_thigh_angle": average_thigh_angle,
            "avg_r_foot_force": avg_r_foot_force,
            "avg_l_foot_force": avg_l_foot_force,
            "avg_r_foot_cy": avg_r_foot_cy,
            "avg_l_foot_cy": avg_l_foot_cy,
        }

        for callback in self.callbacks:
            callback(results)

    def detect_rep(self):
        if self.state == "Descending":
            self.rep_in_progress = True

        if (
            self.rep_in_progress
            and self.state == "Completed"
            and self.last_state == "Ascending"
        ):
            self.rep_count += 1
            self.rep_in_progress = False
            self.publish_squat_metrics()
