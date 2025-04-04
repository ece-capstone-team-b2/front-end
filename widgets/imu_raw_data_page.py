from typing import Dict, List

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from data_structures import *
from data_view_publisher import DataViewPublisher
from widgets import DataPageInterface

XYZ_AXES = ["x", "y", "z"]
WXYZ_AXES = ["w", "x", "y", "z"]
EULER_AXES = ["roll", "pitch", "yaw"]

plot_config = {
    "accel": XYZ_AXES,
    "gyro": XYZ_AXES,
    "quat": WXYZ_AXES,
    "euler": EULER_AXES,
}

axis_color_config = {
    "x": pg.mkPen(color="r", width=3),
    "y": pg.mkPen(color="g", width=3),
    "z": pg.mkPen(color="b", width=3),
    "w": pg.mkPen(color="c", width=3),
    "roll": pg.mkPen(color="r", width=3),
    "pitch": pg.mkPen(color="b", width=3),
    "yaw": pg.mkPen(color="g", width=3),
}


class ImuRawDataPage(DataPageInterface):
    def __init__(
        self,
        data_source: DataViewPublisher,
        label: str,
        left_node_id: int,
        right_node_id: int,
        visible: bool = False,
    ):
        super().__init__()
        self.label = label
        self.data_source = data_source
        self.data_source.subscribe(self)
        self.data: List[ImuData] = []
        self.visible = visible
        self.left_node_id = left_node_id
        self.right_node_id = right_node_id
        self.setup()

    # setup the layout, plots, and tables
    def setup(self):
        # separate left and right data
        left_right_data_layout = QHBoxLayout(self)
        left_label = QLabel(f"Left {self.label} IMU")
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_label = QLabel(f"Right {self.label} IMU")
        right_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_side = QVBoxLayout()
        right_side = QVBoxLayout()
        left_data_layout = QGridLayout()
        right_data_layout = QGridLayout()
        # adding labels to each side
        left_side.addWidget(left_label)
        left_side.addLayout(left_data_layout)
        right_side.addWidget(right_label)
        right_side.addLayout(right_data_layout)

        # plots and tables for left side of body
        self.accel_plot_left = pg.PlotWidget()
        self.accel_plot_left.setBackground("white")
        self.accel_plot_left.getPlotItem().setTitle("Accel Plot", color="k", size="14")
        self.accel_table_left = create_formatted_table(
            rowHeaders=XYZ_AXES, colHeader="accel"
        )
        self.gyro_plot_left = pg.PlotWidget()
        self.gyro_plot_left.setBackground("white")
        self.gyro_plot_left.getPlotItem().setTitle("Gyro Plot", color="k", size="14")
        self.gyro_table_left = create_formatted_table(
            rowHeaders=XYZ_AXES, colHeader="gyro"
        )
        self.quat_plot_left = pg.PlotWidget()
        self.quat_plot_left.setBackground("white")
        self.quat_plot_left.getPlotItem().setTitle("Quat Plot", color="k", size="14")
        self.quat_table_left = create_formatted_table(
            rowHeaders=WXYZ_AXES, colHeader="quat orient"
        )
        self.euler_plot_left = pg.PlotWidget()
        self.euler_plot_left.setBackground("white")
        self.euler_plot_left.getPlotItem().setTitle("Euler Plot", color="k", size="14")
        self.euler_table_left = create_formatted_table(
            rowHeaders=EULER_AXES, colHeader="euler orient"
        )
        left_data_layout.setRowStretch(0, 2)
        left_data_layout.setRowStretch(1, 2)
        left_data_layout.setRowStretch(2, 1)
        left_data_layout.addWidget(self.accel_plot_left, 0, 0, 1, 2)
        left_data_layout.addWidget(self.gyro_plot_left, 0, 2, 1, 2)
        left_data_layout.addWidget(self.quat_plot_left, 1, 0, 1, 2)
        left_data_layout.addWidget(self.euler_plot_left, 1, 2, 1, 2)
        left_data_layout.addWidget(self.accel_table_left, 2, 0, 2, 1)
        left_data_layout.addWidget(self.gyro_table_left, 2, 1, 2, 1)
        left_data_layout.addWidget(self.quat_table_left, 2, 2, 2, 1)
        left_data_layout.addWidget(self.euler_table_left, 2, 3, 2, 1)

        # plots for right side of body
        self.accel_plot_right = pg.PlotWidget()
        self.accel_plot_right.setBackground("white")
        self.accel_plot_right.getPlotItem().setTitle("Accel Plot", color="k", size="14")
        self.accel_table_right = create_formatted_table(
            rowHeaders=XYZ_AXES, colHeader="accel"
        )
        self.gyro_plot_right = pg.PlotWidget()
        self.gyro_plot_right.setBackground("white")
        self.gyro_plot_right.getPlotItem().setTitle("Gyro Plot", color="k", size="14")
        self.gyro_table_right = create_formatted_table(
            rowHeaders=XYZ_AXES, colHeader="gyro"
        )
        self.quat_plot_right = pg.PlotWidget()
        self.quat_plot_right.setBackground("white")
        self.quat_plot_right.getPlotItem().setTitle("Quat Plot", color="k", size="14")
        self.quat_table_right = create_formatted_table(
            rowHeaders=WXYZ_AXES, colHeader="quat orient"
        )
        self.euler_plot_right = pg.PlotWidget()
        self.euler_plot_right.setBackground("white")
        self.euler_plot_right.getPlotItem().setTitle("Euler Plot", color="k", size="14")
        self.euler_table_right = create_formatted_table(
            rowHeaders=EULER_AXES, colHeader="euler orient"
        )
        right_data_layout.setRowStretch(0, 2)
        right_data_layout.setRowStretch(1, 2)
        right_data_layout.setRowStretch(2, 1)
        right_data_layout.addWidget(self.accel_plot_right, 0, 0, 1, 2)
        right_data_layout.addWidget(self.gyro_plot_right, 0, 2, 1, 2)
        right_data_layout.addWidget(self.quat_plot_right, 1, 0, 1, 2)
        right_data_layout.addWidget(self.euler_plot_right, 1, 2, 1, 2)
        right_data_layout.addWidget(self.accel_table_right, 2, 0, 2, 1)
        right_data_layout.addWidget(self.gyro_table_right, 2, 1, 2, 1)
        right_data_layout.addWidget(self.quat_table_right, 2, 2, 2, 1)
        right_data_layout.addWidget(self.euler_table_right, 2, 3, 2, 1)

        # combine left and right layouts
        left_right_data_layout.addLayout(left_side)
        left_right_data_layout.addLayout(right_side)
        self.setLayout(left_right_data_layout)

        # initialize lines for every plot
        self.initializeLines()

        # dictionary of map table names to table
        # self.table_mape[left|right][accel|gyro|quat|euler] -> returns QTableWidget
        self.table_map: Dict[str, Dict[str, QTableWidget]] = {
            "left": {
                "accel": self.accel_table_left,
                "gyro": self.gyro_table_left,
                "quat": self.quat_table_left,
                "euler": self.euler_table_left,
            },
            "right": {
                "accel": self.accel_table_right,
                "gyro": self.gyro_table_right,
                "quat": self.quat_table_right,
                "euler": self.euler_table_right,
            },
        }

    def initializeLines(self):

        # sample usage:
        # self.plot_data[accel|gyro][left|right][x|y|z] -> returns list (initially empty), containing data points
        # self.plot_data[quat][left|right][w|x|y|z]
        # self.plot_data[euler][left|right][roll|pitch|yaw]
        self.plot_data: Dict[str, Dict[str, Dict[str, List[float]]]] = {}
        for plot_name, axes in plot_config.items():
            self.plot_data[plot_name] = {
                "left": initialize_plot_data(axes),
                "right": initialize_plot_data(axes),
            }

        # self.plot_items[accel|gyro|quat|euler][left|right] -> returns PlotItem, where lines will be plotted
        self.plot_items: Dict[str, Dict[str, pg.PlotItem]] = {
            "accel": {
                "left": self.accel_plot_left.getPlotItem(),
                "right": self.accel_plot_right.getPlotItem(),
            },
            "gyro": {
                "left": self.gyro_plot_left.getPlotItem(),
                "right": self.gyro_plot_right.getPlotItem(),
            },
            "quat": {
                "left": self.quat_plot_left.getPlotItem(),
                "right": self.quat_plot_right.getPlotItem(),
            },
            "euler": {
                "left": self.euler_plot_left.getPlotItem(),
                "right": self.euler_plot_right.getPlotItem(),
            },
        }

        # sample usage:
        # self.plot_lines[accel|gyro][left|right][x|y|z] -> returns PlotDataItem for line
        # self.plot_lines[quat][left|right][w|x|y|z]
        # self.plot_lines[euler][left|right][roll|pitch|yaw]
        self.plot_lines: Dict[str, Dict[str, Dict[str, pg.PlotDataItem]]] = {}

        for plot_name, axes in plot_config.items():
            # get the left and right plot items (to add lines to)
            plot_left_item = self.plot_items[plot_name]["left"]
            plot_right_item = self.plot_items[plot_name]["right"]
            plot_left_item.addLegend().setOffset((0, 1))
            plot_right_item.addLegend()
            self.plot_lines[plot_name] = {
                "left": {
                    # for each axis (w,x,y,z,roll,pitch,yaw) in this particular plot, get the data
                    axis: plot_left_item.plot(
                        x=self.plot_data[plot_name]["left"][axis][0],
                        y=self.plot_data[plot_name]["left"][axis][1],
                        name=axis,
                        pen=axis_color_config[axis],
                        width=5,
                    )
                    for axis in axes
                },
                "right": {
                    axis: plot_right_item.plot(
                        x=self.plot_data[plot_name]["right"][axis][0],
                        y=self.plot_data[plot_name]["right"][axis][1],
                        name=axis,
                        pen=axis_color_config[axis],
                        width=5,
                    )
                    for axis in axes
                },
            }

    # *** update the data to render ***
    def updateData(self, data: ImuData):
        if not isinstance(data, ImuData) or (
            data.nodeId != self.left_node_id and data.nodeId != self.right_node_id
        ):
            return
        plot_values = {
            "accel": data.accelData,
            "gyro": data.gyroData,
            "quat": data.positionData.quatOrientation,
            "euler": data.positionData.eulerOrientation,
        }
        self.data.append(data)
        for plot_name, new_data in plot_values.items():
            for axis in plot_config[plot_name]:
                value = getattr(new_data, axis)
                side = "left" if data.nodeId == self.left_node_id else "right"
                self.plot_data[plot_name][side][axis][0].append(data.timestamp)
                self.plot_data[plot_name][side][axis][1].append(value)

        if self.visible:
            self.updateLines()
            self.updateTables(plot_values)

    def updateLines(self):
        for plot_name, plots in self.plot_lines.items():
            for side, axes in plots.items():
                for axis, line in axes.items():
                    line.setData(
                        x=self.plot_data[plot_name][side][axis][0],
                        y=self.plot_data[plot_name][side][axis][1],
                    )
                    line.appendData()
                    line.setData

    def updateTables(self, table_data):
        for side, tables in self.table_map.items():
            for table_name, table in tables.items():
                data = table_data[table_name]
                for i, axis in enumerate(data):
                    table.setItem(i, 0, QTableWidgetItem(f"{axis:.5f}"))


# helpers
def create_formatted_table(rowHeaders: List[str], colHeader: str):
    table = QTableWidget()
    table.setRowCount(len(rowHeaders))
    table.setColumnCount(1)
    table.setHorizontalHeaderLabels([colHeader])
    table.setVerticalHeaderLabels(rowHeaders)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    return table


# returns { axis name : list of data points }
def initialize_plot_data(axes: List[str]):
    return {axis: (CappedList(), CappedList()) for axis in axes}
