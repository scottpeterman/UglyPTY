from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
import serial
from serial.tools import list_ports

from uglypty.uglyplugin_serial.Library.serialshellreader import SerialReaderThread

class SerialBackend(QObject):
    send_output = pyqtSignal(str)

    def __init__(self, port='COM1', baudrate=9600, databits=8, stopbits=1, parity='N', parent=None):
        super().__init__(parent)
        self.parent = parent

        # Print available serial ports for debugging
        print("Available serial ports:")
        for port_info in list_ports.comports():
            print(f"{port_info.device}: {port_info.description}")
        self.port = port
        self.baudrate = baudrate
        self.databits = databits
        self.stopbits = stopbits
        self.parity = parity
        self.serial = None
        self.reader_thread = None

    @pyqtSlot()
    def connect(self):
        if not self.serial:
            try:
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    bytesize=self.databits,
                    stopbits=self.stopbits,
                    parity=self.parity,
                    timeout=1  # timeout for reading operations
                )
                print(f"Connected to... {self.port}")
            except Exception as e:
                print(e)
                return
            self.reader_thread = SerialReaderThread(self.serial)
            self.reader_thread.data_ready.connect(self.send_output)
            self.reader_thread.start()

    @pyqtSlot()
    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
        if self.reader_thread:
            self.reader_thread.quit()
            self.reader_thread.wait()
        try:
            self.ui.close()
        except Exception as e:
            print(f"{e}")


    @pyqtSlot(str)
    def write_data(self, data):
        if self.serial and self.serial.is_open:
            try:
                self.serial.write(data.encode())
            except Exception as e:
                print(f"Error while writing to serial port: {e}")

    def __del__(self):
        self.disconnect()
