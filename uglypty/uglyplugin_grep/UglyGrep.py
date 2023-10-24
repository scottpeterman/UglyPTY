from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit,
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem,
                             QPlainTextEdit, QFileDialog, QDialog, QHBoxLayout, QStatusBar)

import os
import sys
from time import time

from PyQt6.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout, QStatusBar
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt


class CustomViewerDialog(QDialog):
    def __init__(self, parent, file_path, search_pattern):
        super().__init__(parent)
        self.file_path = file_path
        self.search_pattern = search_pattern
        self.setWindowTitle(f"Viewer - {self.file_path}")

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.textEditor = QPlainTextEdit()
        self.statusBar = QStatusBar()

        layout.addWidget(self.textEditor)
        layout.addWidget(self.statusBar)

        self.setLayout(layout)

        self.loadFile()
        self.highlightPattern()
        self.updateStatusBar()
        self.textEditor.cursorPositionChanged.connect(self.updateStatusBar)

    def loadFile(self):
        try:
            with open(self.file_path, "r") as f:
                text = f.read()
            self.textEditor.setPlainText(text)
        except Exception as e:
            print(f"Unable to open file: {e}")

    def highlightPattern(self):
        cursor = self.textEditor.textCursor()
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("darkgreen"))
        cursor.setPosition(0)
        self.textEditor.setTextCursor(cursor)

        pattern_length = len(self.search_pattern)
        text = self.textEditor.toPlainText()
        search_pos = 0

        while True:
            search_pos = text.find(self.search_pattern, search_pos)
            if search_pos == -1:
                break
            cursor.setPosition(search_pos, QTextCursor.MoveMode.MoveAnchor)
            cursor.setPosition(search_pos + pattern_length, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(highlight_format)
            search_pos += pattern_length

    def updateStatusBar(self):
        cursor = self.textEditor.textCursor()
        line_num = cursor.blockNumber() + 1  # +1 to make it human-readable (start from 1)
        self.statusBar.showMessage(f"Line: {line_num}")

class BoyerMooreSearch:
    def __init__(self, pattern):
        self.pattern = pattern
        self.bad_char_table = self.build_bad_char_table()
        self.good_suffix_table = self.build_good_suffix_table()

    def build_bad_char_table(self):
        bad_char_table = {}
        for index, char in enumerate(self.pattern[:-1]):
            bad_char_table[char] = len(self.pattern) - 1 - index
        return bad_char_table

    def build_good_suffix_table(self):
        pattern_length = len(self.pattern)
        border_position = [0] * pattern_length
        shift_distance = [0] * pattern_length

        # Build border_position array
        border_position[pattern_length - 1] = pattern_length
        j = pattern_length - 1
        for i in range(pattern_length - 2, -1, -1):
            while j < pattern_length - 1 and self.pattern[i] != self.pattern[j]:
                j = border_position[j + 1] - 1
            j -= 1
            border_position[i] = j + 1

        # Build shift_distance array
        for i in range(pattern_length):
            shift_distance[i] = pattern_length - border_position[i]

        j = 0
        for i in range(pattern_length - 1, -1, -1):
            if border_position[i] == i + 1:
                while j < i:
                    if shift_distance[j] == pattern_length:
                        shift_distance[j] = i
                    j += 1

        return shift_distance

    def search(self, text):
        text_index = 0
        text_length = len(text)
        pattern_length = len(self.pattern)

        while text_index <= text_length - pattern_length:
            pattern_index = pattern_length - 1

            while pattern_index >= 0 and self.pattern[pattern_index] == text[text_index + pattern_index]:
                pattern_index -= 1

            if pattern_index < 0:
                return text_index

            skip_bad_char = self.bad_char_table.get(text[text_index + pattern_index], pattern_length)
            skip_good_suffix = self.good_suffix_table[pattern_index]

            text_index += max(skip_bad_char, skip_good_suffix)

        return -1



class SearchThread(QThread):
    signal = pyqtSignal(str, int, str, int)  # Add an extra int for line_number
    file_signal = pyqtSignal(int)


    def __init__(self, pattern, root_dir, file_extension):
        super().__init__()
        self.pattern = pattern
        self.root_dir = root_dir
        self.file_extension = file_extension

    def run(self):
        file_count = 0
        for foldername, _, filenames in os.walk(self.root_dir):
            if self.isInterruptionRequested():
                return
            for filename in filenames:
                try:
                    if filename.endswith(self.file_extension):
                        file_count += 1  # Increment file count
                        self.file_signal.emit(file_count)

                        fullpath = os.path.join(foldername, filename)
                        # print(f"Processing: {filename}:{foldername}")
                        with open(fullpath, "r") as f:
                            text = f.read()
                        bm = BoyerMooreSearch(self.pattern)
                        index = bm.search(text)
                        if index != -1:
                            text_up_to_index = text[:index]
                            line_number = text_up_to_index.count("\n") + 1
                            self.signal.emit(fullpath, index, self.pattern, line_number)  # Emit line_number as well
                except Exception as e:
                    print(f"Error processing file: {e}")

# Main App Class
class Grep(QWidget):
    def __init__(self):
        super().__init__()
        self.match_count = 0
        self.file_count = 0
        self.start_time = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setWindowTitle("UglyGrep")
        self.resize(600, 400)

        self.startDirInput = QLineEdit('./Capture', self)
        layout.addWidget(self.startDirInput)

        self.fileSpecInput = QLineEdit('*.txt', self)
        self.fileSpecInput.setPlaceholderText('Enter file extension (e.g., *.txt, *.md)')
        layout.addWidget(self.fileSpecInput)

        self.openFolderButton = QPushButton('Open Folder', self)
        self.openFolderButton.clicked.connect(self.openFolder)
        layout.addWidget(self.openFolderButton)

        self.patternInput = QLineEdit(self)
        self.patternInput.setPlaceholderText('Enter search pattern')
        layout.addWidget(self.patternInput)

        self.searchButton = QPushButton('Search', self)
        layout.addWidget(self.searchButton)

        self.resultLabel = QLabel('Results:', self)
        layout.addWidget(self.resultLabel)

        # Initialize TableWidget to replace ListWidget
        self.resultTable = QTableWidget(0, 3, self)
        self.resultTable.setHorizontalHeaderLabels(['Line No.', 'Filename', 'Path'])
        self.resultTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.resultTable.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.resultTable.itemDoubleClicked.connect(self.openFile)
        layout.addWidget(self.resultTable)

        telemetryLayout = QHBoxLayout()  # New horizontal layout
        self.matchCountLabel = QLabel('Matches: 0')
        self.fileCountLabel = QLabel('Files: 0')  # New label for file count
        self.elapsedTimeLabel = QLabel('Time: 00:00:00')  # New label for elapsed time

        telemetryLayout.addWidget(self.matchCountLabel)
        telemetryLayout.addWidget(self.fileCountLabel)
        telemetryLayout.addWidget(self.elapsedTimeLabel)

        layout.addLayout(telemetryLayout)  # Add the horizontal layout to the main layout

        self.setLayout(layout)
        self.searchButton.clicked.connect(self.initSearch)

    def updateResults(self, fullpath, index, pattern, line_number):
        self.match_count += 1
        self.matchCountLabel.setText(f"Matches: {self.match_count}")
        self.updateElapsedTime()
        filename = os.path.basename(fullpath)
        path_without_filename = os.path.dirname(fullpath)
        # print(path_without_filename)

        row_position = self.resultTable.rowCount()
        self.resultTable.insertRow(row_position)

        line_item = QTableWidgetItem(str(line_number))
        filename_item = QTableWidgetItem(filename)
        path_item = QTableWidgetItem(path_without_filename)

        line_item.fullPath = fullpath
        line_item.index = index

        self.resultTable.setItem(row_position, 0, line_item)
        self.resultTable.setItem(row_position, 1, filename_item)
        self.resultTable.setItem(row_position, 2, path_item)


    def openFile(self, item):
        row = item.row()
        item = self.resultTable.item(row, 0)  # Always get the item in column 0
        fullpath = item.fullPath
        pattern = self.patternInput.text()

        self.viewer_dialog = CustomViewerDialog(self, fullpath, pattern)
        self.viewer_dialog.resize(600, 400)
        self.viewer_dialog.exec()


    def openFolder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.startDirInput.setText(folder)

    def searchCompleted(self):
        self.resultTable.resizeColumnsToContents()  # Automatically adjust column widths

        self.resultTable.setSortingEnabled(True)
        self.resultTable.sortItems(1, Qt.SortOrder.AscendingOrder)  # Sort by filename (column 1)
        self.dialog.close()

    def updateFileCount(self, file_count):
        self.file_count = file_count
        self.fileCountLabel.setText(f"Files: {self.file_count}")

    def updateElapsedTime(self):
        elapsed_time = int(time() - self.start_time)
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.elapsedTimeLabel.setText(f"Time: {hours:02d}:{minutes:02d}:{seconds:02d}")

    def initSearch(self):
        self.resultTable.setRowCount(0)
        pattern = self.patternInput.text()
        root_dir = self.startDirInput.text()
        self.match_count = 0
        self.start_time = time()  # Record the start time


        try:
            file_extension = str(self.fileSpecInput.text()).split(".")[1]
        except Exception as e:
            file_extension = "*"
        file_extension = "." + file_extension
        self.searchThread = SearchThread(pattern, root_dir, file_extension)
        self.searchThread.signal.connect(self.updateResults)
        self.searchThread.file_signal.connect(self.updateFileCount)
        self.searchThread.finished.connect(self.searchCompleted)  # New line

        self.dialog = QDialog(self)
        self.dialog.setWindowTitle('Searching...')
        self.dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        dLayout = QHBoxLayout()
        dLabel = QLabel("Searching, please wait...", self.dialog)
        cancelButton = QPushButton('Cancel', self.dialog)
        cancelButton.clicked.connect(self.cancelSearch)
        dLayout.addWidget(dLabel)
        dLayout.addWidget(cancelButton)

        self.dialog.setLayout(dLayout)
        self.dialog.show()

        self.searchThread.start()

    def cancelSearch(self):
        self.searchThread.requestInterruption()
        self.dialog.close()

def main():
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    ex = Grep()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
