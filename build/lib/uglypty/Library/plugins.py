import sys
import os

import requests
import yaml
import subprocess
import threading
from PyQt6.QtCore import pyqtSignal, Qt, QUrl, QSize, QThread
from PyQt6.QtGui import QMovie
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QApplication, QMessageBox, QPlainTextEdit
import sqlite3

from PyQt6.QtCore import pyqtSignal

class CustomOutputDialog(QDialog):
    new_output = pyqtSignal(str)
    finished = pyqtSignal(bool)  # Emit True if successfully installed, False otherwise

    def __init__(self, parent=None):
        super(CustomOutputDialog, self).__init__(parent)
        self.setWindowTitle("Installing...")
        self.spinner = QLabel()
        # movie = QMovie("./path/to/your/spinner.gif")
        # self.spinner.setMovie(movie)
        # self.spinner.hide()

        layout = QVBoxLayout()

        self.text_edit = QPlainTextEdit()
        self.text_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.text_edit.clear()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        layout.addWidget(self.text_edit)
        layout.addWidget(close_button)

        self.setLayout(layout)

        # Make sure to disconnect first to avoid duplicate connections
        try:
            self.new_output.disconnect()
        except TypeError:
            pass  # No previous connections

        self.new_output.connect(self.update_output)



    def update_output(self, text):
        if text not in self.text_edit.toPlainText():
            self.text_edit.appendPlainText(text)

    def install_plugin(self, command):
        success = False
        try:

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            while True:
                output = process.stdout.readline().strip()
                if output:
                    self.new_output.emit(output)

                    # Check for success or already installed status
                    if "Successfully installed" in output:
                        success = True
                    elif "Requirement already satisfied" in output:
                        success = True
                    elif "Successfully uninstalled" in output:
                        success = True

                if process.poll() is not None:
                    break
        except Exception as e:
            self.new_output.emit(f"An error occurred: {str(e)}")
        finally:
            self.finished.emit(success)

class DownloadThread(QThread):
    download_successful = pyqtSignal(bool)

    def __init__(self, url, local_path):
        super(DownloadThread, self).__init__()
        self.url = url
        self.local_path = local_path

    def run(self):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(self.url, headers=headers)
            r.raise_for_status()
            with open(self.local_path, 'wb') as f:
                f.write(r.content)
            self.download_successful.emit(True)
        except Exception as e:
            self.download_successful.emit(False)

