import socket
import time

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLineEdit, QLabel, QFormLayout, \
    QComboBox, QHBoxLayout, QRadioButton, QGroupBox
import threading
import logging
import paramiko

# Assuming ftp_lib is in the same directory
from ftp_lib import FTPServerThread

from sftp_lib import StubServer, StubSFTPServer

import secrets
import string

def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))


class SFTPServerThread(QThread):
    logSignal = pyqtSignal(str)

    def __init__(self, host, port, keyfile, level):
        super().__init__()
        self.host = host
        self.port = port
        self.keyfile = keyfile
        self.level = level
        self.stop_flag = threading.Event()
        self.configure_logging()

    def configure_logging(self):
        paramiko_logger = logging.getLogger("paramiko")
        paramiko_logger.setLevel(getattr(logging, self.level))
        paramiko_logger.addHandler(PyQtLogHandler(self.logSignal))

    def run(self):
        self.random_password = self.generate_random_password()
        logging.info(f"Creds: admin/{self.random_password}")
        self.logSignal.emit(f"Creds: admin/{self.random_password}")
        self.start_server()

    @staticmethod
    def generate_random_password(length=10):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def start_server(self):
        paramiko_level = getattr(paramiko.common, self.level)
        paramiko.common.logging.basicConfig(level=paramiko_level)

        logging.info(f"Starting SFTP server on {self.host}:{self.port} with keyfile {self.keyfile}")
        self.logSignal.emit(f"Starting SFTP server on {self.host}:{self.port} with keyfile {self.keyfile}")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(10)

            while not self.stop_flag.is_set():
                conn, addr = server_socket.accept()
                threading.Thread(target=self.handle_connection, args=(conn, addr)).start()

    def handle_connection(self, conn, addr):
        logging.info(f"New connection from {addr}")
        self.logSignal.emit(f"New connection from {addr}")

        host_key = paramiko.RSAKey.from_private_key_file(self.keyfile)
        transport = paramiko.Transport(conn)
        transport.add_server_key(host_key)
        transport.set_subsystem_handler('sftp', paramiko.SFTPServer, StubSFTPServer)

        server = StubServer("admin", self.random_password)
        transport.start_server(server=server)

        channel = transport.accept()
        while transport.is_active():
            time.sleep(1)

        logging.info(f"Connection from {addr} closed")
        self.logSignal.emit(f"Connection from {addr} closed")

class PyQtLogHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        log_entry = self.format(record)
        self.signal.emit(log_entry)

class SFTPWidget(QWidget):
    def __init__(self, parent=None):
        super(SFTPWidget, self).__init__(parent)
        self.setWindowTitle("SFTP/FTP Server")
        self.stop_flag = threading.Event()
        # Initialize UI components
        self.logArea = QTextEdit()
        self.logArea.setMinimumWidth(500)
        self.logArea.setReadOnly(True)

        self.startButton = QPushButton('Start Server')
        self.startButton.setStyleSheet("background-color: #006400; color: white;")

        self.stopButton = QPushButton('Stop Server')
        self.stopButton.setStyleSheet("background-color: #8B0000; color: white;")
        self.stopButton.setEnabled(False)

        self.hostInput = QLineEdit('0.0.0.0')
        self.portInput = QLineEdit('2022')
        self.keyfileInput = QLineEdit('./test_rsa.key')

        self.levelInput = QComboBox()
        self.levelInput.addItems(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])
        self.levelInput.setStyleSheet("background-color: #8B6508; color: white;")
        self.levelInput.setCurrentIndex(3)

        # Protocol Selection Group
        self.protocolGroup = QGroupBox("Protocol Selection")
        self.sftpRadio = QRadioButton("SFTP")
        self.ftpRadio = QRadioButton("FTP")
        self.sftpRadio.setChecked(True)

        protocolLayout = QHBoxLayout()
        protocolLayout.addWidget(self.sftpRadio)
        protocolLayout.addWidget(self.ftpRadio)
        self.protocolGroup.setLayout(protocolLayout)

        # Layout Configuration
        formLayout = QFormLayout()
        formLayout.addRow(QLabel('Listening IP:'), self.hostInput)
        formLayout.addRow(QLabel('Port:'), self.portInput)
        formLayout.addRow(QLabel('Keyfile:'), self.keyfileInput)
        formLayout.addRow(QLabel('Log Level:'), self.levelInput)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(self.protocolGroup)
        mainLayout.addWidget(self.startButton)
        mainLayout.addWidget(self.stopButton)
        mainLayout.addWidget(self.logArea)
        self.setLayout(mainLayout)

        # Signal Connections
        self.startButton.clicked.connect(self.start_server)
        self.stopButton.clicked.connect(self.stop_server)

    def start_server(self):
        if self.sftpRadio.isChecked():
            # Start SFTP server
            self.sftp_thread = SFTPServerThread(self.hostInput.text(), int(self.portInput.text()), self.keyfileInput.text(),
                                                self.levelInput.currentText())
            self.sftp_thread.logSignal.connect(self.update_log)
            self.sftp_thread.start()
        elif self.ftpRadio.isChecked():
            # Start FTP server
            # You need to decide how to handle the username and password for FTP
            username = "admin"  # Example, replace with actual logic
            password = "password"  # Example, replace with actual logic
            directory = "./"  # Example, replace with actual logic
            random_password = generate_random_password()
            logging.info(f"Creds: admin/{random_password}")
            self.logArea.append(f"\nCreds: admin/{random_password}\n Serving from ./ folder")
            self.ftp_thread = FTPServerThread(self.hostInput.text(), int(self.portInput.text()), username, random_password, directory)
            self.ftp_thread.logSignal.connect(self.update_log)

            self.ftp_thread.start()

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.stop_flag.clear()

    def stop_server(self):
        # Stop the appropriate server
        if self.sftpRadio.isChecked() and hasattr(self, 'sftp_thread'):
            # Signal SFTP server to stop
            self.sftp_thread.stop_flag.set()
        elif self.ftpRadio.isChecked() and hasattr(self, 'ftp_thread'):
            # Signal FTP server to stop
            self.ftp_thread.stop()

        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.logArea.append("\nServer stopped")

    def update_log(self, log_message):
        self.logArea.append(log_message)

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("fusion")
    window = SFTPWidget()
    window.show()
    app.exec()
