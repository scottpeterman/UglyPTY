import sys
import os
from PyQt6.QtWidgets import QApplication, QTabBar, QVBoxLayout, QPlainTextEdit, QTabWidget, QWidget, QHBoxLayout, QPushButton, QFrame, QMessageBox, QSplitter
from uglypty.log_viewer_widget import FileTree
import string
import re


class FileViewer(QWidget):
    def __init__(self, parent=None):
        super(FileViewer, self).__init__(parent)
        self.setWindowTitle("Log Viewer")
        # Set up the main layout
        self.main_layout = QVBoxLayout(self)

        # Set up the splitter
        self.splitter = QSplitter(self)
        self.main_layout.addWidget(self.splitter)

        # Add the FileTree widget
        self.file_tree = FileTree(self)
        self.file_tree.setFixedWidth(200)
        self.file_tree.file_double_clicked.connect(self.handle_open)
        self.splitter.addWidget(self.file_tree)

        # Set up the text display area
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setFixedWidth(500)
        self.tab_widget.setFixedHeight(600)

        self.tab_widget.setTabsClosable(True)  # Enable closing of tabs
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Connect to slot for closing tabs
        self.splitter.addWidget(self.tab_widget)

        # Keep track of which files are open in which tabs
        self.open_files = {}

    def handle_open(self, file_path):
        # Check if the file is already open in a tab
        if file_path in self.open_files:
            # If it is, select the tab
            self.tab_widget.setCurrentIndex(self.open_files[file_path])
        else:
            # Otherwise, open the file in a new tab
            self.add_tab(file_path)

    def add_tab(self, file_path):
        file_name = os.path.basename(file_path)
        # Create a new QWidget and QVBoxLayout
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)

        # Create QPlainTextEdit and add it to the QVBoxLayout
        text_widget = QPlainTextEdit(tab_widget)
        tab_layout.addWidget(text_widget)

        # Create QPushButton and add it to the QVBoxLayout
        clear_button = QPushButton('Clear Log', tab_widget)
        clear_button.clicked.connect(lambda: self.confirm_clear(file_path, text_widget))
        tab_layout.addWidget(clear_button)

        try:
            # Load file content
            with open(file_path, 'r') as file:
                file_content = file.read()

            # Remove ANSI escape sequences
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            content_without_escapes = ansi_escape.sub('', file_content)

            # Remove non-printable characters
            printable_content = ''.join(filter(lambda x: x in string.printable, content_without_escapes))

            text_widget.setPlainText(printable_content)

            # Add tab
            tab_index = self.tab_widget.addTab(tab_widget, file_name)
            self.open_files[file_path] = tab_index  # Record which tab this file is open in
            self.tab_widget.setCurrentIndex(tab_index)  # Set the new tab as the current tab

        except Exception as e:
            print(e)

    def confirm_clear(self, file_path, text_widget):
        reply = QMessageBox.question(self, 'Confirmation', "Are you sure you want to clear this file?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_file(file_path, text_widget)

    def clear_file(self, file_path, text_widget):
        # Clear the file content
        with open(file_path, 'w') as file:
            file.write("")

        # Clear the text in the QPlainTextEdit
        text_widget.setPlainText("")

    def close_tab(self, index):
        # Remove the tab at the given index
        self.tab_widget.removeTab(index)

        # Remove the file from open_files
        for file_path, tab_index in list(self.open_files.items()):  # We need to convert to list to safely modify while iterating
            if tab_index == index:
                del self.open_files[file_path]
            elif tab_index > index:
                # Decrement the tab indices of all tabs after the one that was closed
                self.open_files[file_path] = tab_index - 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileViewer()
    window.show()
    sys.exit(app.exec())
