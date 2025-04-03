from serial_port_capture import *
from serial.tools import list_ports


def list_serial_ports():
    """List available serial ports."""
    ports = list_ports.comports()
    return [port.device for port in ports]


def select_serial_port(ports):
    """Ask user to select a serial port."""
    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i}: {port}")

    while True:
        try:
            index = int(input("Select a port by number: "))
            if 0 <= index < len(ports):
                return ports[index]
        except ValueError:
            pass
        print("Invalid selection. Try again.")


if __name__ == "__main__":
    ports = list_serial_ports()
    if not ports:
        print("No serial devices found.")
    else:
        selected_port = select_serial_port(ports)

    port = SerialPortCapture(serial.Serial(selected_port, 115200, timeout=10))
    while True:
        port.collect_data()
