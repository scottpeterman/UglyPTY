from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from hnmp import SNMP, SNMPError
from pysnmp.error import PySnmpError


class SNMPQueryThread(QThread):
    finished = pyqtSignal(list)
    errorOccurred = pyqtSignal(str)

    def __init__(self, host, version, community=None, username=None, authproto=None, authkey=None, privproto=None, privkey=None, parent=None):
        super().__init__(parent)

        self.host = host
        self.version = version
        self.community = community
        self.username = username
        self.authproto = authproto
        self.authkey = authkey
        self.privproto = privproto
        self.privkey = privkey

    def run(self):
        try:
            if self.version == 2:
                snmp = SNMP(host=self.host, community=self.community, version=2, timeout=20)
            else:
                snmp = SNMP(
                    host=self.host,
                    version=3,
                    username=self.username,
                    authproto=self.authproto,
                    authkey=self.authkey,
                    privproto=self.privproto,
                    privkey=self.privkey,
                    timeout=20
                )
            interface_table_oid = "1.3.6.1.2.1.2.2.1"
            columns = {
                '2': 'interfaceName',
                '8': 'interfaceStatus'
            }
            print(f"Getting interface table")
            try:
                # interface_table = snmp.table(interface_table_oid)
                interface_table = snmp.table(
                    interface_table_oid,
                    columns=columns,
                    fetch_all_columns=False
                )

                interface_data = []
                for row in interface_table.rows:
                    # Extract the '_row_id' which indicates the interface index
                    row_id = row['_row_id']
                    name = row[2]  # Interface Name
                    status = row[8]  # Operational Status

                    # Convert status to human-readable form
                    status_symbol = self.get_status_symbol(status)
                    status_text = f"{status_symbol} {name}"
                    interface_data.append((row_id, status_text))
                print("done getting interface table")
                # self.finished.emit(interface_data)
                # QTimer.singleShot(0, lambda: self.emit_finished_signal(interface_data))
                self.finished.emit(interface_data)


            except SNMPError as e:
                # self.finished.emit([])

                self.errorOccurred.emit(str(e))
            except PySnmpError as pye:
                message = f'''Error: {pye}\n Verify SNMP Settings\nusername=self.username,
authproto=self.authproto,
authkey=self.authkey,
privproto=self.privproto,
privkey=self.privkey,'''
                self.errorOccurred.emit(message)
            except Exception as e:
                print(f"Unexpected error in thread: {e}")


        except Exception as e:
            self.errorOccurred.emit(str(e))  # Emit the error message

    def emit_finished_signal(self, interface_data):
        print("emitting finished")

    def get_status_symbol(self, status):
        if status == 1:
            return "\U00002705"  # Green check mark
        elif status == 2:
            return "\U0000274C"  # Red X
        else:
            return "\U00002753"  # Yellow question mark

