from PyQt6.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QScreen, QGuiApplication
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QVBoxLayout, QLabel, QTextEdit
import sys
import subprocess

class RunThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')
    stdout_signal = pyqtSignal(str)

    def __init__(self, cmd):
        QThread.__init__(self)
        self.cmd = cmd

    def run(self):
        process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self.signal.emit(process)

        for line in iter(process.stdout.readline, ''):
            self.stdout_signal.emit(line)

        process.stdout.close()
        process.wait()

class crawlerGuiUI(QWidget):

    def __init__(self):
        super(crawlerGuiUI, self).__init__()
        self.initUI()


    def center(self):
        screen = QGuiApplication.primaryScreen()  # Get the primary screen
        screen_geometry = screen.availableGeometry()  # Get available geometry of the screen
        self.setGeometry(
            (screen_geometry.width() - self.width()) // 2,
            (screen_geometry.height() - self.height()) // 2,
            self.width(),
            self.height()
        )

    def initUI(self):
        self.setWindowTitle('CDP Crawler and Mapper')
        self.setGeometry(100, 100, 400, 400)
        self.center()
        vbox = QVBoxLayout()

        self.seed_ip_edit = QLineEdit(self)
        self.seed_ip_edit.setPlaceholderText("Enter seed IP")
        vbox.addWidget(self.seed_ip_edit)

        self.device_id_edit = QLineEdit(self)
        self.device_id_edit.setPlaceholderText("Enter device ID")
        vbox.addWidget(self.device_id_edit)

        self.username_edit = QLineEdit(self)
        self.username_edit.setPlaceholderText("Enter username")
        vbox.addWidget(self.username_edit)

        self.password_edit = QLineEdit(self)
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        vbox.addWidget(self.password_edit)

        self.domain_name = QLineEdit(self)
        self.domain_name.setPlaceholderText("Enter domain name")
        self.domain_name.setText("company.com")
        vbox.addWidget(self.domain_name)

        self.exclude_string = QLineEdit(self)
        self.exclude_string.setPlaceholderText("comma separated string - use for network edges")
        self.exclude_string.setText("SEP,IPPhone")
        vbox.addWidget(self.exclude_string)

        self.layout_algo = QLineEdit(self)
        self.layout_algo.setPlaceholderText("rt for most networks, kk for larger networks")
        self.layout_algo.setText("rt")
        vbox.addWidget(self.layout_algo)

        self.map_name = QLineEdit(self)
        self.map_name.setPlaceholderText("name of .graphml file to save")
        self.map_name.setText("map.graphml")
        vbox.addWidget(self.map_name)

        self.collection_name = QLineEdit(self)
        self.collection_name.setPlaceholderText("collection folder to save parsed cdp/lldp info")
        self.collection_name.setText("")
        vbox.addWidget(self.collection_name)
        self.status_label = QLabel('Status: Idle', self)
        vbox.addWidget(self.status_label)

        btn1 = QPushButton('Run', self)
        btn1.clicked.connect(self.run_main)
        vbox.addWidget(btn1)

        btn2 = QPushButton('Cancel', self)
        btn2.clicked.connect(self.cancel_main)
        vbox.addWidget(btn2)

        self.output_text_edit = QTextEdit(self)
        self.output_text_edit.setReadOnly(True)
        vbox.addWidget(self.output_text_edit)

        self.setLayout(vbox)

    def run_main(self):
        seed_ip = self.seed_ip_edit.text()
        device_id = self.device_id_edit.text()
        username = self.username_edit.text()
        password = self.password_edit.text()
        domain_name = self.domain_name.text()
        exclude_string = self.exclude_string.text()
        layout_algo = self.layout_algo.text()
        map_name = self.map_name.text()
        collection_name = self.collection_name.text()

        cmd = [
            "cmd", "/c", sys.executable,"-u", "crawl.py",
            "--seed_ip", seed_ip,
            "--device_id", device_id,
            "--username", username,
            "--password", password,
            "--domain_name", domain_name,
            "--exclude_string", exclude_string,
            "--layout_algo", layout_algo,
            "--map_name", map_name,
            "--collection_name", collection_name

        ]

        self.status_label.setText("Status: Running")
        self.thread = RunThread(cmd)  # Modify the constructor of RunThread to accept cmd directly
        self.thread.signal.connect(self.set_process)
        self.thread.stdout_signal.connect(self.update_text_edit)
        self.thread.start()

    def set_process(self, process):
        self.process = process

    def update_text_edit(self, text):
        self.output_text_edit.append(text.replace("\n", ""))

    def cancel_main(self):
        self.process.terminate()
        self.status_label.setText("Status: Terminated")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    ex = crawlerGuiUI()
    ex.resize(600, 500)
    ex.show()
    sys.exit(app.exec())
