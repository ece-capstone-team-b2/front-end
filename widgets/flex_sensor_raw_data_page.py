import random
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

from data_processing import ProcessedFlexData
from data_structures import *
from data_view_publisher import DataViewPublisher
from widgets import DataPageInterface


class FlexSensorRawDataPage(DataPageInterface):
    def __init__(
        self, data_source: DataViewPublisher, label: str, visible: bool = False
    ):
        super().__init__()
        self.data_source = data_source
        self.data_source.subscribe(self)
        self.visible = visible
        self.label = label
        self.setup()

    def setup(self):
        layout = QGridLayout(self)

        # labels for left/right
        left_label = QLabel(f"Left {self.label} Angle")
        right_label = QLabel(f"Right {self.label} Angle")
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # plots for left side and right side
        self.left_angle_plot = pg.PlotWidget()
        self.left_angle_plot.setBackground("white")
        self.left_angle_plot.getPlotItem().setTitle("Angles Plot", color="k", size="14")
        self.left_angle_plot.getPlotItem().setLabel("left", "degrees")

        self.right_angle_plot = pg.PlotWidget()
        self.right_angle_plot.setBackground("white")
        self.right_angle_plot.getPlotItem().setTitle(
            "Angles Plot", color="k", size="14"
        )
        self.right_angle_plot.getPlotItem().setLabel("left", "degrees")

        layout.addWidget(left_label, 0, 0, 1, 2)
        layout.addWidget(right_label, 0, 2, 1, 2)
        layout.addWidget(self.left_angle_plot, 1, 0, 2, 2)
        layout.addWidget(self.right_angle_plot, 1, 2, 2, 2)

        self.initializeLines()

    def initializeLines(self):
        self.plot_data = {
            "left": (CappedList(), CappedList()),
            "right": (CappedList(), CappedList()),
        }
        self.plot_items = {
            "left": self.left_angle_plot.getPlotItem(),
            "right": self.right_angle_plot.getPlotItem(),
        }
        self.plot_lines: Dict[str, pg.PlotDataItem] = {}
        for side, plot_item in self.plot_items.items():
            self.plot_lines[side] = plot_item.plot(
                x=self.plot_data[side][0],
                y=self.plot_data[side][1],
                pen=pg.mkPen(color="r", width=3),
                width=5,
            )

    def updateData(self, data: ProcessedFlexData):
        if not isinstance(data, ProcessedFlexData):
            return
        side = "left" if data.nodeId == 1 else "right"
        self.plot_data[side][0].append(data.timestamp)
        self.plot_data[side][1].append(data.bendAngleDegrees)
        if self.visible:
            self.updateLines()

    def updateLines(self):
        for side, lines in self.plot_lines.items():
            lines.setData(x=self.plot_data[side][0], y=self.plot_data[side][1])
