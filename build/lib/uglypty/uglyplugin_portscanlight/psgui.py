import re
import sys
from ipaddress import ip_address, ip_network

from uglypty.uglyplugin_portscanlight.PortScannerThread import PortScannerThread
from uglypty.uglyplugin_portscanlight.portscan import PortScan
from uglypty.uglyplugin_portscanlight.pscan_help import help_content
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QPlainTextEdit, QComboBox, QFormLayout,
    QCheckBox, QMenuBar, QMenu, QTextBrowser, QLabel
)
from PyQt6.QtCore import QProcess, Qt, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction
import os

class PortScannerGUI(QWidget):
    output_received = pyqtSignal(str)
    on_scan_complete = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.portScannerThread = None

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
        # Validate the form
        if not self.ip_input.text() or not self.port_input.text() or not self.wait_time_input.text():
            error_label = QLabel('Please fill out all required fields.', self)
            error_label.setStyleSheet('color: red')
            self.layout().addWidget(error_label)
            return

        # Extract user input
        ip_str = self.ip_input.text()
        port_str = self.port_input.text()
        thread_num = int(self.thread_num_input.currentText())
        show_refused = self.show_refused_input.isChecked()
        wait_time = int(self.wait_time_input.text())
        stop_after_count_str = self.stop_after_count_input.text()
        stop_after_count = int(stop_after_count_str) if stop_after_count_str else None

        # Parse IPs and Ports using the read_ip and read_port methods
        try:
            ip_list = self.read_ip(ip_str)
            port_list = self.read_port(port_str)
        except ValueError as ve:
            error_label = QLabel(f'Invalid input: {ve}', self)
            error_label.setStyleSheet('color: red')
            self.layout().addWidget(error_label)
            return

        # Initialize and configure the PortScannerThread
        self.portScannerThread = PortScannerThread(
            ip_list, port_list, thread_num, show_refused, wait_time, stop_after_count
        )

        # Connect signals to slots
        self.portScannerThread.textReady.connect(self.update_output)
        self.portScannerThread.scanComplete.connect(self.on_scan_complete)


        # Disable the "Run Scanner" button and update the status label
        self.run_button.setEnabled(False)
        self.status_label.setText("Status: Scanning...")

        # Start the thread
        self.portScannerThread.start()
    def update_output(self, text):
        self.result_output.appendPlainText(text)

    @pyqtSlot(list)
    def on_scan_complete(self, result):
        self.result_output.appendPlainText("Scan Complete!")
        formatted_result = "\n".join([f"IP: {ip}, Port: {port}" for ip, port in result])
        self.result_output.appendPlainText(formatted_result)

        self.status_label.setText("Status: Finished")
        self.run_button.setEnabled(True)



    def on_process_finished(self):
        self.run_button.setEnabled(True)  # Re-enable run button
        self.status_label.setText('Status: Finished')  # Update status label

    def help_from_portscan(self):
        help =help_content
        return help

    from ipaddress import ip_address, ip_network

    def read_ip(self, ip_str):
        try:
            # Check if it's a single IP address
            ip = ip_address(ip_str)
            return [str(ip)]
        except ValueError:
            pass

        try:
            # Check if it's a network range in CIDR notation
            network = ip_network(ip_str)
            return [str(ip) for ip in network]
        except ValueError:
            pass

        if ip_str.startswith("[") and ip_str.endswith("]"):
            ip_str = ip_str[1:-1]
            elements = [e.strip() for e in ip_str.split(',')]
            master = []
            for each in elements:
                try:
                    sub_list = self.read_ip(each)
                    master.extend(sub_list)
                except ValueError as e:
                    print("{} is not correctly formatted".format(each))
            return master

        raise ValueError('incorrect Match')

    def read_port(self, port_str):
        ports = port_str.split(',')
        port_list = []
        for port in ports:
            if re.match('^\d+$', port):
                port_list.append(int(port))
            elif re.match('^\d+-\d+$', port):
                p_start = int(port.split('-')[0])
                p_end = int(port.split('-')[1])
                p_range = list(range(p_start, p_end + 1))
                port_list.extend(p_range)
            else:
                raise ValueError('incorrect Match')
        return port_list

if __name__ == '__main__':
    app = QApplication([])
    app.setStyle("fusion")
    gui = PortScannerGUI()
    gui.show()
    app.exec()
