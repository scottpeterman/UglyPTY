from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QLineEdit, QLabel, QPushButton, \
    QTableWidget, QTableWidgetItem, QFormLayout, QFileDialog
from ipaddress import ip_network, ip_interface
import csv
import sys


class MyWindow(QWidget):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.setWindowTitle("IP Subnet Calculator")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()
        tab_widget = QTabWidget()

        # IPv4 Tab
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        self.setup_ipv4_tab(tab1, tab1_layout)
        tab_widget.addTab(tab1, "IPv4")

        # IPv6 Tab
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        self.setup_ipv6_tab(tab2, tab2_layout)
        tab_widget.addTab(tab2, "IPv6")

        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def setup_ipv4_tab(self, tab, layout):
        form_layout = self.create_form_layout('ipv4')
        calc_button = QPushButton('Calculate')
        calc_button.clicked.connect(lambda: self.calculate_subnets('ipv4'))
        form_layout.addRow('', calc_button)

        self.summary_text_ipv4 = QLabel('')
        form_layout.addRow('Summary:', self.summary_text_ipv4)

        self.table_ipv4 = self.create_table()
        layout.addLayout(form_layout)
        layout.addWidget(self.table_ipv4)

        export_button = QPushButton('Export to CSV')
        export_button.clicked.connect(lambda: self.export_table_to_csv('ipv4'))
        layout.addWidget(export_button)

        tab.setLayout(layout)

    def setup_ipv6_tab(self, tab, layout):
        form_layout = self.create_form_layout('ipv6')
        calc_button_ipv6 = QPushButton('Calculate IPv6')
        calc_button_ipv6.clicked.connect(lambda: self.calculate_subnets('ipv6'))
        form_layout.addRow('', calc_button_ipv6)

        self.summary_text_ipv6 = QLabel('')
        form_layout.addRow('Summary:', self.summary_text_ipv6)

        self.table_ipv6 = self.create_table()
        layout.addLayout(form_layout)
        layout.addWidget(self.table_ipv6)

        export_button_ipv6 = QPushButton('Export to CSV (IPv6)')
        export_button_ipv6.clicked.connect(lambda: self.export_table_to_csv('ipv6'))
        layout.addWidget(export_button_ipv6)

        tab.setLayout(layout)

    def create_form_layout(self, ip_version):
        form_layout = QFormLayout()
        setattr(self, f'ip_input_{ip_version}', QLineEdit())
        setattr(self, f'prefix_input_{ip_version}', QLineEdit())
        setattr(self, f'subnet_prefix_input_{ip_version}', QLineEdit())
        form_layout.addRow('IP Prefix:', getattr(self, f'ip_input_{ip_version}'))
        form_layout.addRow('Prefix Length:', getattr(self, f'prefix_input_{ip_version}'))
        form_layout.addRow('Subnet Prefix Length:', getattr(self, f'subnet_prefix_input_{ip_version}'))
        return form_layout

    def create_table(self):
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(
            ['Subnet', 'Prefix Length', 'Starting Host IP', 'Ending Host IP', 'Broadcast Address'])
        return table

    def calculate_subnets(self, ip_version):
        # ip_prefix = f'ip_input_{ip_version}'
        ip_prefix = getattr(self, f'ip_input_{ip_version}').text()
        try:
            prefix_length = int(getattr(self, f'prefix_input_{ip_version}').text())
            subnet_prefix_length = int(getattr(self, f'subnet_prefix_input_{ip_version}').text())
            network = ip_network(f"{ip_prefix}/{prefix_length}", strict=False)
        except ValueError as e:
            if ip_version == "ipv4":
                self.summary_text_ipv4.setText(f"Calculation Error: {str(e)}")
            if ip_version == "ipv6":
                self.summary_text_ipv6.setText(f"Calculation Error: {str(e)}")
            return


        subnets = list(network.subnets(new_prefix=subnet_prefix_length))

        summary_text = f"Number of Subnets: {len(subnets)}, Hosts per Subnet: {len(list(subnets[0].hosts()))}"
        summary_label = getattr(self, f'summary_text_{ip_version}')
        summary_label.setText(summary_text)

        table = getattr(self, f'table_{ip_version}')
        table.setRowCount(len(subnets))

        for idx, subnet in enumerate(subnets):
            hosts = list(subnet.hosts())
            table.setItem(idx, 0, QTableWidgetItem(str(subnet.network_address)))
            table.setItem(idx, 1, QTableWidgetItem(str(subnet.prefixlen)))
            table.setItem(idx, 2, QTableWidgetItem(str(hosts[0]) if hosts else 'N/A'))
            table.setItem(idx, 3, QTableWidgetItem(str(hosts[-1]) if hosts else 'N/A'))
            table.setItem(idx, 4, QTableWidgetItem(str(subnet.broadcast_address)))

    def export_table_to_csv(self, ip_version):
        table = getattr(self, f'table_{ip_version}')
        default_filename = f"{ip_version}_subnets.csv"

        filename, _ = QFileDialog.getSaveFileName(self, "Save File", default_filename,
                                                  "CSV Files (*.csv);;All Files (*)")

        if not filename:  # Cancelled or closed dialog
            return

        # Add a .csv extension if not present
        if not filename.endswith('.csv'):
            filename += '.csv'

        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write the header
                headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())]
                writer.writerow(headers)

                # Write the table data
                for row in range(table.rowCount()):
                    row_data = []
                    for column in range(table.columnCount()):
                        item = table.item(row, column)
                        if item is not None:
                            row_data.append(item.text())
                        else:
                            row_data.append('')
                    writer.writerow(row_data)

        except Exception as e:
            summary_label = getattr(self, f'summary_text_{ip_version}')
            summary_label.setText(f"Save Error: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
