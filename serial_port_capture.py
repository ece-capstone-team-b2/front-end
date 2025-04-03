import serial
from serial.tools import list_ports
import struct
from crc import get_crc
from data_structures import *
from queue import Queue
from threading import Thread
from data_processing import *

IMU_DATA = 0
KNEE_FLEX = 1
INSOLE_FORCE = 2


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

    def __init__(self, serial_port, packet_queue, bin_log_file):
        self.serial_port: serial.Serial = serial_port
        self.packet_queue = packet_queue
        self.bin_log_file = bin_log_file

    def start(self):
        self.run_thread = Thread(target=self.collect_data)
        self.run_thread.start()

    def collect_data(self):
        while True:
            length = self.serial_port.read()
            if not length:
                continue
            length = length[0]
            if length == 1:
                continue
            # print(f"Receiving packet of {length} bytes")
            rest_of_packet = self.serial_port.read(length - 1)

            full_packet = bytes([length]) + rest_of_packet

            with open(self.bin_log_file, "ab") as bin_file:
                bin_file.write(full_packet)

            crc = struct.unpack("<H", full_packet[-2:])[0]
            # print(len(full_packet))
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

        self.packet_queue.put(imu_data)

    def parse_knee_flex(self, data):
        flex_data = unpack_flex_data(data[2:-2])

        self.packet_queue.put(process_flex_data(flex_data))

    def parse_insole_force(self, data):
        insole_data = unpack_insole_data(data[2:-2])

        self.packet_queue.put(
            process_insole_data(insole_data, (insole_data.nodeId == 3))
        )
