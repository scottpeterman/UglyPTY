from PyQt6.QtCore import QThread, pyqtSignal
from hnmp import SNMPError, SNMP
import csv, datetime, os

class InterfaceMonitor(QThread):
    # utilizationUpdated = pyqtSignal(float, float)
    utilizationUpdated = pyqtSignal(float, float, float, float)
    errorOccurred = pyqtSignal(str)

    # Constants for OIDs
    INBOUND_OID_BASE = "1.3.6.1.2.1.2.2.1.10."
    OUTBOUND_OID_BASE = "1.3.6.1.2.1.2.2.1.16."
    IF_SPEED_OID = "1.3.6.1.2.1.2.2.1.5."
    IF_HIGH_SPEED_OID = "1.3.6.1.2.1.31.1.1.1.15."
    POLL_INTERVAL = 10  # Poll every 10 seconds

    def __init__(self, snmp_details, snmp_index, unit):
        super().__init__()
        self.snmp_details = snmp_details
        self.snmp_index = snmp_index
        self.running = False
        self.last_inbound_value = 0
        self.last_outbound_value = 0
        self.max_data_points = 2000
        self.unit = unit
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.csv_filename = f"data_{timestamp}.csv"
        # self.init_csv_file()
        self.sample_counter = 0  # Initialize the sample counter
        self.writer = None
        # with open(self.csv_filename, 'a', newline='') as csvfile:
        self.fh = open(self.csv_filename, 'a', newline='')
        fieldnames = ['Timestamp', 'Inbound Utilization', 'Outbound Utilization', 'Inbound Throughput',
                      'Outbound Throughput', 'Inbound Octets', 'Outbound Octets']
        self.writer = csv.DictWriter(self.fh, fieldnames=fieldnames)



    def create_snmp_session(self):
        # Create an SNMP session based on the version
        if self.snmp_details['version'] == 2:
            return SNMP(
                host=self.snmp_details['host'],
                community=self.snmp_details['community'],
                version=2
            )
        else:
            return SNMP(
                host=self.snmp_details['host'],
                version=3,
                username=self.snmp_details['username'],
                authproto=self.snmp_details['authproto'],
                authkey=self.snmp_details['authkey'],
                privproto=self.snmp_details['privproto'],
                privkey=self.snmp_details['privkey'],
            )

    # def init_csv_file(self):
    #     # Create and initialize the CSV file with headers
    #     with open(self.csv_filename, 'w', newline='') as csvfile:
    #         fieldnames = ['Timestamp', 'Inbound Utilization', 'Outbound Utilization', 'Inbound Throughput',
    #                       'Outbound Throughput']
    #         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #         writer.writeheader()

    def write_to_csv(self, in_utilization, out_utilization, in_throughput, out_throughput, in_octets, out_octets):

            # Write data
        self.writer.writerow({
            'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Inbound Utilization': in_utilization,
            'Outbound Utilization': out_utilization,
            'Inbound Throughput': in_throughput,
            'Outbound Throughput': out_throughput,
            'Inbound Octets': in_octets,
            'Outbound Octets': out_octets
        })

    def run(self):
        print("InterfaceMonitor run method entered")
        self.running = True
        # Fetch initial values for interface speed and octet counters
        interface_speed = self.fetch_interface_speed()
        if interface_speed is None:
            print("Failed to get interface speed")
            self.running = False
            return

        while self.running:
            if self.running:
                print(f"Polling SNMP index {self.snmp_index}")
                self.sample_counter += 1

                # Fetch current inbound and outbound octets
                current_inbound_value, current_outbound_value = self.fetch_octet_counters()

                # Calculate utilizations using the last values and the current ones
                in_utilization, in_throughput = self.calculate_utilization(current_inbound_value, self.last_inbound_value, interface_speed)
                out_utilization, out_throughput = self.calculate_utilization(current_outbound_value, self.last_outbound_value, interface_speed)

                # Emit the calculated utilization values
                # self.utilizationUpdated.emit(in_utilization, out_utilization)
                if self.sample_counter > 2:
                    self.write_to_csv(in_utilization, out_utilization, in_throughput, out_throughput, current_inbound_value,
                                      current_outbound_value)
                    self.utilizationUpdated.emit(in_utilization, out_utilization, in_throughput, out_throughput)

                # Update last values for the next calculation
                self.last_inbound_value = current_inbound_value
                self.last_outbound_value = current_outbound_value

                self.sleep(self.POLL_INTERVAL)
            else:
                break
    def fetch_interface_speed(self):
        snmp = self.create_snmp_session()
        try:
            interface_speed_mbps = snmp.get(self.IF_HIGH_SPEED_OID + str(self.snmp_index))
            if interface_speed_mbps is not None:
                return interface_speed_mbps * 1e6 if self.unit == 'Mbps' else interface_speed_mbps
            else:
                # Fallback to ifSpeed if ifHighSpeed is not available
                interface_speed_bps = snmp.get(self.IF_SPEED_OID + str(self.snmp_index))
                if interface_speed_bps is not None:
                    return interface_speed_bps
                else:
                    return None
        except SNMPError as e:
            self.errorOccurred.emit(f"Error fetching interface speed: {str(e)}")
            return None

    def fetch_octet_counters(self):
        snmp = self.create_snmp_session()
        try:
            inbound_oid = self.INBOUND_OID_BASE + str(self.snmp_index)
            outbound_oid = self.OUTBOUND_OID_BASE + str(self.snmp_index)
            current_inbound_octets = int(snmp.get(inbound_oid))
            current_outbound_octets = int(snmp.get(outbound_oid))
            return current_inbound_octets, current_outbound_octets
        except SNMPError as e:
            self.errorOccurred.emit(f"Error fetching octet counters: {str(e)}")
            return 0, 0

    # def calculate_utilization(self, current_value, last_value, interface_speed):
    #     diff = current_value - last_value
    #     if diff < 0:  # Counter wrap
    #         diff += 2**32
    #     bits = diff * 8  # Convert octets to bits
    #     utilization = (bits / (interface_speed * self.POLL_INTERVAL)) * 100
    #     print(utilization)
    #     return round(max(0, min(utilization, 100)), 2)  # Ensure 0 <= utilization <= 100 and round to 2 decimal places
    def calculate_utilization(self, current_value, last_value, interface_speed):
        diff = current_value - last_value
        if diff < 0:  # Counter wrap
            diff += 2 ** 32
        bits = diff * 8  # Convert octets to bits

        # Calculate throughput based on the selected unit
        if self.unit == 'bps':
            throughput = bits / (self.POLL_INTERVAL * 1e6)  # Convert to Mbps
        else:  # default to Mbps
            throughput = bits / self.POLL_INTERVAL

        utilization = (throughput / (interface_speed / 1e6)) * 100 if self.unit == 'Mbps' else (bits / (
                    interface_speed * self.POLL_INTERVAL)) * 100
        utilization = round(max(0, min(utilization, 100)), 2)

        return utilization, throughput

    def stop(self):
        self.fh.close()
        self.running = False
