from PyQt6.QtWidgets import QGridLayout, QLabel, QTableWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem
from PyQt6.QtCore import Qt
from widgets import DataPageInterface
from data_view_publisher import DataViewPublisher
import pyqtgraph as pg
from data_structures import *
import random
from typing import List, Dict

class FlexSensorRawDataPage(DataPageInterface):
  def __init__(self, data_source: DataViewPublisher, label: str, visible: bool = False):
    super().__init__()
    self.data_source = data_source
    self.data_source.subscribe(self)
    self.visible = visible
    self.label = label
    self.setup()

  def setup(self):
    layout = QGridLayout(self)

    # labels for left/right
    left_label = QLabel(f'Left {self.label} Angle')
    right_label = QLabel(f'Right {self.label} Angle')
    left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    right_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # plots for left side and right side
    self.left_angle_plot = pg.PlotWidget()
    self.left_angle_plot.setBackground('white')
    self.left_angle_plot.getPlotItem().setTitle('Angles Plot', color='k', size='14')
    self.left_angle_plot.getPlotItem().setLabel('left', 'degrees')

    self.right_angle_plot = pg.PlotWidget()
    self.right_angle_plot.setBackground('white')
    self.right_angle_plot.getPlotItem().setTitle('Angles Plot', color='k', size='14')
    self.right_angle_plot.getPlotItem().setLabel('left', 'degrees')

    layout.addWidget(left_label, 0, 0, 1, 2)
    layout.addWidget(right_label, 0, 2, 1, 2)
    layout.addWidget(self.left_angle_plot, 1, 0, 2, 2)
    layout.addWidget(self.right_angle_plot, 1, 2, 2, 2)

    self.initializeLines()

  def initializeLines(self):
    self.plot_data = {
      'left': [],
      'right': []
    }
    self.plot_items = {
      'left': self.left_angle_plot.getPlotItem(),
      'right': self.right_angle_plot.getPlotItem()
    }
    self.plot_lines: Dict[str, pg.PlotDataItem] = {}
    for side, plot_item in self.plot_items.items():
      self.plot_lines[side] = plot_item.plot(
        y=self.plot_data[side],
        pen=pg.mkPen(color='r', width=3),
        width=5
      )

  def updateData(self, data: ImuData):
    # ignoring imu data for now
    self.plot_data['left'].append(random.uniform(0, 90))
    self.plot_data['right'].append(random.uniform(0, 90))
    if self.visible:
      self.updateLines()

  def updateLines(self):
    for side, lines in self.plot_lines.items():
      lines.setData(y=self.plot_data[side])


