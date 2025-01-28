import random

# as an example

class SensorDataCollector:
    def __init__(self):
        self.sensor = None

    def readData(self):
        return random.randint(1,10)