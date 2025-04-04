import random
from typing import Dict

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPen, QRadialGradient, QTransform
from PyQt6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsSimpleTextItem,
    QGraphicsTextItem,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from data_processing import ProcessedInsoleData
from data_structures import *
from data_view_publisher import DataViewPublisher
from widgets import DataPageInterface

left_foot_pressure_points = [
    (16.9, 85),
    (-16.9, 85),
    (25.1, 49.5),
    (-4.8, 43.3),
    (-30.1, 28.6),
    (-26.9, -19.5),
    (13.1, -88.8),
    (-14.5, -88.8),
]

ellipse_width = 87.74
ellipse_height = 236.78
mini_ellipse_width = 20
mini_ellipse_height = 32

grid_size = 400


class ForceRawDataPage(DataPageInterface):
    def __init__(
        self, data_source: DataViewPublisher, label: str, visible: bool = False
    ):
        super().__init__()
        self.label = label
        self.data_source = data_source
        self.data_source.subscribe(self)
        self.visible = visible
        self.setup()

    def setup(self):
        layout = QGridLayout(self)

        # labels for left/right
        left_label = QLabel(f"Left {self.label} Pressure")
        right_label = QLabel(f"Right {self.label} Pressure")
        left_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # plots for left side and right side
        self.left_foot_plot = pg.PlotWidget()
        self.left_foot_plot.setAspectLocked(True)
        self.left_foot_plot.setBackground("white")
        self.left_foot_plot.getPlotItem().setTitle(
            "Insole Pressure Plot", color="k", size="14"
        )

        self.right_foot_plot = pg.PlotWidget()
        self.right_foot_plot.setAspectLocked(True)
        self.right_foot_plot.setBackground("white")
        self.right_foot_plot.getPlotItem().setTitle(
            "Insole Pressure Plot", color="k", size="14"
        )

        # [left|right][node#] -> QGraphicsEllipseItem
        self.pressure_points: Dict[str, Dict[int, QGraphicsEllipseItem]] = {
            "left": {},
            "right": {},
        }
        # [left|right][node#] -> QGraphicsTextItem
        self.labels: Dict[str, Dict[int, QGraphicsSimpleTextItem]] = {
            "left": {},
            "right": {},
        }
        # add pressure points and labels
        for idx, point in enumerate(left_foot_pressure_points):
            x, y = point
            ellipse_left = QGraphicsEllipseItem(
                x - mini_ellipse_width / 2,
                y - mini_ellipse_height / 2,
                mini_ellipse_width,
                mini_ellipse_height,
            )
            ellipse_right = QGraphicsEllipseItem(
                -x - mini_ellipse_width / 2,
                y - mini_ellipse_height / 2,
                mini_ellipse_width,
                mini_ellipse_height,
            )
            ellipse_left.setPen(pg.mkPen(color="w"))
            ellipse_right.setPen(pg.mkPen(color="w"))
            self.pressure_points["left"][idx] = ellipse_left
            self.pressure_points["right"][idx] = ellipse_right
            self.left_foot_plot.addItem(ellipse_left)
            self.right_foot_plot.addItem(ellipse_right)
            label_left = self.createLabel(x, y)
            label_right = self.createLabel(-x, y)
            self.labels["left"][idx] = label_left
            self.labels["right"][idx] = label_right
            self.left_foot_plot.addItem(label_left)
            self.right_foot_plot.addItem(label_right)
        layout.addWidget(left_label, 0, 0, 1, 2)
        layout.addWidget(right_label, 0, 2, 1, 2)
        layout.addWidget(self.left_foot_plot, 1, 0, 2, 2)
        layout.addWidget(self.right_foot_plot, 1, 2, 2, 2)

        self.initializeLines()

    def createLabel(self, x: float, y: float):
        label = QGraphicsSimpleTextItem("0")
        label.setPos(x - mini_ellipse_width / 3, y - mini_ellipse_height / 3 + 5)
        label.setFont(QFont("Arial", 8))
        # https://github.com/pyqtgraph/pyqtgraph/issues/2804
        y1 = label.boundingRect().height()
        label.setTransform(QTransform(1, 0, 0, -1, 0, y1))
        return label

    def initializeLines(self):
        left_foot = QGraphicsEllipseItem(
            -ellipse_width / 2, -ellipse_height / 2, ellipse_width, ellipse_height
        )
        left_foot.setPen(pg.mkPen(width=2, color="r"))
        self.left_foot_plot.addItem(left_foot)
        right_foot = QGraphicsEllipseItem(
            -ellipse_width / 2, -ellipse_height / 2, ellipse_width, ellipse_height
        )
        right_foot.setPen(pg.mkPen(width=2, color="r"))
        self.right_foot_plot.addItem(right_foot)

    # ignoring imu data
    def updateData(self, data: ProcessedInsoleData):
        if not isinstance(data, ProcessedInsoleData):
            return
        cmap = pg.ColorMap(
            [0.0, 1.0], [pg.mkColor(255, 255, 255), pg.mkColor(255, 0, 0)]
        )
        side = "left" if data.nodeId == 3 else "right"
        for node, ellipse in self.pressure_points[side].items():
            x, y = left_foot_pressure_points[node]
            weight = data.calculatedForces[node]
            gradient = QRadialGradient(
                x if side == "left" else -x, y, mini_ellipse_width
            )
            gradient.setColorAt(0, cmap.mapToQColor(weight))
            gradient.setColorAt(1, QColor(255, 255, 255))
            ellipse.setBrush(QBrush(gradient))
            self.labels[side][node].setText(f"{weight:.2f}")


