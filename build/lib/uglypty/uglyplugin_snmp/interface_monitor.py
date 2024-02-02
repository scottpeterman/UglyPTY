import os
import re
import sys
import time

import numpy
import yaml
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, pyqtSlot
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QRadioButton, QPushButton, QStackedWidget, QLabel,
                             QLineEdit, QFormLayout, QListWidget, QListWidgetItem, QComboBox, QMessageBox, QSplitter,
                             QInputDialog)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from uiUtils import SNMPQueryThread
from snmpmonitor import InterfaceMonitor
class SNMPConfigDialog(QWidget):

    def __init__(self, host_ip, parent=None):
        super().__init__(parent)
        self.host_ip = host_ip  # Store the host IP address
        self.unit = 'Mbps'  # 'Mbps' or 'bps'
        self.inbound_data = []
        self.outbound_data = []
        self.max_data_points = 60
        self.initUI()
        self.isstopping = False

    def initUI(self):
        self.setWindowTitle(f'SNMP Monitoring IP: {self.host_ip}')
        self.setGeometry(100, 100, 970, 768)  # Adjust the size to match the screenshot provided

        mainLayout = QVBoxLayout()

        # Radio buttons and 'List Interfaces' button
        topLayout = QHBoxLayout()
        self.snmpV2Radio = QRadioButton('SNMPv2')
        self.snmpV3Radio = QRadioButton('SNMPv3')
        self.listInterfacesButton = QPushButton('List Interfaces')
        topLayout.addWidget(self.snmpV2Radio)
        topLayout.addWidget(self.snmpV3Radio)
        topLayout.addWidget(self.listInterfacesButton)
        mainLayout.addLayout(topLayout)

        # Stacked widget for different panes
        self.stack = QStackedWidget()

        # SNMPv2 settings pane
        self.v2Widget = QWidget()
        v2Layout = QFormLayout()
        self.communityLineEdit = QLineEdit()
        self.communityLineEdit.setText("")
        v2Layout.addRow('Community:', self.communityLineEdit)
        self.v2Widget.setLayout(v2Layout)
        self.stack.addWidget(self.v2Widget)

        # SNMPv3 settings pane
        self.v3Widget = QWidget()
        v3Layout = QFormLayout()
        self.usernameLineEdit = QLineEdit()
        self.usernameLineEdit.setText("")
        self.authkeyLineEdit = QLineEdit()
        self.authkeyLineEdit.setText("")

        self.authprotoComboBox = QComboBox()
        self.authprotoComboBox.addItems(["MD5", "SHA", "SHA-224", "SHA-256", "SHA-384", "SHA-512"])

        self.privprotoComboBox = QComboBox()
        self.privprotoComboBox.addItems(["DES", "AES128", "AES192", "AES256"])

        self.privkeyLineEdit = QLineEdit()
        self.privkeyLineEdit.setText("")
        v3Layout.addRow('Username:', self.usernameLineEdit)
        v3Layout.addRow('Auth Proto:', self.authprotoComboBox)
        v3Layout.addRow('Auth Key:', self.authkeyLineEdit)
        v3Layout.addRow('Priv Proto:', self.privprotoComboBox)
        v3Layout.addRow('Priv Key:', self.privkeyLineEdit)
        self.v3Widget.setLayout(v3Layout)
        self.stack.addWidget(self.v3Widget)

        mainLayout.addWidget(self.stack)

        # Status label for SNMP query
        self.queryStatusLabel = QLabel("Status: Ready")
        mainLayout.addWidget(self.queryStatusLabel)

        # Monitor button
        self.monitorButton = QPushButton('Monitor')
        self.monitorButton.setEnabled(False)
        self.monitorButton.clicked.connect(self.onMonitorClick)  # Connect to a method to handle monitoring
        mainLayout.addWidget(self.monitorButton)

        # Interface listing and matplotlib graph pane with QSplitter
        self.interfaceWidget = QWidget()
        splitter = QSplitter(Qt.Orientation.Horizontal, self.interfaceWidget)

        # Interface list on the left
        self.interfaceList = QListWidget()
        self.listInterfacesButton.clicked.connect(self.onListInterfacesClick)  # Connect to a method to list interfaces
        splitter.addWidget(self.interfaceList)

        # Matplotlib graph on the right
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.figure = self.canvas.figure
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.plot.set_title(f"Network Throughput ({self.unit})")
        self.plot.set_xlabel("Time (Seconds)")
        self.plot.set_ylabel(f"Throughput ({self.unit})")
        self.plot.grid(True)
        splitter.addWidget(self.canvas)

        # Set the initial sizes for the splitter panels
        splitter.setSizes([370, 600])

        # Add the splitter to the interface widget
        interfaceLayout = QVBoxLayout()
        interfaceLayout.addWidget(splitter)
        self.interfaceWidget.setLayout(interfaceLayout)
        self.stack.addWidget(self.interfaceWidget)

        # Set default view and connect signals
        self.snmpV2Radio.setChecked(True)
        self.stack.setCurrentIndex(0)
        self.snmpV2Radio.toggled.connect(lambda: self.stack.setCurrentIndex(0))
        self.snmpV3Radio.toggled.connect(lambda: self.stack.setCurrentIndex(1))

        # Set the layout for the main widget
        self.setLayout(mainLayout)
        self.loadSettings()


    def loadSettings(self):
        if os.path.exists('snmp.yaml'):
            try:
                with open('snmp.yaml', 'r') as file:
                    settings = yaml.safe_load(file)

                # Set form fields based on loaded settings
                if 'community' in settings:
                    self.communityLineEdit.setText(settings['community'])
                if 'username' in settings:
                    self.usernameLineEdit.setText(settings['username'])
                if 'authproto' in settings:
                    index = self.authprotoComboBox.findText(settings['authproto'], Qt.MatchFlag.MatchFixedString)
                    if index >= 0:
                        self.authprotoComboBox.setCurrentIndex(index)
                if 'authkey' in settings:
                    self.authkeyLineEdit.setText(settings.get('authkey','public').strip())
                if 'privproto' in settings:
                    index = self.privprotoComboBox.findText(settings['privproto'], Qt.MatchFlag.MatchFixedString)
                    if index >= 0:
                        self.privprotoComboBox.setCurrentIndex(index)
                if 'privkey' in settings:
                    self.privkeyLineEdit.setText(settings.get('privkey','public').strip())
            except Exception as e:
                self.notify(e)
    def onMonitorClick(self):
        self.startMonitoring()


    def onVersionToggle(self):
        if self.snmpV2Radio.isChecked():
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)

    def notify(self, message):
        self.listInterfacesButton.setEnabled(True)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg.exec()
    def onListInterfacesClick(self):

        self.interfaceList.clear()
        self.listInterfacesButton.setEnabled(False)
        self.queryStatusLabel.setText("Status: Retrieving Interface list...")
        try:
            if self.snmpV2Radio.isChecked():
                self.snmpQueryThread = SNMPQueryThread(
                    self.host_ip,
                    version=2,
                    community=self.communityLineEdit.text(),
                    parent=self
                )
            else:
                self.snmpQueryThread = SNMPQueryThread(
                    self.host_ip,
                    version=3,
                    username=str(self.usernameLineEdit.text()),
                    authproto=str(self.authprotoComboBox.currentText()).lower(),
                    authkey=self.authkeyLineEdit.text(),
                    privproto=str(self.privprotoComboBox.currentText()).lower(),
                    privkey=self.privkeyLineEdit.text(),
                    parent=self
                )
        except Exception as e:
            print(f"thread failure: {e}")
            return

        self.snmpQueryThread.errorOccurred.connect(self.notify)  # Connect the error signal to the notify slot
        self.snmpQueryThread.finished.connect(self.onSNMPQueryFinished)
        self.snmpQueryThread.start()

    @pyqtSlot(list)
    def onSNMPQueryFinished(self, interface_data):
        self.listInterfacesButton.setEnabled(True)
        self.queryStatusLabel.setText("Status: Ready")
        self.monitorButton.setEnabled(True)

        # Update the interface list with status symbols
        for index, status_text in interface_data:
            item_text = f"{status_text}"
            item = QListWidgetItem(item_text)
            item.snmpIndex = int(index)
            self.interfaceList.addItem(item)
        self.stack.setCurrentIndex(2)

    def startMonitoring(self):
        self.queryStatusLabel.setText("Starting Poller ... ~30 sec delay")
        selected_item = self.interfaceList.currentItem()
        if selected_item:
            snmp_index = getattr(selected_item, 'snmpIndex', None)
            if snmp_index is not None:
                # Stop and clean up any existing monitoring thread
                if self.isstopping:
                    print(f"Process still stopping")
                    return
                try:
                    if hasattr(self, 'interfaceMonitor') and self.interfaceMonitor.isRunning():
                        self.interfaceMonitor.stop()  # Stop the thread
                        self.interfaceMonitor.wait()  # Wait for the thread to finish
                except Exception as e:
                    print(e)
                    print("still cleaning up?")
                    if self.isstopping:
                        return
                # Create a new monitoring thread
                self.interfaceMonitor = InterfaceMonitor(self.getSNMPDetails(), snmp_index, self.unit)
                self.interfaceMonitor.utilizationUpdated.connect(self.displayUtilization)
                self.interfaceMonitor.finished.connect(
                    self.interfaceMonitor.deleteLater)  # Ensure cleanup after thread is finished
                self.interfaceMonitor.start()
                self.monitorButton.setText("Stop Monitoring")  # Update button text to reflect action
                self.monitorButton.clicked.disconnect()  # Disconnect the old slot
                self.monitorButton.clicked.connect(self.stopMonitoring)  # Connect to the stopMonitoring method

    def getSNMPDetails(self):
        # This method constructs a dictionary of SNMP details
        # based on the user input from the GUI.
        snmp_details = {
            'host': self.host_ip,
            'port': 161,  # Default SNMP port
            'timeout': 30,  # SNMP timeout (can be adjusted)
        }

        if self.snmpV2Radio.isChecked():
            # SNMPv2 details
            snmp_details.update({
                'version': 2,
                'community': self.communityLineEdit.text(),
            })
        else:
            # SNMPv3 details
            snmp_details.update({
                'version': 3,
                'username': self.usernameLineEdit.text(),
                'authproto': self.authprotoComboBox.currentText().lower(),
                'authkey': self.authkeyLineEdit.text(),
                'privproto': self.privprotoComboBox.currentText().lower(),
                'privkey': self.privkeyLineEdit.text(),
            })

        return snmp_details


    def init_plot(self):
        # Initialize the Matplotlib plot
        self.figure = Figure()  # Create a Figure for plotting
        self.canvas = FigureCanvas(self.figure)  # Create a canvas for the Figure
        self.plot = self.figure.add_subplot(1, 1, 1)  # Add a subplot to the figure

        # self.plot = self.figure.add_subplot(111)
        self.plot.set_title("Network Throughput (Mbps)")
        self.plot.set_xlabel("Time (Seconds)")
        self.plot.set_ylabel("Throughput (Mbps)")
        self.plot.grid(True)
        interfaceLayout = QHBoxLayout(self.interfaceWidget)
        interfaceLayout.addWidget(self.interfaceList)
        interfaceLayout.addWidget(self.canvas)

    def displayUtilization(self, in_utilization, out_utilization, in_throughput, out_throughput):
        if self.unit == 'Mbps':
            # Convert bps to Mbps by dividing by 1e6
            in_throughput_display = in_throughput / 1e6
            out_throughput_display = out_throughput / 1e6
            throughput_unit = "Mbps"
        else:  # Assume bps if not Mbps
            in_throughput_display = in_throughput
            out_throughput_display = out_throughput
            throughput_unit = "bps"

            # Append the latest throughput data to the lists
        self.inbound_data.append(in_throughput_display)
        self.outbound_data.append(out_throughput_display)

        # Limit the size of the lists to the number of data points you want to display
        self.inbound_data = self.inbound_data[-self.max_data_points:]
        self.outbound_data = self.outbound_data[-self.max_data_points:]

        # Update the graph with the new data
        self.update_graph()

        # Print the latest throughput values

        print(f"Inbound Throughput: {in_throughput_display:.2f} {throughput_unit}")  # Displayed with 2 decimal places
        print(f"Outbound Throughput: {out_throughput_display:.2f} {throughput_unit}")  # Displayed with 2 decimal places

    import numpy as np  # Make sure to import NumPy

    def update_graph(self):
        self.queryStatusLabel.setText("Running ... ~10 sec samples")

        # Clear the existing plot
        self.plot.clear()
        # Get the selected item's text
        selected_interface = self.interfaceList.currentItem()
        if selected_interface is not None:
            interface_name = selected_interface.text()
        else:
            interface_name = "No interface selected"
        interface_name = re.sub(r'[^\w\s/.-]', '', interface_name)
        # Format the title with IP and Interface name
        title = f"IP: {self.host_ip} \n{interface_name} (Mbps)"
        self.plot.set_title(title)
        # Assuming self.inbound_data and self.outbound_data are lists of your data points

        # Calculate the max value for setting y-ticks range
        max_value = max(max(self.inbound_data), max(self.outbound_data))
        min_value = min(min(self.inbound_data), min(self.outbound_data))

        # Set the step value for y-ticks depending on your max_value
        step_value = max_value / 10  # This will create 10 y-ticks up to the maximum value

        # Set the y-ticks with a range from min to max value with the defined step
        y_ticks = numpy.arange(0, max_value + step_value, step_value)
        self.plot.set_yticks(y_ticks)

        # Optionally, if you want minor ticks at a finer resolution
        minor_step = step_value / 5  # This will place minor ticks at every fifth of the step value
        minor_y_ticks = numpy.arange(0, max_value + minor_step, minor_step)
        self.plot.set_yticks(minor_y_ticks, minor=True)

        # Enable grid on both major and minor ticks and set properties
        self.plot.grid(True, which='major', linestyle='-', linewidth=0.5)
        self.plot.grid(True, which='minor', linestyle=':', linewidth=0.5, alpha=0.7)

        # Plot the inbound and outbound data
        self.plot.plot(self.inbound_data, label='Inbound', color='blue')
        self.plot.plot(self.outbound_data, label='Outbound', color='orange')

        # Update the labels and legend
        self.plot.set_xlabel('Time')
        self.plot.set_ylabel('Throughput (Mbps)')
        self.plot.legend()

        # Refresh the canvas to show the updated plot
        self.canvas.draw()

    def stopMonitoring(self):
        try:
            # Attempt to check if the thread exists and is running
            if hasattr(self, 'interfaceMonitor') and self.interfaceMonitor and self.interfaceMonitor.isRunning():
                self.interfaceMonitor.stop()
                self.interfaceMonitor.wait()
        except Exception as e:
            print(f"Error stopping the monitoring thread: {e}")
        finally:
            # Clean up
            if hasattr(self, 'interfaceMonitor'):
                self.interfaceMonitor.deleteLater()
                self.interfaceMonitor = None

            # Reset the UI
            self.isstopping = False
            self.monitorButton.setText("Start Monitoring")
            self.monitorButton.setEnabled(True)
            self.queryStatusLabel.setText("Status: Ready")
            self.monitorButton.clicked.disconnect()
            self.monitorButton.clicked.connect(self.startMonitoring)


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Do you want to save SNMP settings?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.saveSettings()
            event.accept()  # Proceed with the window close
        else:
            event.accept()

    def saveSettings(self):
        settings = {
            # 'snmp_version': 2 if self.snmpV2Radio.isChecked() else 3,
            'community': self.communityLineEdit.text(),
            'username': self.usernameLineEdit.text(),
            'authproto': self.authprotoComboBox.currentText(),
            'authkey': self.authkeyLineEdit.text(),
            'privproto': self.privprotoComboBox.currentText(),
            'privkey': self.privkeyLineEdit.text()
        }

        with open('snmp.yaml', 'w') as file:
            yaml.dump(settings, file)

        print("Settings saved to snmp.yaml")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("fusion")

    # Check if an IP address is provided as a command line argument
    if len(sys.argv) > 1:
        host_ip = sys.argv[1]  # Use the provided IP address
    else:
        # Create an input dialog for IP address
        text, ok = QInputDialog.getText(None, "Input Dialog", "Enter the IP address for SNMP monitoring:")
        if ok and text:
            host_ip = text  # Use the entered IP address
        else:
            sys.exit(0)  # Exit if no input is provided

    # Create and show the SNMPConfigDialog
    ex = SNMPConfigDialog(host_ip)
    ex.show()
    sys.exit(app.exec())

