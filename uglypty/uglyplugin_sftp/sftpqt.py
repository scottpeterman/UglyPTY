from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLineEdit, QLabel, QFormLayout, \
    QComboBox
import time
import socket
import paramiko
import threading
import logging

from uglypty.uglyplugin_sftp.sftp_lib import StubServer, StubSFTPServer

import secrets
import string

def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))
class SFTPServerThread(QThread):
    logSignal = pyqtSignal(str)

    def __init__(self, host, port, keyfile, level):
        super(SFTPServerThread, self).__init__()
        self.host = host
        self.port = port
        self.keyfile = keyfile
        self.level = level
        self.stop_flag = threading.Event()

        paramiko_logger = logging.getLogger("paramiko")
        paramiko_logger.setLevel(getattr(logging, self.level))
        handler = PyQtLogHandler(self.logSignal)
        paramiko_logger.addHandler(handler)

    def run(self):
        # Generate random password
        alphabet = string.ascii_letters + string.digits
        self.random_password = ''.join(secrets.choice(alphabet) for i in range(10))

        # You could add code here to set the password to the Paramiko authentication
        # For example, self.set_password(random_password)

        # Notify through logs
        logging.info(f"Creds: admin/{self.random_password}")
        self.logSignal.emit(f"Creds: admin/{self.random_password}")

        self.start_server()

    def handle_connection(self, conn, addr):
        logging.info(f"New connection from {addr}")
        self.logSignal.emit(f"New connection from {addr}")

        host_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        transport = paramiko.Transport(conn)
        transport.add_server_key(host_key)
        transport.set_subsystem_handler('sftp', paramiko.SFTPServer, StubSFTPServer)
        # random password set in run() for display
        server = StubServer("admin", self.random_password)
        transport.start_server(server=server)

        channel = transport.accept()
        while transport.is_active():
            time.sleep(1)

        logging.info(f"Connection from {addr} closed")
        self.logSignal.emit(f"Connection from {addr} closed")

    def start_server(self):
        paramiko_level = getattr(paramiko.common, self.level)
        paramiko.common.logging.basicConfig(level=paramiko_level)

        logging.info(f"Starting SFTP server on {self.host}:{self.port} with keyfile {self.keyfile}")
        self.logSignal.emit(f"Starting SFTP server on {self.host}:{self.port} with keyfile {self.keyfile}")

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        server_socket.bind((self.host, self.port))
        server_socket.listen(10)

        while not self.stop_flag.is_set():
            conn, addr = server_socket.accept()
            threading.Thread(target=self.handle_connection, args=(conn, addr)).start()

        # Close the socket after loop termination (initiated by stop request)
        server_socket.close()


class PyQtLogHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        log_entry = self.format(record)
        self.signal.emit(log_entry)


class SFTPWidget(QWidget):
    def __init__(self, parent=None):
        super(SFTPWidget, self).__init__()
        self.parent = parent
        self.setWindowTitle("SFTP Server")
        self.logArea = QTextEdit()
        self.logArea.setMinimumWidth(500)
        self.logArea.setReadOnly(True)
        self.startButton = QPushButton('Start Server')
        self.stopButton = QPushButton('Stop Server')
        self.stopButton.setEnabled(False)
        self.stop_flag = threading.Event()

        self.hostInput = QLineEdit('0.0.0.0')
        self.portInput = QLineEdit('2022')
        self.keyfileInput = QLineEdit('./test_rsa.key')
        # self.levelInput = QLineEdit('DEBUG')
        self.levelInput = QComboBox()
        self.levelInput.addItems(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])
        self.levelInput.setCurrentIndex(3)
        layout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.addRow(QLabel('Host:'), self.hostInput)
        formLayout.addRow(QLabel('Port:'), self.portInput)
        formLayout.addRow(QLabel('Keyfile:'), self.keyfileInput)
        formLayout.addRow(QLabel('Log Level:'), self.levelInput)

        layout.addLayout(formLayout)
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.logArea)

        self.setLayout(layout)

        self.startButton.clicked.connect(self.start_server)
        self.stopButton.clicked.connect(self.stop_server)

    def start_server(self):

        self.sftp_thread = SFTPServerThread(self.hostInput.text(), int(self.portInput.text()), self.keyfileInput.text(),
                                            self.levelInput.currentText())
        self.sftp_thread.logSignal.connect(self.update_log)
        self.sftp_thread.start()
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.stop_flag.clear()

    def stop_server(self):
        # Implement stop logic
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.stop_flag.set()
        self.logArea.append("\nServer stopped")

    def update_log(self, log_message):
        self.logArea.append(log_message)

if __name__ == "__main__":
    app = QApplication([])
    window = SFTPWidget()
    window.show()
    app.exec()
