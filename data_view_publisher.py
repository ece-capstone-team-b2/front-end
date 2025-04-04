from typing import List

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget

from queue import Queue

from data_structures import ImuData, FlexData, InsoleData
from data_processing import *
from serial_port_capture import SerialPortCapture
import serial
from log_file_capture import LogFileCapture


# Publishes data to feedback page and raw data page
class DataViewPublisher:
    def __init__(self):
        self.subscribers: List = []
        self.activeTimer = False
        self.timer = QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.retrieveData)
        self.raw_data_queue = Queue()
        self.data_capture_source = None

    def stop_reading(self):
        if self.data_capture_source is not None:
            self.data_capture_source.stop()
        self.data_capture_source = None
        self.timer.stop()

    def read_from_serial_port(self, serial_port_name):
        self.stop_reading()
        self.timer.start()
        self.data_capture_source = SerialPortCapture(
            serial.Serial(serial_port_name, 115200, timeout=1), self.raw_data_queue
        )

        self.data_capture_source.start()

    def read_from_bin_file(self, bin_file_path):
        self.stop_reading()
        self.timer.start()
        print(f"Request to read from binary file {bin_file_path}")
        self.data_capture_source = LogFileCapture(bin_file_path, self.raw_data_queue)
        self.data_capture_source.start()

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def retrieveData(self):
        if not self.raw_data_queue.empty():
            data = self.raw_data_queue.get()
            if isinstance(data, ImuData):
                processed_data = process_imu_data(data)
            elif isinstance(data, FlexData):
                processed_data = process_flex_data(data)
            elif isinstance(data, InsoleData):
                processed_data = process_insole_data(data, (data.nodeId == 3))
            else:
                print("Unexpected type in raw data queue")
            self.notifySubscribers(processed_data)

    def notifySubscribers(self, data):
        for subscriber in self.subscribers:
            subscriber.updateData(data)
