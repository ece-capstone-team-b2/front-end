import csv
from datetime import datetime
import time

from data_structures import ImuData, Axis3d
from sensor_data_collector import read_serial_data, unpack_imu_data


def unpack_axis3d(data: Axis3d):
    return [data.x, data.y, data.z]


def get_unpacked_row(data: ImuData):
    return [*unpack_axis3d(data.accelData), *unpack_axis3d(data.linearAccelData), *unpack_axis3d(data.gravityAccel),
            *unpack_axis3d(data.gyroData), *unpack_axis3d(data.magData), *unpack_axis3d(data.positionData.position)]


if __name__ == "__main__":
    with open(f"out-{datetime.now()}", "w") as output_file:
        writer = csv.writer(output_file)

        writer.writerow(["accelData", "linearAccelData", "gravityAccel", "gyroData", "magData", "positionData"])

        while True:
            data = read_serial_data("/dev/ttyACM0")
            unpacked: ImuData = unpack_imu_data(data)

            print(unpacked.accelData.x)

            unpacked_row = get_unpacked_row(unpacked)

            writer.writerow(unpacked_row)

            time.sleep(0.5)
