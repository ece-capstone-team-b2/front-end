import random

# as an example

class SensorDataCollector:

    def __init__(self):
        self.sensor = None
        self.counter = 0

    def readData(self):
        self.counter += 1
        print(f"simulating data collection, returned {self.counter}")
        return self.counter