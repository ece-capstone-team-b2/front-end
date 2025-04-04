import struct
from collections import namedtuple
from typing import NamedTuple

import numpy as np

IMU_DATA = 0
KNEE_FLEX = 1
INSOLE_FORCE = 2

Axis3d = namedtuple("Axis3d", ["x", "y", "z"])
Quaternion = namedtuple("Quaternion", ["w", "x", "y", "z"])
EulerAngles = namedtuple("EulerAngles", ["roll", "pitch", "yaw"])


class VoltageDividerData(NamedTuple):
    adcRawCount: int
    outputVoltage: float
    calculatedResistance: float


class PositionData(NamedTuple):
    position: Axis3d
    quatOrientation: Quaternion
    eulerOrientation: EulerAngles


imu_struct_format = "< 18d 4d 3d 4B"


class ImuData(NamedTuple):
    nodeId: int
    accelData: Axis3d
    linearAccelData: Axis3d
    gravityAccel: Axis3d
    gyroData: Axis3d
    magData: Axis3d
    positionData: PositionData
    sysCalibration: int
    accelCalibration: int
    gyroCalibration: int
    magCalibration: int
    timestamp: float


voltage_divider_struct_format = "< I 2d"


class FlexData(NamedTuple):
    nodeId: int
    flexData: VoltageDividerData
    timestamp: float


NUM_INSOLE_PRESSURE = 8


class InsoleData(NamedTuple):
    nodeId: int
    insoleData: tuple[
        VoltageDividerData,
        VoltageDividerData,
        VoltageDividerData,
        VoltageDividerData,
        VoltageDividerData,
        VoltageDividerData,
        VoltageDividerData,
        VoltageDividerData,
    ]
    timestamp: float


def unpack_insole_data(binary_data: bytes) -> InsoleData:
    nodeId = binary_data[0]

    binary_data = binary_data[1:]
    if len(binary_data) != NUM_INSOLE_PRESSURE * struct.calcsize(
        voltage_divider_struct_format
    ):
        raise ValueError(
            f"Invalid binary data size: Expected {struct.calcsize(voltage_divider_struct_format)}, received {len(binary_data)}"
        )
    insoleData = list()

    entry_size = struct.calcsize(voltage_divider_struct_format)

    for i in range(NUM_INSOLE_PRESSURE):
        insoleData.append(
            struct.unpack(
                voltage_divider_struct_format,
                binary_data[i * entry_size : (i + 1) * entry_size],
            )
        )

    return InsoleData(nodeId, insoleData, 0)


def unpack_flex_data(binary_data: bytes) -> FlexData:
    nodeId = binary_data[0]

    binary_data = binary_data[1:]

    if len(binary_data) != struct.calcsize(voltage_divider_struct_format):
        raise ValueError(
            f"Invalid binary data size: Expected {struct.calcsize(voltage_divider_struct_format)}, received {len(binary_data)}"
        )
    unpacked = struct.unpack(voltage_divider_struct_format, binary_data)
    flexData = VoltageDividerData(*unpacked)

    return FlexData(nodeId, flexData, 0)


def unpack_imu_data(binary_data: bytes) -> ImuData:

    nodeId = binary_data[0]

    binary_data = binary_data[1:]
    if len(binary_data) != struct.calcsize(imu_struct_format):
        raise ValueError(
            f"Invalid binary data size: Expected {struct.calcsize(imu_struct_format)}, received {len(binary_data)}"
        )
    unpacked = struct.unpack(imu_struct_format, binary_data)

    accelData = Axis3d(*unpacked[0:3])
    linearAccelData = Axis3d(*unpacked[3:6])
    gravityAccel = Axis3d(*unpacked[6:9])
    gyroData = Axis3d(*unpacked[9:12])
    magData = Axis3d(*unpacked[12:15])

    position = Axis3d(*unpacked[15:18])
    quatOrientation = Quaternion(*unpacked[18:22])
    eulerOrientation = EulerAngles(*unpacked[22:25])
    positionData = PositionData(position, quatOrientation, eulerOrientation)

    sysCalibration, accelCalibration, gyroCalibration, magCalibration = unpacked[25:]

    return ImuData(
        nodeId,
        accelData,
        linearAccelData,
        gravityAccel,
        gyroData,
        magData,
        positionData,
        sysCalibration,
        accelCalibration,
        gyroCalibration,
        magCalibration,
        0,
    )


from collections import deque


import numpy as np


class CappedList:
    def __init__(self, max_length=100):
        self.max_length = max_length
        self.data = np.empty(max_length, dtype=float)
        self.size = 0
        self.start = 0  # circular buffer start index

    def append(self, value):
        idx = (self.start + self.size) % self.max_length
        if self.size < self.max_length:
            self.data[idx] = value
            self.size += 1
        else:
            self.data[self.start] = value
            self.start = (self.start + 1) % self.max_length

    def __getitem__(self, index):
        if not 0 <= index < self.size:
            raise IndexError("index out of bounds")
        return self.data[(self.start + index) % self.max_length]

    def __len__(self):
        return self.size

    def __array__(self):
        if self.start + self.size <= self.max_length:
            return self.data[self.start : self.start + self.size]
        else:
            end = (self.start + self.size) % self.max_length
            return np.concatenate((self.data[self.start :], self.data[:end]))
