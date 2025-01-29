import random

# as an example

class SensorDataCollector:
    def __init__(self):
        self.sensor = None

    def readData(self):
        ret = random.randint(1,10)
        print(f"simulating data collection, returned {ret}")
        return ret