# horrible attempt at interpolated heatmap

# normalized_pressures = [pressure/max(random_pressures) for pressure in random_pressures]
# x_min, x_max = left_foot_pressure_points[:, 0].min(), left_foot_pressure_points[:,0].max()
# y_min, y_max = left_foot_pressure_points[:, 1].min(), left_foot_pressure_points[:,1].max()
# grid_x, grid_y = np.mgrid[-30:30:50j, -100:100:50j]
# # grid_x, grid_y = np.mgrid[-28.2:31:50j, -96.8:96.5:50j]
# # grid_x, grid_y = np.mgrid[-20:20:50j, -80:80:50j]
# grid_z = griddata(left_foot_pressure_points, random_pressures, (grid_x, grid_y), method='cubic')
# grid_z = np.nan_to_num(grid_z, nan=0.0)
# mask = ((grid_x**2/(ellipse_width/4)**2) + (grid_y**2)/((ellipse_height/2)**2)) <= 1
# grid_z[~mask]=0
# # grid_x, grid_y = np.meshgrid(x, y)
# # interpolated = griddata(left_foot_pressure_points, random_pressures, (grid_x, grid_y), method='cubic')
# # heatmap = pg.ImageItem(interpolated)
# # heatmap.setOpts(interpolation='linear')
# # heatmap.setLookupTable(pg.colormap.get('viridis').getLookupTable())
# heatmap = pg.ImageItem()
# heatmap.setImage(grid_z)
# heatmap.setRect(pg.QtCore.QRectF(-ellipse_width/2 + 5.9, -ellipse_height/2, ellipse_width, ellipse_height))
# heatmap.setZValue(-1)
# # heatmap.setLookupTable(pg.colormap.get('viridis').getLookupTable())
# cmap = pg.ColorMap([0.0, 1.0], [pg.mkColor(255,255,255), pg.mkColor(255,160,160)])
# heatmap.setLookupTable(cmap.getLookupTable())
# self.left_foot_plot.addItem(heatmap)
# heatmap.setImage(interpolated)
# heatmap.setColorMap(pg.colormap.get('viridis'))
# heatmap = np.zeros((grid_size, grid_size))
# for (point, pressure) in zip(left_foot_pressure_points, random_pressures):
#   x, y = point
#   heatmap[int(-y+250), int(x+250)] = pressure

# mask = np.zeros((grid_size, grid_size))
# map_center = (grid_size // 2, grid_size // 2)
# for x in range(grid_size):
#   for y in range(grid_size):
#     dx = x - map_center[0]
#     dy = y - map_center[1]
#     if (dx ** 2)/((ellipse_width/2)**2) + (dy ** 2)/((ellipse_height/2)**2) <= 1:
#       mask[y, x] = 1

# masked_heatmap = heatmap * mask
# # print(masked_heatmap)

# cmap = pg.ColorMap([0, 0.2, 0.4, 0.6, 0.8, 1],
#                [(0, 0, 255), (0, 255, 255), (0, 255, 0), (255, 255, 0), (255, 0, 0), (255, 0, 0)])
# heatmap_image = pg.ImageItem(masked_heatmap)
# heatmap_image.setColorMap
# # heatmap_image.setLookupTable(cmap.getLookupTable(255))
# self.left_foot_plot.addItem(heatmap_image)

# masked_heatmap = masked_heatmap / np.max(masked_heatmap)
# x, y = point
# grid_x = int((x + 50) % grid_size)
# grid_y = int((y + 100) % grid_size)
# heatmap[grid_y, grid_x] = pressure
# colors = cmap.map(normalized)
# scatter = pg.ScatterPlotItem(left_foot_pressure_points_x, left_foot_pressure_points_y, brush=colors)
# self.left_foot_plot.addItem(scatter)
