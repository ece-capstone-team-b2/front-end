import struct
from typing import Dict, List

import serial.tools.list_ports as list_ports
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QLineEdit,
    QVBoxLayout,
)


from data_logging import DataLogger
from data_structures import *
from data_view_publisher import DataViewPublisher
from style_sheets import *
from widgets import DataPageInterface
from serial_port_capture import *


class SerialPortComboBox(QComboBox):

    def showPopup(self):
        self.refresh_ports()
        super().showPopup()

    def refresh_ports(self):
        current_selection = self.currentText()
        self.clear()
        ports = list_serial_ports()
        self.addItems(ports)
        # Reselect previous value if it's still available
        if current_selection in ports:
            self.setCurrentText(current_selection)


class DataControlsPage(DataPageInterface):
    def __init__(self, data_source: DataViewPublisher, visible: bool):
        super().__init__()
        self.data_source = data_source
        self.record_data = False
        self.read_data = False
        self.data_source.subscribe(self)

        self.port_dropdown = SerialPortComboBox()
        self.read_serial_button = QPushButton()
        self.read_bin_file_button = QPushButton()
        self.bin_file_path_box = QLineEdit()
        self.csv_logger = None
        self.log_prefix_box = QLineEdit()
        self.log_button = QPushButton()
        self.visible = visible
        self.setup()

    def read_serial_clicked(self):
        if self.data_source:
            self.data_source.stop_reading()
        if self.read_data:
            self.read_data = False
            self.read_serial_button.setText("Read data from serial port")
            self.read_bin_file_button.setText("Read data from binary file")
            return  # Return early because this was a request to stop reading
        self.data_source.read_from_serial_port(self.port_dropdown.currentText())
        self.read_data = True
        self.read_serial_button.setText("Stop reading from serial port")
        self.read_bin_file_button.setText("Read data from binary file")
        if self.record_data:
            _, bin_file = (
                f"{self.log_prefix_box.text()}.{ext}" for ext in (".csv", ".bin")
            )
            self.data_source.start_logging(bin_file)

    def read_file_clicked(self):
        if self.data_source:
            self.data_source.stop_reading()
        if self.read_data:
            self.read_data = False

            self.read_serial_button.setText("Read data from serial port")
            self.read_bin_file_button.setText("Read data from binary file")
            return  # Return early because this was a request to stop reading
        self.data_source.read_from_bin_file(self.bin_file_path_box.text())
        self.read_data = True
        self.read_serial_button.setText("Read data from serial port")
        self.read_bin_file_button.setText("Stop reading data from binary file")

    def toggle_recording(self):
        if self.record_data:
            if isinstance(self.data_source, SerialPortCapture):
                self.data_source.data_capture_source.stop_logging()
            if self.csv_logger is not None:
                self.csv_logger = None
            self.record_data = False
            self.log_button.setText("Log data (logs will be {prefix}.csv/.bin)")
        else:
            csv_file, bin_file = (
                f"{self.log_prefix_box.text()}.{ext}" for ext in ("csv", "bin")
            )

            self.csv_logger = DataLogger(csv_file)
            if isinstance(self.data_source.data_capture_source, SerialPortCapture):
                self.data_source.data_capture_source.start_logging(bin_file)
            self.record_data = True

            self.log_button.setText("Stop logging")

    def setup(self):
        layout = QGridLayout(self)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.read_serial_button.setText("Read data from serial port")
        self.read_bin_file_button.setText("Read data from binary file")
        self.log_button.setText("Log data (logs will be {prefix}.csv/.bin)")
        self.log_button.clicked.connect(self.toggle_recording)

        self.read_serial_button.clicked.connect(self.read_serial_clicked)
        self.read_bin_file_button.clicked.connect(self.read_file_clicked)

        layout.addWidget(self.bin_file_path_box, 0, 0)
        layout.addWidget(self.read_bin_file_button, 0, 1)
        layout.addWidget(self.port_dropdown, 1, 0)
        layout.addWidget(self.read_serial_button, 1, 1)
        layout.addWidget(self.log_prefix_box, 2, 0)
        layout.addWidget(self.log_button, 2, 1)

    def updateData(self, data: ImuData):
        if self.csv_logger is not None:
            self.csv_logger.update(data)
