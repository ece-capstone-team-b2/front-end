import time
from data_structures import *
from data_processing import *
import csv


def get_imu_csv_columns(node_id: int) -> list[str]:
    prefix = f"node_{node_id}_imu"
    columns = []

    def add_axis3d(name: str):
        for axis in ["x", "y", "z"]:
            columns.append(f"{prefix}_{name}_{axis}")

    def add_quaternion(name: str):
        for part in ["w", "x", "y", "z"]:
            columns.append(f"{prefix}_{name}_{part}")

    def add_euler(name: str):
        for part in ["roll", "pitch", "yaw"]:
            columns.append(f"{prefix}_{name}_{part}")

    # Add top-level fields
    add_axis3d("accelData")
    add_axis3d("gyroData")
    add_axis3d("magData")

    # Add nested PositionData fields
    add_quaternion("positionData_quatOrientation")

    return columns


def voltage_divider_columns(base: str) -> list[str]:
    return [
        f"{base}_calculatedResistance",
    ]


def get_flex_csv_columns(node_id: int) -> list[str]:
    prefix = f"node_{node_id}_flex"
    columns = []
    columns += voltage_divider_columns(f"{prefix}_flexData")
    columns.append(f"{prefix}_bendAngleDegrees")
    return columns


def get_insole_csv_columns(node_id: int) -> list[str]:
    prefix = f"node_{node_id}_insole"
    columns = []

    # Raw VoltageDividerData for each sensor
    for i in range(NUM_INSOLE_PRESSURE):
        base = f"{prefix}_insoleData_{i}"
        columns += voltage_divider_columns(base)

    # Calculated forces
    for i in range(NUM_INSOLE_PRESSURE):
        columns.append(f"{prefix}_calculatedForce_{i}")

    # Center of pressure
    columns.append(f"{prefix}_forceCenterX")
    columns.append(f"{prefix}_forceCenterY")

    return columns


def get_all_csv_rows():
    node_1_rows = get_imu_csv_columns(1) + get_flex_csv_columns(1)
    node_2_rows = get_imu_csv_columns(2) + get_flex_csv_columns(2)
    node_3_rows = get_imu_csv_columns(3) + get_insole_csv_columns(3)
    node_4_rows = get_imu_csv_columns(4) + get_insole_csv_columns(4)
    return ["timestamp_ms"] + node_1_rows + node_2_rows + node_3_rows + node_4_rows


def flatten_voltage_divider(data: VoltageDividerData) -> list[float]:
    return [data[2]]


def flatten_imu_data(data: ImuData) -> list[float]:
    values = []

    def flatten_axis3d(a: Axis3d):
        return [a.x, a.y, a.z]

    def flatten_quat(q: Quaternion):
        return [q.w, q.x, q.y, q.z]

    def flatten_euler(e: EulerAngles):
        return [e.roll, e.pitch, e.yaw]

    values += flatten_axis3d(data.accelData)
    values += flatten_axis3d(data.gyroData)
    values += flatten_axis3d(data.magData)

    pos = data.positionData
    values += flatten_quat(pos.quatOrientation)

    return values


def flatten_processed_insole_data(data: ProcessedInsoleData) -> list[float]:
    values = []

    # Raw voltage divider data from insole
    for vd in data.raw.insoleData:
        values += flatten_voltage_divider(vd)

    # Calculated forces
    values += list(data.calculatedForces)

    # Center of pressure
    values.append(data.forceCenterX)
    values.append(data.forceCenterY)

    return values


def flatten_processed_flex_data(data: ProcessedFlexData) -> list[float]:
    values = []
    values += flatten_voltage_divider(data.raw.flexData)
    values.append(data.bendAngleDegrees)
    return values


class DataLogger:

    def __init__(self, csv_file):
        empty_imu = ImuData(
            nodeId=0,
            accelData=Axis3d(0.0, 0.0, 0.0),
            linearAccelData=Axis3d(0.0, 0.0, 0.0),
            gravityAccel=Axis3d(0.0, 0.0, 0.0),
            gyroData=Axis3d(0.0, 0.0, 0.0),
            magData=Axis3d(0.0, 0.0, 0.0),
            positionData=PositionData(
                position=Axis3d(0.0, 0.0, 0.0),
                quatOrientation=Quaternion(1.0, 0.0, 0.0, 0.0),
                eulerOrientation=EulerAngles(0.0, 0.0, 0.0),
            ),
            sysCalibration=0,
            accelCalibration=0,
            gyroCalibration=0,
            magCalibration=0,
        )
        empty_flex = ProcessedFlexData(
            nodeId=0,
            raw=FlexData(nodeId=0, flexData=VoltageDividerData(0, 0.0, 0.0)),
            bendAngleDegrees=0.0,
        )
        empty_insole = ProcessedInsoleData(
            nodeId=0,
            raw=InsoleData(
                nodeId=0,
                insoleData=tuple(
                    VoltageDividerData(0, 0.0, 0.0) for _ in range(NUM_INSOLE_PRESSURE)
                ),
            ),
            calculatedForces=tuple(0.0 for _ in range(NUM_INSOLE_PRESSURE)),
            forceCenterX=0.0,
            forceCenterY=0.0,
        )
        self.imu_data = [empty_imu, empty_imu, empty_imu, empty_imu]
        self.flex_data = [empty_flex, empty_flex]
        self.insole_data = [empty_insole, empty_insole]
        self.csv_file = csv_file
        with open(csv_file, "a") as datafile:
            writer = csv.writer(datafile)
            writer.writerow(get_all_csv_rows())
        self.start_time = time.time() * 1000

    def update(self, data):

        device_num = data.nodeId

        if isinstance(data, ImuData):
            self.imu_data[device_num - 1] = data
        elif isinstance(data, ProcessedFlexData):
            self.flex_data[device_num - 1] = data
        elif isinstance(data, ProcessedInsoleData):
            self.insole_data[device_num - 3] = data
        else:
            print("Invalid packet type")

        columns = (
            [(time.time() * 1000) - self.start_time]
            + flatten_imu_data(self.imu_data[0])
            + flatten_processed_flex_data(self.flex_data[0])
            + flatten_imu_data(self.imu_data[1])
            + flatten_processed_flex_data(self.flex_data[1])
            + flatten_imu_data(self.imu_data[2])
            + flatten_processed_insole_data(self.insole_data[0])
            + flatten_imu_data(self.imu_data[3])
            + flatten_processed_insole_data(self.insole_data[1])
        )
        with open(self.csv_file, "a") as datafile:
            writer = csv.writer(datafile)
            writer.writerow(columns)
