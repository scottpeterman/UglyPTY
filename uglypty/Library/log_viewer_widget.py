import os
import yaml
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QFileDialog, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt6.QtGui import QIcon, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

class FileTree(QWidget):
    file_double_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super(FileTree, self).__init__(parent)

        # Set up layout
        self.layout = QVBoxLayout(self)

        # Set up the button
        self.button = QPushButton("Select Folder", self)
        self.button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.button)

        # Set up the tree widget
        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)  # Hide header
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)  # Connect to double click handler
        self.layout.addWidget(self.tree)

        # Set up the icons
        self.folder_icon = QIcon("./icons/folder.png")
        self.folder_open_icon = QIcon("./icons/folder_open.png")  # New icon for opened folders
        self.file_icon = QIcon("./icons/file.png")

        self.load_folder("./")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            try:
                # Set the header to the selected folder name
                self.tree.setHeaderLabel(os.path.basename(folder))
                self.tree.setHeaderHidden(False)  # Show header
                self.load_folder(folder)
            except Exception as e:
                print(f"Failed to load the folder: {e}")

    def load_folder(self, folder, parent_item=None):
        # Create separate lists for directories and files
        dirs = []
        files = []

        for entry in os.scandir(folder):
            if entry.name.startswith('.'):
                continue
            if entry.is_dir():
                dirs.append(entry)
            else:
                files.append(entry)

        # Sort the directories and files
        dirs.sort(key=lambda e: e.name.lower())
        files.sort(key=lambda e: e.name.lower())

        # If parent_item is None, add items to the tree, otherwise add them as children of the parent_item
        if parent_item is None:
            self.tree.clear()
            add_item = self.tree
        else:
            parent_item.takeChildren()  # Remove existing children
            add_item = parent_item
            parent_item.setIcon(0, self.folder_open_icon)  # Set the icon for the opened folder

        # Add directories and files to the tree widget
        for entries in [dirs, files]:
            for entry in entries:
                icon = self.folder_icon if entry.is_dir() else self.file_icon

                # If the entry is a file and the extension is .yaml, load the status from the file
                if entry.is_file() and entry.name.endswith('.yaml'):
                    try:
                        with open(entry.path, 'r') as file:
                            content = yaml.safe_load(file)
                            if 'status' in content:
                                item = QTreeWidgetItem(add_item)
                                item.setIcon(0, icon)
                                item.setText(0, entry.name)
                                item.setData(0, Qt.ItemDataRole.UserRole, entry.path)  # Store the full path
                                if content['status'] == 'failure':
                                    item.setForeground(0, QBrush(QColor('red')))
                                elif content['status'] == 'skipped':
                                    item.setForeground(0, QBrush(QColor('yellow')))
                    except yaml.YAMLError as error:
                        print(f"Error parsing YAML file {entry.path}: {error}")
                else:  # If the entry is not a .yaml file or a directory, add it normally
                    item = QTreeWidgetItem(add_item)
                    item.setIcon(0, icon)
                    item.setText(0, entry.name)
                    item.setData(0, Qt.ItemDataRole.UserRole, entry.path)  # Store the full path

        if parent_item:
            QTimer.singleShot(100, lambda: parent_item.setExpanded(True))

        if parent_item is None:
            self.tree.expandAll()

    def on_item_double_clicked(self, item, column):
        path = item.data(column, Qt.ItemDataRole.UserRole)
        if os.path.isfile(path):
            # Emit a signal with the path of the double-clicked file
            self.file_double_clicked.emit(path)

        elif os.path.isdir(path):
            # Load the directory
            # Get the item from the tree widget
            item_to_change = self.tree.selectedItems()[0]
            self.load_folder(path, item_to_change)
