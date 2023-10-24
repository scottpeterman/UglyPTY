from PyQt6.QtWidgets import QHBoxLayout, QFileDialog, QApplication, QMessageBox, QWidget, QComboBox, QVBoxLayout, QPushButton, QLabel, QLineEdit, QProgressBar
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from uglypty.Library.collector_lib import *
from uglypty.Library.util import cryptonomicon
import sqlite3
import datetime
import traceback

class Worker(QThread):
    progress = pyqtSignal(int)
    success = pyqtSignal(str)
    failure = pyqtSignal(str)
    skipped = pyqtSignal(str)

    def __init__(self, max_job_size, query, output_dir, command, devices, device_type, username, password):
        super().__init__()
        self.run_complete = False
        self.max_job_size = max_job_size
        self.query = query
        self.output_dir = output_dir
        self.command = command
        self.devices = devices
        self.device_type = device_type
        self.username = username
        self.password = password
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    def run(self):

        try:
            with ProcessPoolExecutor() as process_executor:
                for i in range(0, len(self.devices), self.max_job_size):
                    job_devices = self.devices[i:i + self.max_job_size]

                    with ThreadPoolExecutor() as thread_executor:
                        for device in job_devices:
                            device['device_type'] = self.device_type
                            device['username'] = self.username
                            device['password'] = self.password
                            device['timestamp'] = self.timestamp
                            device['command'] = self.command

                        job_results = thread_executor.map(lambda device: ssh_to_device(device), job_devices)

                        for idx, result in enumerate(job_results):
                            filename = job_devices[idx]['display_name']
                            # Update progress regardless of job result
                            if not self.run_complete:
                                self.progress.emit(i + self.max_job_size)
                            else:
                                self.progress.emit(100)
                            if result is not None:
                                save_result_to_file(self.output_dir, filename, result)
                                # Emit success or failure signal based on the result
                                print(f"Result: {result.get('status')}")

                                if result['status'] == 'success':
                                    self.success.emit(filename)
                                elif result['status'] == 'skipped':
                                    self.skipped.emit(filename)
                                else:
                                    self.failure.emit(filename)
                            else:
                                self.failure.emit(filename)
            print(f"Run Complete")
        except Exception as e:
            print(f"Error occurred: {e}")
            traceback.print_exc()
        finally:
            QTimer.singleShot(1000, lambda: self.progress.emit(100))

class CollectorForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Netmiko Collector")
        self.success_count = {}
        self.failure_count = {}
        self.skipped_count = {}
        self.setFixedWidth(400)
        # Create widgets
        self.layout = QVBoxLayout()

        self.label_max_jobs = QLabel("Max Job Size:")
        self.edit_max_jobs = QLineEdit()
        self.edit_max_jobs.setText(max_job_size)

        # Create new horizontal layout
        self.yaml_layout = QHBoxLayout()

        # Create and add label
        self.yaml_label = QLabel("YAML File:")
        self.yaml_layout.addWidget(self.yaml_label)

        # Create and add line edit
        self.yaml_lineedit = QLineEdit("./sessions/sessions.yaml")
        self.yaml_layout.addWidget(self.yaml_lineedit)

        # Create and add push button
        def open_file_dialog():
            filename, _ = QFileDialog.getOpenFileName(None, "Open YAML File", "", "YAML Files (*.yaml)")
            if filename:
                self.yaml_lineedit.setText(filename)

        self.yaml_button = QPushButton("Browse...")
        self.yaml_button.clicked.connect(open_file_dialog)
        self.yaml_layout.addWidget(self.yaml_button)

        # Add the new hbox layout to your existing layout
        self.layout.addLayout(self.yaml_layout)

        self.label_query = QLabel("SQL Query:")
        self.edit_query = QLineEdit()
        self.edit_query.setText(query_default)
        self.label_device_type = QLabel("Netmiko Type:")
        self.device_type_combo = QComboBox()
        self.device_type_combo.addItems(["cisco_xe", "cisco_nxos", "cisco_ios","cisco_xr","cloudgenix_ion","fortinet","hp_procurve","hp_comware", "juniper_junos", "junos", "arista_eos", "linux"])

        self.label_output_dir = QLabel("Output Directory:")
        self.edit_output_dir = QLineEdit()
        self.edit_output_dir.setText(str(output_dir))

        self.select_folder_button = QPushButton("Select Folder")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.directory_layout = QHBoxLayout()
        self.directory_layout.addWidget(self.edit_output_dir)
        self.directory_layout.addWidget(self.select_folder_button)

        self.label_command = QLabel("Command to Run:")
        self.edit_command = QLineEdit()
        self.edit_command.setText("show version")

        self.label_user = QLabel("User:")
        self.combo_user = QComboBox()

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.button_start = QPushButton("Start")

        self.label_success = QLabel("Success: 0")
        self.label_failure = QLabel("Failures: 0")
        self.label_skipped = QLabel("Skipped: 0")

        # Add widgets to layout
        self.layout.addWidget(self.label_max_jobs)
        self.layout.addWidget(self.edit_max_jobs)
        self.layout.addWidget(self.label_device_type)
        self.layout.addWidget(self.device_type_combo)
        self.layout.addWidget(self.label_query)
        self.layout.addWidget(self.edit_query)
        self.layout.addWidget(self.label_user)
        self.layout.addWidget(self.combo_user)
        self.layout.addLayout(self.directory_layout)
        self.layout.addWidget(self.label_command)
        self.layout.addWidget(self.edit_command)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.label_success)
        self.layout.addWidget(self.label_failure)
        self.layout.addWidget(self.label_skipped)
        self.layout.addWidget(self.button_start)

        self.setLayout(self.layout)

        self.button_start.clicked.connect(self.start)
        # self.worker.skipped.connect(self.increment_skipped)
        self.load_users()

    def select_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")

        if directory:  # if user didn't pick a directory don't change anything
            self.edit_output_dir.setText(directory)  # sets the text to the selected directory

    def get_creds(self, user_id):
        conn = sqlite3.connect("settings.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM creds WHERE id = ?", (user_id,))
        record = cursor.fetchone()
        encrypted_password = record[1]
        username = record[0]
        conn.close()

        # Decrypt the password
        decrypted_password = cryptonomicon(encrypted_password)

        return username, decrypted_password

    def load_users(self):
        conn = sqlite3.connect("settings.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT id, username FROM creds")
        rows = cursor.fetchall()
        conn.close()

        for row in rows:
            id, username = row
            self.combo_user.addItem(username, id)

    def start(self):
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        # command = self.edit_command.text()
        max_job_size = int(self.edit_max_jobs.text())
        query = self.edit_query.text()
        output_dir = self.edit_output_dir.text()
        command = str(self.edit_command.text()).strip()
        device_type = self.device_type_combo.currentText()
        yaml_file = self.yaml_lineedit.text()  # Get yaml file from lineedit

        devices = fetch_devices(yaml_file, query)
        self.progress_bar.setMaximum(len(devices))
        username, password = self.get_creds(self.combo_user.currentData())
        self.worker = Worker(max_job_size, query, output_dir, command, devices, device_type, username, password)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.success.connect(self.increment_success)
        self.worker.failure.connect(self.increment_failure)
        self.worker.skipped.connect(self.increment_skipped)
        self.worker.finished.connect(self.complete)  # Connect to 'finished' signal
        self.worker.start()

    def complete(self):
        self.progress_bar.setValue(100)

        self.progress_bar.setVisible(False)

        self.notify("Done", "Worker has finished execution.")
        print("Worker has finished execution.")

    def increment_success(self, hostname):
        self.success_count[hostname] = self.success_count.get(hostname, 0) + 1
        total_successes = sum(self.success_count.values())
        self.label_success.setText(f"Successes: {total_successes}")

    def increment_failure(self, hostname):
        self.failure_count[hostname] = self.failure_count.get(hostname, 0) + 1
        total_failures = sum(self.failure_count.values())
        self.label_failure.setText(f"Failures: {total_failures}")

    def increment_skipped(self, hostname):
        self.skipped_count[hostname] = self.skipped_count.get(hostname, 0) + 1
        total_skipped = sum(self.skipped_count.values())
        self.label_skipped.setText(f"Skipped: {total_skipped}")

    def notify(self, message, info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg.exec()

if __name__ == "__main__":
    app = QApplication([])
    import qdarktheme


    qdarktheme.setup_theme("dark")
    window = CollectorForm()
    window.show()
    app.exec()

    '''netmiko device types by value:
    Supported SSH device_type values
    a10
    accedian
    adtran_os
    adva_fsp150f2
    adva_fsp150f3
    alcatel_aos
    alcatel_sros
    allied_telesis_awplus
    apresia_aeos
    arista_eos
    arris_cer
    aruba_os
    aruba_osswitch
    aruba_procurve
    audiocode_66
    audiocode_72
    audiocode_shell
    avaya_ers
    avaya_vsp
    broadcom_icos
    brocade_fastiron
    brocade_fos
    brocade_netiron
    brocade_nos
    brocade_vdx
    brocade_vyos
    calix_b6
    casa_cmts
    cdot_cros
    centec_os
    checkpoint_gaia
    ciena_saos
    cisco_asa
    cisco_ftd
    cisco_ios
    cisco_nxos
    cisco_s200
    cisco_s300
    cisco_tp
    cisco_viptela
    cisco_wlc
    cisco_xe
    cisco_xr
    cloudgenix_ion
    coriant
    dell_dnos9
    dell_force10
    dell_isilon
    dell_os10
    dell_os6
    dell_os9
    dell_powerconnect
    dell_sonic
    dlink_ds
    eltex
    eltex_esr
    endace
    enterasys
    ericsson_ipos
    ericsson_mltn63
    ericsson_mltn66
    extreme
    extreme_ers
    extreme_exos
    extreme_netiron
    extreme_nos
    extreme_slx
    extreme_tierra
    extreme_vdx
    extreme_vsp
    extreme_wing
    f5_linux
    f5_ltm
    f5_tmsh
    flexvnf
    fortinet
    generic
    generic_termserver
    hillstone_stoneos
    hp_comware
    hp_procurve
    huawei
    huawei_olt
    huawei_smartax
    huawei_vrp
    huawei_vrpv8
    ipinfusion_ocnos
    juniper
    juniper_junos
    juniper_screenos
    keymile
    keymile_nos
    linux
    mellanox
    mellanox_mlnxos
    mikrotik_routeros
    mikrotik_switchos
    mrv_lx
    mrv_optiswitch
    netapp_cdot
    netgear_prosafe
    netscaler
    nokia_srl
    nokia_sros
    oneaccess_oneos
    ovs_linux
    paloalto_panos
    pluribus
    quanta_mesh
    rad_etx
    raisecom_roap
    ruckus_fastiron
    ruijie_os
    sixwind_os
    sophos_sfos
    supermicro_smis
    teldat_cit
    tplink_jetstream
    ubiquiti_edge
    ubiquiti_edgerouter
    ubiquiti_edgeswitch
    ubiquiti_unifiswitch
    vyatta_vyos
    vyos
    watchguard_fireware
    yamaha
    zte_zxros
    zyxel_os
    '''