import sys
import os
import yaml
import re
from PyQt6.QtWidgets import QApplication, QTextBrowser, QTabWidget, QWidget, QMessageBox, QSplitter, QStyleFactory
from PyQt6.QtWidgets import QFormLayout
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
# from collect_gui_netmiko import *
from uglypty.uglyplugin_yaml.YAMLSearch_widget import FileTree
import traceback
class SearchDialog(QDialog):
    search_initiated = pyqtSignal(str)

    def __init__(self, parent=None):
        super(SearchDialog, self).__init__(parent)
        self.p = parent
        layout = QVBoxLayout(self)

        self.string_search_line_edit = QLineEdit(self)
        layout.addWidget(QLabel("Search string:"))
        layout.addWidget(self.string_search_line_edit)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.initiate_search)
        layout.addWidget(self.search_button)

    def initiate_search(self):
        self.p.search_string = str(self.string_search_line_edit.text())
        self.search_initiated.emit(self.string_search_line_edit.text())

class YAMLViewer(QWidget):
    def __init__(self, parent=None):
        super(YAMLViewer, self).__init__(parent)
        self.setWindowTitle("YAML Search")

        self.main_layout = QVBoxLayout(self)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.open_search_dialog)
        self.search_button.setMaximumWidth(200)
        self.main_layout.addWidget(self.search_button)

        self.search_string = None
        self.splitter = QSplitter(self)
        self.main_layout.addWidget(self.splitter)

        self.file_tree = FileTree(self)
        self.file_tree.setMinimumWidth(300)
        self.file_tree.setMaximumWidth(300)
        self.file_tree.file_double_clicked.connect(self.handle_open)
        self.splitter.addWidget(self.file_tree)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMinimumWidth(600)
        self.tab_widget.setMinimumHeight(600)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.splitter.addWidget(self.tab_widget)

        # Create an instance of CollectorForm and add it to the splitter
        # self.collector_form = CollectorForm()
        # self.splitter.addWidget(self.collector_form)

        self.open_files = {}

    def open_search_dialog(self):
        self.search_dialog = SearchDialog(self)
        self.search_dialog.search_initiated.connect(self.handle_search)
        self.search_dialog.show()

    def handle_search(self, search_string):
        self.file_tree.load_folder(self.file_tree.current_folder, search_string=search_string)

    def handle_open(self, file_info):
        file_path, line_number = file_info

        if file_path in self.open_files:
            self.tab_widget.setCurrentIndex(self.open_files[file_path])
        else:
            self.display_yaml_file(file_path, line_number)

    def display_yaml_file(self, file_path, line_number):
        try:
            form_widget = QWidget()
            form_layout = QFormLayout(form_widget)
            try:
                with open(file_path, 'r') as file:
                    yaml_data = yaml.safe_load(file)
            except Exception as e:
                self.notify("File Error", f"Error reading yaml: {e}")
                return

            keys = yaml_data.keys()
            if "status" in keys:
                label = QLabel("Status")
                line_edit = QLineEdit()
                line_edit.setText(str(yaml_data['status']))
                form_layout.addRow(label, line_edit)
            for key, value in yaml_data["device"].items():
                if key == "password":
                    continue
                if key == "status":
                    print(f"status: {yaml_data['status']}")
                label = QLabel(key)
                line_edit = QLineEdit()
                line_edit.setText(str(value))
                form_layout.addRow(label, line_edit)

            output_text_edit = QTextBrowser()

            # Get the 'output' key's value and replace newline characters and spaces
            output_text = yaml_data["output"]
            if self.search_string is not None:
                output_text = output_text.replace(self.search_string, f'<hr><div>Found:</div> {self.search_string}<hr>{self.search_string}', 10)
            # print(output_text)
            output_text = re.sub(r"\n", "<br>", output_text)
            output_text = re.sub(r" ", "&nbsp;", output_text)

            # Highlight matching lines


            # Wrap the text in a full HTML document structure
            html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
            <title>Output</title>
            </head>
            <body>
            {output_text}
            </body>
            </html>
            """
            # print(html)
            output_text_edit.setText(html)

            form_layout.addRow(QLabel("Output:"), output_text_edit)

            tab_index = self.tab_widget.addTab(form_widget, os.path.basename(file_path))
            self.open_files[file_path] = tab_index
            self.tab_widget.setCurrentIndex(tab_index)

        except Exception as e:
            print(e)
            traceback.print_exc()

    def notify(self, message, info):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    def close_tab(self, index):
        self.tab_widget.removeTab(index)
        for file_path, tab_index in list(self.open_files.items()):  # We need to convert to list to safely modify while iterating
            if tab_index == index:
                del self.open_files[file_path]
            elif tab_index > index:
                self.open_files[file_path] = tab_index - 1

if __name__ == "__main__":
    import qdarktheme

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = YAMLViewer()
    window.show()
    sys.exit(app.exec())
