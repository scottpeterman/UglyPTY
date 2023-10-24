from PyQt6.QtCore import pyqtSignal, QThread
import serial

class SerialReaderThread(QThread):
    data_ready = pyqtSignal(str)

    def __init__(self, serial):
        super().__init__()
        self.serial = serial

    def run(self):
        while True:
            if self.serial.is_open:
                try:
                    data = self.serial.readline().decode('utf-8')
                    if data:  # only emit data if something is read
                        self.data_ready.emit(data)
                except Exception as e:
                    print(f"Error while reading from serial port: {e}")
            else:
                print("Serial port is not open...")
                break
