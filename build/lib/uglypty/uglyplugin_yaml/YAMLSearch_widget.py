import os
from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QWidget, QFileDialog, QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QIcon, QColor, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import yaml

from PyQt6.QtWidgets import QHBoxLayout


class FileTree(QWidget):
    file_double_clicked = pyqtSignal(tuple)  # Emit a tuple containing the file path and line number

    def __init__(self, parent=None):
        super(FileTree, self).__init__(parent)
        self.current_folder = './Capture'  # or another default directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.layout = QVBoxLayout(self)

        # Create a horizontal layout for the buttons
        self.button_layout = QHBoxLayout()

        self.button = QPushButton("Select Folder", self)
        self.button.clicked.connect(self.select_folder)
        self.button_layout.addWidget(self.button)

        # Add a Refresh button
        self.refresh_button = QPushButton(self)
        self.refresh_button.setMaximumWidth(30)
        self.refresh_button.setIcon(QIcon(f"{current_dir}/../icons/refresh.png"))  # Set the icon
        self.refresh_button.clicked.connect(self.refresh_tree)
        self.button_layout.addWidget(self.refresh_button)

        # Add the horizontal layout to the main layout
        self.layout.addLayout(self.button_layout)

        self.tree = QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.layout.addWidget(self.tree)

        print(f"current folder: {current_dir}")
        self.folder_icon = QIcon(f"{current_dir}/../icons/folder.png")
        self.folder_open_icon = QIcon(f"{current_dir}/../icons/folder_open.png")
        self.file_icon = QIcon(f"{current_dir}/../icons/file.png")
        try:
            self.load_directory_structure("./Capture")  # Changed this line to use the new method
        except:
            self.load_directory_structure("./")
    # New method to refresh the tree
    def refresh_tree(self):
        self.load_folder(self.current_folder)
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.current_folder = folder
            self.load_directory_structure(folder)  # Changed this line to use the new method

    def load_directory_structure(self, folder, parent_item=None):
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
            parent_item.setIcon(0, self.folder_open_icon)  # Set the icon for the opened folder
            add_item = parent_item

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

    def load_folder(self, folder, search_string=None):
        self.tree.clear()
        if search_string is not None and search_string != "":
            matching_entries = self.search_folder(folder, search_string)

            for entry in matching_entries:
                self.add_entry_to_tree(entry)
        else:
            self.load_directory_structure(folder)  # Changed this line to use the new method

    # ... Rest of the code


    def search_folder(self, folder, search_string=None):
        matching_entries = []

        for root, dirs, files in os.walk(folder):
            for name in dirs + files:
                entry_path = os.path.join(root, name)
                if os.path.isfile(entry_path):
                    if "__" not in entry_path:
                        with open(entry_path, 'r', encoding='utf-8',  errors='ignore') as file:
                            lines = file.readlines()
                            i = 0
                            if search_string is None:
                                search_string = ""
                            for line in lines:
                                if search_string not in line:
                                    i += 1
                                    continue


                                matching_entries.append((entry_path, i))
                                print(f"Found match: {entry_path}")
                                i += 1
                else:
                    matching_entries.append((entry_path, None))

        return matching_entries

    def add_entry_to_tree(self, entry):
        path, line_number = entry
        dirs = path.split(os.sep)

        parent_item = None
        current_path = ""

        for dir in dirs:
            current_path = os.path.join(current_path, dir)

            found = False
            for i in range(self.tree.topLevelItemCount()):
                if self.tree.topLevelItem(i).text(0) == dir:
                    parent_item = self.tree.topLevelItem(i)
                    found = True
                    break
            if not found and parent_item is not None:
                for i in range(parent_item.childCount()):
                    if parent_item.child(i).text(0) == dir:
                        parent_item = parent_item.child(i)
                        found = True
                        break

            if not found:
                if parent_item is None:
                    parent_item = QTreeWidgetItem(self.tree)
                else:
                    parent_item = QTreeWidgetItem(parent_item)
                parent_item.setText(0, dir)
                parent_item.setData(0, Qt.ItemDataRole.UserRole, (current_path, line_number))

    def on_item_double_clicked(self, item, column):
        data = item.data(column, Qt.ItemDataRole.UserRole)
        if isinstance(data, tuple) and len(data) == 2:
            path, line_number = data
            if os.path.isfile(path):
                self.file_double_clicked.emit((path, line_number))
        elif isinstance(data, str):
            path = data
            if os.path.isfile(path):
                # Emit a signal with the path of the double-clicked file
                self.file_double_clicked.emit((path, None))
            elif os.path.isdir(path):
                # Load the directory
                self.load_directory_structure(path, item)

        else:
            print("don't know what to do")

