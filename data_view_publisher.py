from typing import List
from widgets.data_page_interface import DataPageInterface
from sensor_data_collector import SensorDataCollector
from PyQt6.QtWidgets import QWidget, QWidget
from PyQt6.QtCore import QTimer

class DataViewPublisher:
    def __init__(self):
        self.sensorDataCollector = SensorDataCollector()
        self.subscribers: List[DataPageInterface]= []
        self.activeTimer = False
        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.retrieveData)

    def subscribe(self, subscriber: QWidget):
        self.subscribers.append(subscriber)

    def retrieveData(self):
        data = self.sensorDataCollector.readData()
        self.notifySubscribers(data)

    def notifySubscribers(self, data):
        for subscriber in self.subscribers:
            subscriber.updateData(data)

    def toggleCollectData(self, exercise: str):
        if self.activeTimer:
            print(f"Data collection stopped for {exercise}")
            self.timer.stop()
            self.activeTimer = False
        else:
            print(f"Data collection started for {exercise}")
            self.timer.start()
            self.activeTimer = True
