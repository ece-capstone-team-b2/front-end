from abc import abstractmethod
from PyQt6.QtWidgets import QWidget

class DataPageInterface(QWidget):
    @abstractmethod
    def updateData(self):
        pass