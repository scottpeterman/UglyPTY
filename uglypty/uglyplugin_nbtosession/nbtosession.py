import json

from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QProgressBar, QLabel, \
    QFileDialog
import pynetbox
import yaml
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str)
    save_file_signal = pyqtSignal(object)

    def __init__(self, token, url):
        QThread.__init__(self)
        self.token = token
        self.url = url

    def run(self):
        try:
            self.status_signal.emit("Status: Connecting to Netbox")
            netbox = pynetbox.api(self.url, token=self.token)
            netbox.http_session.verify = False  # This is insecure; use with caution

            self.status_signal.emit("Status: Downloading Data")
            uglypty_list = []

            # First loop to count total sites
            site_list = []
            sites = netbox.dcim.sites.all()
            for temp_site in sites:
                print(f"Site Preloading: {temp_site.name}")
                site_list.append(temp_site)
            total_sites = len(site_list)

            # Reset progress bar
            counter = 0

            # Second loop to actually get the data
            for site in site_list:
                folder_dict = {}
                folder_dict['folder_name'] = site.slug
                folder_dict['sessions'] = []
                devices = netbox.dcim.devices.filter(site_id=site.id)

                for device in devices:
                    session = {}
                    try:
                        session['DeviceType'] = device.device_role.name if device.device_role else 'Unknown'
                        session['Model'] = device.device_type.model
                        session['SerialNumber'] = device.serial
                        session['SoftwareVersion'] = 'Unknown'  # Replace with actual data if available
                        session[
                            'Vendor'] = device.device_type.manufacturer.name if device.device_type.manufacturer else 'Unknown'
                        session['credsid'] = '1'
                        session['display_name'] = device.name
                        session['host'] = str(device.primary_ip4.address).split("/")[0] if device.primary_ip4 else 'Unknown'
                        session['port'] = '22'

                        folder_dict['sessions'].append(session)
                        print(f"Processed: {device.name}")
                    except Exception as e:
                        print(f"Error processing device: {device.name}")
                        print(e)

                uglypty_list.append(folder_dict)
                counter += 1
                print(f"Site Number: {counter} of {total_sites}")

                # Update the progress bar
                self.progress_signal.emit((counter * 100) // total_sites)
            # save successfull settings
            settings = {
                "token": self.token,
                "url": self.url
            }
            try:
                with open("netbox_settings.json", "w") as f:
                    json.dump(settings, f)
            except Exception as e:
                print(f"failed to save netbox settings! {e}")
            # Save the YAML file
            # self.status_signal.emit("Status: Saving YAML File")
            # with open("netbox_sessions.yaml", "w") as f:
            #     yaml.dump(uglypty_list, f, default_flow_style=False)
            self.save_file_signal.emit(uglypty_list)


            self.status_signal.emit("Download Complete. Saved to 'netbox_sessions.yaml'")
            self.progress_signal.emit(100)

        except Exception as e:
            print("An error occurred:", e)
            self.status_signal.emit("Status: An error occurred")

def create_default_settings():
    default_settings = {
        "token": "",
        "url": "http://netbox.yourcompany.com"
    }
    with open("netbox_settings.json", "w") as f:
        json.dump(default_settings, f)
class App(QWidget):
    def __init__(self, parrent=None):
        super().__init__()
        self.parent = parrent
        self.title = 'Netbox to UglyPTY YAML Exporter'
        # Load Netbox settings from JSON if exists, else create it.
        try:
            with open("netbox_settings.json", "r") as f:
                settings = json.load(f)
            self.default_token = settings.get("token", "")
            self.default_url = settings.get("url", "http://netbox.yourcompany.com")
        except FileNotFoundError:
            create_default_settings()
            self.default_token = ""
            self.default_url = "http://netbox.yourcompany.com"
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Netbox to Session Export")
        self.setMinimumWidth(300)
        self.tokenField = QLineEdit(self)
        self.tokenField.setText("")
        self.tokenField.setPlaceholderText('Enter your Netbox Token')
        self.tokenField.setText(self.default_token)
        layout.addWidget(self.tokenField)

        self.urlField = QLineEdit(self)
        self.urlField.setText("http://netbox.yourcompany.com")
        self.urlField.setPlaceholderText('Enter your Netbox URL')
        self.urlField.setText(self.default_url)
        layout.addWidget(self.urlField)

        self.downloadButton = QPushButton('Download', self)
        self.downloadButton.clicked.connect(self.startDownloadThread)
        self.downloadButton.setStyleSheet("background-color: #006400; color: white;")
        layout.addWidget(self.downloadButton)

        self.progress = QProgressBar(self)
        layout.addWidget(self.progress)

        self.statusLabel = QLabel('Status: Waiting', self)
        layout.addWidget(self.statusLabel)

        self.setLayout(layout)
        self.show()

    def startDownloadThread(self):
        self.downloadThread = DownloadThread(self.tokenField.text(), self.urlField.text())
        self.downloadThread.progress_signal.connect(self.updateProgressBar)
        self.downloadThread.status_signal.connect(self.updateStatusLabel)
        self.downloadThread.save_file_signal.connect(self.showSaveFileDialog)
        self.downloadThread.start()

    def showSaveFileDialog(self, uglypty_list):

        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "YAML Files (*.yaml);;All Files (*)")
        if filePath:
            if not filePath.endswith('.yaml'):
                filePath += '.yaml'
            with open(filePath, "w") as f:
                yaml.dump(uglypty_list, f, default_flow_style=False)
            self.statusLabel.setText(f"Download Complete. Saved to {filePath}")
    def updateProgressBar(self, value):
        self.progress.setValue(value)

    def updateStatusLabel(self, text):
        self.statusLabel.setText(f"Status: {text}")



if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    app.exec()