class PluginManager(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setWindowTitle("Plugin Manager")
        # Create a QLabel and set its alignment to center
        self.spinner_label = QLabel()
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a QMovie object for the spinner animation
        current_file_path = os.path.abspath(__file__)  # Get the path of the current file
        current_dir = os.path.dirname(current_file_path)  # Get the directory of the current file
        parent_path = os.path.dirname(current_dir)
        # Construct the path to editor.html relative to the current directory
        spinner_gif_path = os.path.join(parent_path, "static", "green-globe-spinner.gif")
        print(f"loading...{spinner_gif_path}")
        spinner_movie = QMovie(spinner_gif_path)
        spinner_movie.setScaledSize(QSize(50, 50))
        # Assign the movie to the QLabel
        self.spinner_label.setMovie(spinner_movie)
        self.spinner_label.hide()
        # Start the spinner animation
        spinner_movie.start()

        # Add spinner_label to your layout
        layout.addWidget(self.spinner_label)

        self.listWidget = QListWidget()

        # Load available plugins from the catalog.yaml
        with open("catalog.yaml", 'r') as stream:
            self.catalog_data = yaml.safe_load(stream)['plugins']

        for plugin in self.catalog_data:
            item = QListWidgetItem(plugin['name'])
            item.setData(Qt.ItemDataRole.UserRole, plugin)
            self.listWidget.addItem(item)

        self.install_button = QPushButton("Install Selected Plugin")
        self.install_button.clicked.connect(self.install_plugin)
        self.uninstall_button = QPushButton("Uninstall Selected Plugin")  # New Button
        self.uninstall_button.clicked.connect(self.uninstall_plugin)  # New Connection

        layout.addWidget(QLabel("Available Plugins:"))
        layout.addWidget(self.listWidget)
        layout.addWidget(self.install_button)
        layout.addWidget(self.uninstall_button)

        # Add the hyperlink
        hyperlink = QLabel('<a href="none">Download .whl Plugins</a>')
        hyperlink.linkActivated.connect(self.open_browser)
        layout.addWidget(hyperlink)
        if not os.path.exists('./wheels'):
            os.makedirs('./wheels')
        self.setLayout(layout)

    def start_spinner(self):
        self.spinner_label.show()

    def stop_spinner(self):
        self.spinner_label.hide()

    def open_browser(self):
        QDesktopServices.openUrl(QUrl("https://github.com/scottpeterman/UglyPTY-Plugins"))

    def install_plugin(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            self.install_button.setEnabled(False)
            self.start_spinner()
            # Initialize the dialog here
            self.dialog = CustomOutputDialog(self)
            self.dialog.new_output.connect(self.dialog.update_output)
            self.dialog.finished.connect(self.on_installation_complete)

            selected_plugin = self.catalog_data[self.listWidget.row(selected_item)]
            wheel_path = selected_plugin['wheel_url']

            def on_download_complete(success):
                if success:
                    self.dialog.new_output.emit("Download successful.")
                    install_command = ["pip", "install", wheel_path]
                    self.dialog.show()
                    self.run_install(install_command)
                else:
                    self.dialog.new_output.emit("Download failed. Aborting installation.")
                    self.install_button.setEnabled(True)
                self.stop_spinner()

            if wheel_path.startswith("https:"):

                local_path = "./wheels/" + wheel_path.split('/')[-1]
                self.download_thread = DownloadThread(wheel_path, local_path)
                self.download_thread.download_successful.connect(on_download_complete)
                self.download_thread.start()
            else:
                on_download_complete(True)


    def run_install(self, install_command):
        thread = threading.Thread(target=self.dialog.install_plugin, args=(install_command,))
        thread.start()
        # thread.join()  # Causes dialog hang

        self.install_button.setEnabled(True)  # Re-enable the button

    def on_installation_complete(self, success):
        if success:
            selected_item = self.listWidget.currentItem()
            selected_plugin = self.catalog_data[self.listWidget.row(selected_item)]

            conn = sqlite3.connect("settings.SQLite")
            cursor = conn.cursor()

            # Check if the plugin is already in the database
            cursor.execute("SELECT * FROM installed_plugins WHERE name = ?", (selected_plugin['name'],))
            existing_entry = cursor.fetchone()

            if existing_entry is None:
                # Insert the new plugin if it does not exist
                cursor.execute(
                    "INSERT INTO installed_plugins (name, package_name, description, import_name, status) VALUES (?, ?, ?, ?, ?)",
                    (selected_plugin['name'], selected_plugin['package_name'], selected_plugin['description'],
                     selected_plugin['import_name'], 'installed'))
                conn.commit()
            else:
                # Optionally update the existing entry if needed
                cursor.execute(
                    "UPDATE installed_plugins SET status = ? WHERE name = ?",
                    ('installed', selected_plugin['name'])
                )
                conn.commit()

            conn.close()
            QMessageBox.information(self, 'Success', 'Plugin successfully installed or already present.\nRestart the application to see your new plugin in the Plugins menu')
        else:
            QMessageBox.critical(self, 'Failure', 'Plugin installation failed.')

        self.install_button.setEnabled(True)

    def uninstall_plugin(self):  # New Method
        selected_item = self.listWidget.currentItem()
        if selected_item:
            self.uninstall_button.setEnabled(False)
            selected_plugin = self.catalog_data[self.listWidget.row(selected_item)]
            # package_name = selected_plugin['package_name']
            package_name = selected_plugin['import_name'].split(".")[0]
            # uglyplugin_ace.ugly_ace.QtAceWidget
            uninstall_command = ["pip", "uninstall", "-y", package_name]

            # Create and display the dialog
            self.dialog = CustomOutputDialog(self)
            self.dialog.new_output.connect(self.dialog.update_output)
            self.dialog.finished.connect(
                self.on_uninstallation_complete)  # New connection to handle uninstall completion
            self.dialog.setWindowTitle("Uninstalling...")
            self.dialog.show()

            self.run_uninstall(uninstall_command)

    def run_uninstall(self, uninstall_command):  # New Method
        thread = threading.Thread(target=self.dialog.install_plugin, args=(uninstall_command,))
        thread.start()

    def on_uninstallation_complete(self, success):  # New Method
        if success:
            selected_item = self.listWidget.currentItem()
            selected_plugin = self.catalog_data[self.listWidget.row(selected_item)]

            conn = sqlite3.connect("settings.SQLite")
            cursor = conn.cursor()

            cursor.execute("DELETE FROM installed_plugins WHERE name = ?", (selected_plugin['name'],))
            conn.commit()
            conn.close()

            QMessageBox.information(self, 'Success', 'Plugin successfully uninstalled.')
        else:
            QMessageBox.critical(self, 'Failure', 'Plugin uninstallation failed.')

        self.uninstall_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    plugin_manager = PluginManager()
    plugin_manager.setWindowTitle("Plugin Manager")
    plugin_manager.resize(400, 300)
    plugin_manager.show()

    sys.exit(app.exec())
