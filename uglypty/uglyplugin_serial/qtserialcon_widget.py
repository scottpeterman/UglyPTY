import sys
import os
import json
from PyQt6.QtCore import QSize, QUrl, QCoreApplication, pyqtSlot
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMainWindow, QDialog, QFormLayout, \
    QComboBox, QLineEdit, QDialogButtonBox, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from serial.tools import list_ports

from uglypty.uglyplugin_serial.Library.serialshell import SerialBackend

class Ui_SerialWidget(QWidget):

    def __init__(self, port='COM3', baudrate=9600, databits=8, stopbits=1, parity='N', parent=None):
        super().__init__(parent)
        self.port = port
        self.baudrate = baudrate
        self.databits = databits
        self.stopbits = stopbits
        self.parity = parity
        self.parent = parent
        self.setupUi(self)

    def setupUi(self, term):
        self.backend = SerialBackend(port=self.port, baudrate=self.baudrate,
                                     databits=self.databits, stopbits=self.stopbits,
                                     parity=self.parity)
        self.backend.ui = self
        self.channel = QWebChannel()
        self.channel.registerObject("backend", self.backend)

        layout = QVBoxLayout()

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.backend.connect)
        layout.addWidget(self.connect_btn)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.backend.disconnect)
        # layout.addWidget(self.disconnect_btn)

        self.view = QWebEngineView()
        self.view.page().setWebChannel(self.channel)
        self.backend.send_output.connect(
            lambda data: self.view.page().runJavaScript(f"window.handle_output({json.dumps(data)})"))

        current_dir = os.path.dirname(os.path.abspath(__file__))

        terminal_html = os.path.join(current_dir, "qtserialcon.html")
        print(f"opening ...{terminal_html} ")
        self.view.load(QUrl.fromLocalFile(terminal_html))

        layout.addWidget(self.view)
        self.setLayout(layout)

    def show_connection_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Connect to Serial Port")

        form = QFormLayout()
        combox = QComboBox()
        for port in list_ports.comports():
            if "Bluetooth" not in str(port.description):
                combox.addItem(port.name)
        form.addRow("Port", combox)

        baudrate = QLineEdit("9600")
        form.addRow("Baud Rate", baudrate)

        databits = QLineEdit("8")
        form.addRow("Data Bits", databits)

        stopbits = QLineEdit("1")
        form.addRow("Stop Bits", stopbits)

        parity = QLineEdit("N")
        form.addRow("Parity", parity)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)

        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(button_box)
        dialog.setLayout(layout)

        result = dialog.exec()
        print(result)
        if result == QDialog.DialogCode.Accepted:
            self.backend.port=combox.currentText()
            self.backend.baudrate=int(baudrate.text())
            self.backend.databits=int(databits.text())
            self.backend.stopbits=int(stopbits.text())
            self.backend.parity=parity.text()
        else:
            self.backend.port = "com3"
            self.backend.baudrate = 9600
            self.backend.databits = 8
            self.backend.stopbits = 1
            self.backend.parity = "N"
        try:
            self.backend.connect()
            self.connect_btn.setEnabled(False)
            self.connect_btn.setVisible(False)
        except Exception as e:
            print(e)
            self.notify("Connection error", f"{e}")

    def notify(self, message, info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg.exec()

class SerialWidgetWrapper(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # This layout will host the actual SerialWidget
        self.layout = QVBoxLayout()

        # Create the actual SerialWidget but don't show or add it yet
        self.serial_widget = Ui_SerialWidget(parent=self)

        # Show the connection dialog; block until user has made a selection
        self.serial_widget.show_connection_dialog()

        # Now add the fully configured SerialWidget to the layout
        self.layout.addWidget(self.serial_widget)

        self.setLayout(self.layout)
        # self.show()


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)

        mainWin = QMainWindow()
        mainWin.resize(800, 400)

        # Use the wrapper instead of directly using Ui_SerialWidget
        wrapper = SerialWidgetWrapper(parent=mainWin)

        mainWin.setCentralWidget(wrapper)
        mainWin.show()
        mainWin.setWindowTitle("PyQt6 - Serial Terminal Widget")

        sys.exit(app.exec())

    except Exception as e:
        print(f"Exception in main: {e}")