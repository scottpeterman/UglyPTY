from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, \
    QTextEdit, QStyleFactory
import sys
import logging
import tftpy
import threading

class TextEditHandler(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        log_entry = self.format(record)
        self.text_edit.append(log_entry)


class TftpServerApp(QWidget):
    def __init__(self, parent=None):
        super(TftpServerApp, self).__init__()
        self.parent = parent
        self.server = None
        self.setWindowTitle("TFTP Server")

        # Logging Setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("tftpy.TftpServer")
        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # GUI Setup
        self.initUI()

        # Adding TextEditHandler to capture logs in QTextEdit
        self.text_edit_handler = TextEditHandler(self.log_text_edit)
        self.text_edit_handler.setFormatter(log_formatter)
        self.logger.addHandler(self.text_edit_handler)


    def initUI(self):
        layout = QVBoxLayout()

        self.path_edit = QLineEdit(self)
        self.path_edit.setText("./")
        self.path_edit.setPlaceholderText("Enter path to serve files from...")
        layout.addWidget(self.path_edit)

        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_button)

        self.start_button = QPushButton("Start Server", self)
        self.start_button.clicked.connect(self.start_server)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Server", self)
        self.stop_button.clicked.connect(self.stop_server)
        layout.addWidget(self.stop_button)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)

        self.setLayout(layout)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.path_edit.setText(folder_path)

    def start_server(self):
        self.log_text_edit.clear()
        folder_path = self.path_edit.text()
        if folder_path:
            try:
                self.server = tftpy.TftpServer(folder_path)
                server_thread = threading.Thread(target=self.server.listen, args=('0.0.0.0', 69), daemon=True)
                server_thread.start()
                self.log_text_edit.append("Server started.")
            except Exception as e:
                self.log_text_edit.append(f"Failed to start the server: {e}")
        else:
            self.log_text_edit.append("Please specify a valid folder path.")

    def stop_server(self):
        if self.server:
            self.server.stop()  # Assuming TftpServer has a stop method, you might need to implement it
            self.server = None
            self.log_text_edit.append("Server stopped.")
        else:
            self.log_text_edit.append("Server is not running.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    ex = TftpServerApp()
    mainWin = QMainWindow()
    mainWin.setCentralWidget(ex)
    mainWin.setWindowTitle('TFTP Server')
    mainWin.show()
    sys.exit(app.exec())
