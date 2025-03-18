from collections import namedtuple
from typing import NamedTuple

Axis3d = namedtuple("Axis3d", ["x", "y", "z"])
Quaternion = namedtuple("Quaternion", ["w", "x", "y", "z"])
EulerAngles = namedtuple("EulerAngles", ["roll", "pitch", "yaw"])

class PositionData(NamedTuple):
    position: Axis3d
    quatOrientation: Quaternion
    eulerOrientation: EulerAngles

class ImuData(NamedTuple):
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



