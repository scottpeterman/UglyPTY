import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QPlainTextEdit, QComboBox, QFormLayout,
    QCheckBox, QMenuBar, QMenu, QTextBrowser, QLabel
)
from PyQt6.QtCore import QProcess, Qt, pyqtSignal
from PyQt6.QtGui import QAction
import os
class PortScannerGUI(QWidget):
    output_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setMinimumWidth(500)
        layout = QVBoxLayout()
        self.setWindowTitle("TCP Port Scanner Lite")
        menu_bar = QMenuBar()
        help_menu = QMenu('Help', self)
        portscanner_action = QAction('PortScanner', self)
        about_action = QAction('About', self)

        portscanner_action.triggered.connect(self.show_portscanner_info)
        help_menu.addAction(portscanner_action)
        help_menu.addAction(about_action)
        menu_bar.addMenu(help_menu)

        layout.addWidget(menu_bar)  # Add the menu bar to the layout

        form_layout = QFormLayout()

        self.ip_input = QLineEdit()
        self.port_input = QLineEdit()
        self.thread_num_input = QComboBox()
        self.show_refused_input = QCheckBox()
        self.wait_time_input = QLineEdit()
        self.stop_after_count_input = QLineEdit()

        self.thread_num_input.addItems([str(i) for i in range(1, 21)])
        self.thread_num_input.setCurrentIndex(19)
        # Default values and placeholders
        self.ip_input.setPlaceholderText('192.168.1.0/24')
        self.port_input.setPlaceholderText('22,23,80,443,80-200')
        self.thread_num_input.setCurrentText('500')
        self.wait_time_input.setText('1')

        # Tooltips
        self.ip_input.setToolTip('IP Range e.g., 192.168.1.0/24')
        self.port_input.setToolTip('Port Range e.g., 22-100,5000')
        self.thread_num_input.setToolTip('Number of threads (1-20)')
        self.show_refused_input.setToolTip('Show refused connections')
        self.wait_time_input.setToolTip('Wait time for response (seconds)')
        self.stop_after_count_input.setToolTip('Stop scan after x open ports found')


        form_layout.addRow('IP:', self.ip_input)
        form_layout.addRow('Port:', self.port_input)
        form_layout.addRow('Thread Num:', self.thread_num_input)
        form_layout.addRow('Show Refused:', self.show_refused_input)
        form_layout.addRow('Wait Time:', self.wait_time_input)
        form_layout.addRow('Stop After:', self.stop_after_count_input)

        self.result_output = QPlainTextEdit()
        self.run_button = QPushButton('Run Scanner')
        self.run_button.clicked.connect(self.run_scanner)

        self.status_label = QLabel('Status: Ready', self)  # New status label

        layout.addLayout(form_layout)
        layout.addWidget(self.run_button)
        layout.addWidget(self.status_label)  # Add the status label to the layout
        layout.addWidget(self.result_output)

        self.setLayout(layout)
        self.output_received.connect(self.update_output)  # Connect the signal to the slot

    def show_portscanner_info(self):
        self.info_browser = QTextBrowser()
        self.info_browser.setText(self.help_from_portscan())
        self.info_browser.setMinimumWidth(500)
        self.info_browser.setMinimumHeight(400)
        self.info_browser.setOpenExternalLinks(True)
        self.info_browser.show()

    def run_scanner(self):
        # Form validation
        if not self.ip_input.text() or not self.port_input.text() or not self.wait_time_input.text():
            error_label = QLabel('Please fill out all required fields.', self)
            error_label.setStyleSheet('color: red')
            self.layout().addWidget(error_label)
            return

        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)

        args = [
            self.ip_input.text(),
            f"-p{self.port_input.text().replace(' ', '')}",  # Remove any spaces
            f"-t{self.thread_num_input.currentText()}",
            f"-w{self.wait_time_input.text()}"
        ]
        if self.show_refused_input.isChecked():
            args.append("-e")
        if self.stop_after_count_input.text():
            args.append(f"-s{self.stop_after_count_input.text()}")
        self.run_button.setEnabled(False)  # Disable run button
        self.status_label.setText('Status: Scanning...')  # Update status label
        self.process.finished.connect(self.on_process_finished)  # Connect to the finished signal of the process
        # script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'portscan.py')
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uglyplugin_portscanlight', 'portscan.py'))
        print(f"Running python file: {script_path}")
        self.process.start(sys.executable, [script_path] + args)

    def on_process_finished(self):
        self.run_button.setEnabled(True)  # Re-enable run button
        self.status_label.setText('Status: Finished')  # Update status label

    def handle_output(self):
        text = self.process.readAllStandardOutput().data().decode()
        print(text)
        self.output_received.emit(text)  # Emit the custom signal with the text as an argument

    def update_output(self, text):
        self.result_output.appendPlainText(text)  # Update the QPlainTextEdit with the text

    def help_from_portscan(self):
        help = '''<p>Usage: <code>portscan [192.168.1.0/24] [-p 22,80-200 [-t 100 [-w 1 [-e]]]]</code></p>

<pre>
$ portscan -w 0.2
No IP string found, using local address
Local IP found to be 192.168.1.175, scanning entire block
Threads will wait for ping response for 0.2 seconds
192.168.1.1:80 OPEN
192.168.1.1:443 OPEN
192.168.1.167:443 OPEN
192.168.1.167:80 OPEN
Pinged 1024 ports
</pre>

<p>
By default the command checks for your <em>Local Area Network</em> IP first, and then initiate a block wise search. specify IP if you want to search any other IP blocks. <em>Note: This is not available before 0.2.1, please update or specify IP if you're using 0.2.0 and older</em>
</p>

<p>
Use <code>-w [float]</code> to change timeout settings from default of <code>3</code> seconds: for LAN, this can be as low as <code>0.1</code>. <code>1</code> is usually good enough for continental level connection.
</p>

<p>
To show more ports that have denied/refused connection, use <code>-e</code>, this will show you all ports that are not timed out.
</p>

<pre>
$ portscan 174.109.64.0/24 -w 0.5 -e
Threads will wait for ping response for 0.5 seconds
174.109.64.3:443 ERRNO 61, Connection refused
174.109.64.3:23 ERRNO 61, Connection refused
174.109.64.3:80 ERRNO 61, Connection refused
174.109.64.3:22 ERRNO 61, Connection refused
174.109.64.88:80 ERRNO 61, Connection refused
174.109.64.88:23 ERRNO 61, Connection refused
174.109.64.88:443 ERRNO 61, Connection refused
174.109.64.88:22 ERRNO 61, Connection refused
174.109.64.125:443 OPEN
Pinged 1024 ports
</pre>

<h3>Arguments</h3>

<p>
<code>ip</code>: default and optional <em>(since 0.2.1, required before 0.2.1)</em> argument, can parse single IP, list of IP, IP blocks:
</p>

<pre>
192.168.1.0 # single IP
192.168.1.0/24 # A 24 block, from 192.168.1.0 to 192.168.1.255
[192.168.1.0/24,8.8.8.8] # The aforementioned 24 block and 8.8.8.8.
</pre>

<p>Options:</p>

<p>
<code>-p, --port</code>: port range, default <code>22,23,80</code>, use <code>,</code> as a delimiter without space, support port range (e.g. <code>22-100,5000</code>).<br>
<code>-t, --threadnum</code>: thread numbers, default 500, as of now, thread number have a hard cap of 2048. More thread will increase performance on large scale scans.<br>
<code>-e, --show_refused</code>: show connection errors other than timeouts, e.g. connection refused, permission denied with errno number as they happen.<br>
<code>-w, --wait</code>: Wait time for socket to respond. If scanning LAN or relatively fast internet connection, this can be set to <code>1</code> or even <code>0.1</code> for faster (local) scanning, but this runs a risk of missing the open ports. Default to <code>3</code> seconds<br>
<code>-s, --stop_after</code>: Number of open ports to be discovered after which scan would be gracefully stopped. Default is None for not stopping. Note that it will continue to finish what's left in the queue, so the number of open ports returned might be greater than the value passed in.
</p>

<h3>Python API</h3>

<p>
One can also use this portscan inside existing python scripts.
</p>

<p>
Consider following example for finding out adb port for Android device in LAN with static IP:
</p>

<pre>
from portscan import PortScan
ip = '192.168.1.42'
port_range = '5555,37000-44000'
scanner = PortScan(ip, port_range, thread_num=500, show_refused=False, wait_time=1, stop_after_count=True)
open_port_discovered = scanner.run()  # &lt;----- actual scan
# run returns a list of (ip, open_port) tuples
adb_port = int(open_port_discovered[0][1])

# Usecase specific part
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb
device1 = AdbDeviceTcp(ip, adb_port, default_transport_timeout_s=9)
device1.connect(rsa_keys=[python_rsa_signer], auth_timeout_s=0.1)  # adb connect
# shell exec
notifications_dump = device1.shell('dumpsys notification').encode().decode('ascii','ignore')
device1.close()

print(notifications_dump)
</pre>

<h3>Acknowledgement</h3>
<a href="https://github.com/Aperocky/PortScan">Aperocky/PortScan</a>
'''
        return help


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("fusion")
    gui = PortScannerGUI()
    gui.show()
    app.exec()
