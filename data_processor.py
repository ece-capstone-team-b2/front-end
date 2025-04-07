from data_processing import *
from data_structures import *
from data_view_publisher import DataViewPublisher
from quaternion_math import (
    quaternion_conjugate,
    quaternion_multiply,
    quaternion_to_axis_angle,
    rotate_vector_by_quaternion,
    standard_vector,
)


class DataProcessor:
    def __init__(self, data_source: DataViewPublisher):
        self.data_source = data_source
        self.data_source.subscribe(self)

        self.left_data = {
            "flex_knee_angle": None,
            "thigh_quaternion": None,
            "leg_quaternion": None,
            "insole_force_sum": 0.0,
            "insole_cx": 0.0,
            "insole_cy": 0.0,
            "hip_pos": (0.0, 0.0, 0.0),
            "knee_pos": (0.0, 0.0, 0.0),
            "ankle_pos": (0.0, 0.0, 0.0),
        }

        self.right_data = {
            "flex_knee_angle": None,
            "thigh_quaternion": None,
            "leg_quaternion": None,
            "insole_force_sum": 0.0,
            "insole_cx": 0.0,
            "insole_cy": 0.0,
            "hip_pos": (0.0, 0.0, 0.0),
            "knee_pos": (0.0, 0.0, 0.0),
            "ankle_pos": (0.0, 0.0, 0.0),
        }
        # Segment lengths (arbitrary units)
        self.thigh_length = 4
        self.lower_leg_length = 4
        self.foot_length = 1

        self.output_callbacks = []

    def add_callback(self, callback):
        self.output_callbacks.append(callback)

    def process_imu(self, imu_data):
        device_num = imu_data.nodeId
        if device_num == 2:
            self.right_data["thigh_quaternion"] = imu_data.positionData.quatOrientation
        if device_num == 4:
            self.right_data["leg_quaternion"] = imu_data.positionData.quatOrientation
        if device_num == 1:
            self.left_data["thigh_quaternion"] = imu_data.positionData.quatOrientation
        if device_num == 3:
            self.left_data["leg_quaternion"] = imu_data.positionData.quatOrientation

    def process_insole(self, insole_data: ProcessedInsoleData):
        device_num = insole_data.nodeId
        if device_num == 4:
            self.right_data["insole_force_sum"] = insole_data.totalForce
            self.right_data["insole_cx"] = insole_data.forceCenterX
            self.right_data["insole_cy"] = insole_data.forceCenterY
        elif device_num == 3:
            self.left_data["insole_force_sum"] = insole_data.totalForce
            self.left_data["insole_cx"] = insole_data.forceCenterX
            self.left_data["insole_cy"] = insole_data.forceCenterY
        else:
            return

    def process_flex(self, flex_data: ProcessedFlexData):
        device_num = flex_data.nodeId

        if device_num == 1:
            self.left_data["flex_knee_angle"] = flex_data.bendAngleDegrees
        elif device_num == 2:
            self.right_data["flex_knee_angle"] = flex_data.bendAngleDegrees
        else:
            return

    def calculate_metrics(self):
        metrics = DerivedLegMetrics(
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        )
        for data, side in zip((self.left_data, self.right_data), ("left", "right")):
            if (
                data["flex_knee_angle"] is None
                or data["thigh_quaternion"] is None
                or data["leg_quaternion"] is None
            ):
                continue
            hip = np.array([0, 0, 0])
            # Thigh (hip to knee)
            thigh_vector = standard_vector(self.thigh_length)
            knee = hip + rotate_vector_by_quaternion(
                thigh_vector, data["thigh_quaternion"]
            )
            leg_vector = standard_vector(self.lower_leg_length)

            ankle = knee + rotate_vector_by_quaternion(
                leg_vector, data["leg_quaternion"]
            )

            q_thigh_conj = quaternion_conjugate(data["thigh_quaternion"])
            q_rel = quaternion_multiply(data["leg_quaternion"], q_thigh_conj)
            _, imu_knee_angle = quaternion_to_axis_angle(q_rel)

            imu_knee_angle = np.degrees(imu_knee_angle)

            flex_knee_angle = data["flex_knee_angle"]

            average_angle = imu_knee_angle

            if side == "left":
                metrics.l_knee_angle = average_angle
                metrics.l_foot_force = data["insole_force_sum"]
                metrics.l_force_cx = data["insole_cx"]
                metrics.l_force_cy = data["insole_cy"]
                metrics.l_hip = hip
                metrics.l_knee = knee
                metrics.l_ankle = ankle
            else:
                metrics.r_knee_angle = average_angle
                metrics.r_foot_force = data["insole_force_sum"]
                metrics.r_force_cx = data["insole_cx"]
                metrics.r_force_cy = data["insole_cy"]
                metrics.r_hip = hip
                metrics.r_knee = knee
                metrics.r_ankle = ankle
        if (
            self.left_data["thigh_quaternion"] is not None
            and self.right_data["thigh_quaternion"] is not None
        ):
            l_q_thigh_conj = quaternion_conjugate(self.left_data["thigh_quaternion"])
            l_r_rel = quaternion_multiply(
                self.right_data["thigh_quaternion"], l_q_thigh_conj
            )
            _, thigh_relative = quaternion_to_axis_angle(l_r_rel)

            metrics.thigh_relative_angle_degrees = np.degrees(thigh_relative) - 180

        for callback in self.output_callbacks:
            callback(metrics)

    def updateData(self, data):
        if isinstance(data, ImuData):
            self.process_imu(data)
        elif isinstance(data, ProcessedFlexData):
            self.process_flex(data)
        elif isinstance(data, ProcessedInsoleData):
            self.process_insole(data)
        else:
            return
        self.calculate_metrics()
