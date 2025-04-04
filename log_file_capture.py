import struct
from queue import Queue
from threading import Thread
import time

import serial
from serial.tools import list_ports

from crc import get_crc
from data_processing import *
from data_structures import *


class LogFileCapture:

    def __init__(self, bin_filename, raw_packet_queue):
        self.bin_filename = bin_filename
        self.packet_queue = raw_packet_queue
        self.should_run = False
        self.zero_timestamp = None

    def start(self):
        self.run_thread = Thread(target=self.collect_data)
        self.should_run = True
        self.run_thread.start()
        self.start_time = time.time() * 1000

    def stop(self):
        self.should_run = False
        self.run_thread.join()
        self.start_time = None
        self.zero_timestamp = None

    def collect_data(self):
        with open(self.bin_filename, "rb") as bin_file:
            while self.should_run:
                timestamp_bytes = bin_file.read(8)
                if len(timestamp_bytes) == 0:
                    return
                timestamp = struct.unpack("< d", timestamp_bytes)[0]
                if self.zero_timestamp is None:
                    self.zero_timestamp = timestamp
                timestamp -= self.zero_timestamp
                length_bytes = bin_file.read(1)
                if len(length_bytes) == 0:
                    return
                length = length_bytes[0]
                if not length:
                    continue
                if length == 1:
                    continue
                # print(f"File has packet of length {length}")
                rest_of_packet = bin_file.read(length - 1)

                full_packet = bytes([length]) + rest_of_packet

                crc = struct.unpack("<H", full_packet[-2:])[0]
                packet_crc = get_crc(full_packet[:-2])
                if packet_crc != crc:
                    print(
                        f"Error: Bad CRC: {bin(packet_crc)}, {bin(crc)}, this really shouldn't happen"
                    )
                    continue

                packet_type = full_packet[1]

                if packet_type == IMU_DATA:
                    self.parse_imu(full_packet, timestamp)
                elif packet_type == KNEE_FLEX:
                    self.parse_knee_flex(full_packet, timestamp)
                elif packet_type == INSOLE_FORCE:
                    self.parse_insole_force(full_packet, timestamp)
                else:
                    print(f"Error: packet type {packet_type}")

    def parse_imu(self, data, timestamp) -> ImuData:
        imu_data = unpack_imu_data(data[2:-2])
        imu_data = imu_data._replace(timestamp=timestamp)
        # print("Parsing imu data!")
        while time.time() * 1000 - self.start_time < timestamp:
            time.sleep(0.000001)
        self.packet_queue.put(imu_data)

    def parse_knee_flex(self, data, timestamp):
        flex_data = unpack_flex_data(data[2:-2])
        flex_data = flex_data._replace(timestamp=timestamp)
        # print("Parsing flex data!")
        while time.time() * 1000 - self.start_time < timestamp:
            time.sleep(0.000001)
        self.packet_queue.put(flex_data)

    def parse_insole_force(self, data, timestamp):
        insole_data = unpack_insole_data(data[2:-2])
        insole_data = insole_data._replace(timestamp=timestamp)
        # print("Parsing Insole data!")
        while time.time() * 1000 - self.start_time < timestamp:
            time.sleep(0.000001)
        self.packet_queue.put(insole_data)
