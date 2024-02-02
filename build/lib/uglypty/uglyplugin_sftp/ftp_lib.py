import logging
import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from PyQt6.QtCore import QThread, pyqtSignal

class CustomFTPHandler(FTPHandler):
    def on_connect(self):
        logging.info(f"Client connected: {self.remote_ip}:{self.remote_port}")

    def on_disconnect(self):
        logging.info(f"Client disconnected: {self.remote_ip}:{self.remote_port}")

    # Add more custom event handlers if needed
class FTPQtLogHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        log_entry = self.format(record)
        self.signal.emit(log_entry)
class FTPServerThread(QThread):
    logSignal = pyqtSignal(str)

    def __init__(self, host, port, username, password, directory, parent=None):
        super(FTPServerThread, self).__init__(parent)
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.directory = directory

    def run(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = FTPQtLogHandler(self.logSignal)
        logger.addHandler(handler)

        # Set up the FTP server with the correct FTPHandler
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.username, self.password, self.directory, perm='elradfmw')

        # Use a standard or custom FTPHandler here
        ftp_handler = CustomFTPHandler  # or FTPHandler if you don't have a custom one
        ftp_handler.authorizer = authorizer

        # Create and start the FTP server
        self.server = FTPServer((self.host, self.port), ftp_handler)
        self.server.serve_forever()

    def stop(self):
        self.server.close_all()
