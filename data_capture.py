from serial_port_capture import *
from data_processing import *


if __name__ == "__main__":
    ports = list_serial_ports()
    if not ports:
        print("No serial devices found.")
    else:
        selected_port = select_serial_port(ports)
    queue = Queue()

    serial_monitor = SerialPortCapture(
        serial.Serial(selected_port, 115200, timeout=1), queue
    )
    serial_monitor.start()

    while True:
        data = queue.get()
        if isinstance(data, ImuData):
            # print(f"Received IMU Data from {data.nodeId}")
            pass
        elif isinstance(data, FlexData):
            # print(
            #     f"Received Flex Data from {data.nodeId} {data.flexData.calculatedResistance}"
            # )
            pass
        elif isinstance(data, InsoleData):
            processed_data = process_insole_data(data, data.nodeId == 3)
            # print(f"Received Insole Data from {data.nodeId}")
            print(processed_data.forceCenterX)
            print(processed_data.forceCenterY)
            pass
        else:
            print(f"Unknown packet type")
