import struct
from data_structures import *

imu_struct_format = "< 18d 4d 3d 4B"
sample_data_file_path = 'sample_data/imu_data.bin'

imu_struct_size = struct.calcsize(imu_struct_format)

# example data collector
class SensorDataCollector:

    def __init__(self):
        self.sensor = None
        self.data_generator = read_bin_chunks(sample_data_file_path)

    def readData(self):
        data = read_data(self.data_generator)
        return data


def read_bin_chunks(filepath, chunk_size=struct.calcsize(imu_struct_format)):
    with open(filepath, "rb") as bin_file:
        while chunk := bin_file.read(chunk_size):
            yield chunk

def read_data(data_generator):
        data = next(data_generator)
        imudata = unpack_imu_data(data)
        return imudata

def unpack_imu_data(binary_data):
    if len(binary_data) != imu_struct_size:
        raise ValueError("Invalid binary data size")
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
        accelData, linearAccelData, gravityAccel, gyroData, magData, positionData,
        sysCalibration, accelCalibration, gyroCalibration, magCalibration
    )