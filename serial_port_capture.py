import struct
from queue import Queue
from threading import Thread
import time

import serial
from serial.tools import list_ports

from crc import get_crc
from data_processing import *
from data_structures import *


def list_serial_ports():
    """List available serial ports."""
    ports = list_ports.comports()
    return [port.device for port in ports]


def select_serial_port(ports):
    """Ask user to select a serial port."""
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")

    while True:
        try:
            index = int(input("Select a port by number: "))
            if 0 <= index < len(ports):
                return ports[index]
        except ValueError:
            pass
        print("Invalid selection. Try again.")


class SerialPortCapture:

    def __init__(self, serial_port, raw_packet_queue):
        self.serial_port: serial.Serial = serial_port
        self.packet_queue = raw_packet_queue
        self.bin_log_file = None
        self.run_log = False
        self.should_run = False
        self.start_time = None

    def start_logging(self, log_filename):
        self.run_log = True
        print(f"Starting logging to {log_filename}")
        self.bin_log_file = log_filename

    def stop_logging(self):
        self.run_log = False

    def start(self):
        self.run_thread = Thread(target=self.collect_data)
        self.should_run = True
        self.run_thread.start()
        self.start_time = time.time() * 1000

    def stop(self):
        self.run_log = False
        self.should_run = False
        self.run_thread.join()

    def collect_data(self):
        while self.should_run:
            length = self.serial_port.read()
            if not length:
                continue
            length = length[0]
            if length == 1:
                continue
            # print(f"Receiving packet of {length} bytes")
            rest_of_packet = self.serial_port.read(length - 1)

            full_packet = bytes([length]) + rest_of_packet

            if self.run_log:

                timestamp = time.time() * 1000 - self.start_time

                timestamp_bytes = struct.pack("< d", timestamp)
                print(f"logging to {self.bin_log_file}")
                with open(self.bin_log_file, "ab") as bin_file:
                    bin_file.write(timestamp_bytes)
                    bin_file.write(full_packet)

            crc = struct.unpack("<H", full_packet[-2:])[0]
            packet_crc = get_crc(full_packet[:-2])
            if packet_crc != crc:
                print(f"Error: Bad CRC: {bin(packet_crc)}, {bin(crc)}")
                continue

            packet_type = full_packet[1]

            if packet_type == IMU_DATA:
                self.parse_imu(full_packet)
            elif packet_type == KNEE_FLEX:
                self.parse_knee_flex(full_packet)
            elif packet_type == INSOLE_FORCE:
                self.parse_insole_force(full_packet)
            else:
                print(f"Error: packet type {packet_type}")

    def parse_imu(self, data) -> ImuData:
        imu_data = unpack_imu_data(data[2:-2])
        # print("Parsing imu data!")
        imu_data = imu_data._replace(timestamp=time.time() * 1000 - self.start_time)
        self.packet_queue.put(imu_data)

    def parse_knee_flex(self, data):
        flex_data = unpack_flex_data(data[2:-2])
        # print("Parsing flex data!")
        flex_data = flex_data._replace(timestamp=time.time() * 1000 - self.start_time)
        self.packet_queue.put(flex_data)

    def parse_insole_force(self, data):
        insole_data = unpack_insole_data(data[2:-2])
        insole_data = insole_data._replace(
            timestamp=time.time() * 1000 - self.start_time
        )
        # print("Parsing Insole data!")
        self.packet_queue.put(insole_data)
