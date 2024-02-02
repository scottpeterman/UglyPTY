from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QTextCursor, QTextFormat, QColor, QKeySequence, QTextCharFormat, QTextOption
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit, QPushButton, QFileDialog, \
    QListWidget, QLabel
from diff_match_patch import diff_match_patch


class ReadOnlyEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Paste):
            return
        super().keyPressEvent(event)

class App(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()
        self.parent = parent

    def initUI(self):
        self.resize(800,400)
        layout = QVBoxLayout()
        hlayout = QHBoxLayout()

        self.leftEditor = ReadOnlyEditor()
        self.rightEditor = ReadOnlyEditor()
        self.leftEditor.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self.rightEditor.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self.leftLineNumbers = QListWidget()
        self.leftLineNumbers.setFixedWidth(30)
        self.rightLineNumbers = QListWidget()
        self.rightLineNumbers.setFixedWidth(30)

        hlayout.addWidget(self.leftLineNumbers)
        hlayout.addWidget(self.leftEditor)
        hlayout.addWidget(self.rightLineNumbers)
        hlayout.addWidget(self.rightEditor)

        legendLayout = QHBoxLayout()
        self.addLegendItem(legendLayout, "#8B6508", "Left Only")
        self.addLegendItem(legendLayout, "#8B0000", "Right Only")
        self.addLegendItem(legendLayout, "#006400", "Changed")

        layout.addLayout(hlayout)
        layout.addLayout(legendLayout)

        layout.addLayout(hlayout)

        # Hide the scrollbars in the QListWidgets
        self.leftLineNumbers.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.leftLineNumbers.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.rightLineNumbers.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.rightLineNumbers.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Connect the scroll bars for synchronized scrolling
        self.leftEditor.verticalScrollBar().valueChanged.connect(self.syncScroll)
        self.rightEditor.verticalScrollBar().valueChanged.connect(self.syncScroll)

        # Connect the scroll bars for line number synchronization
        self.leftEditor.verticalScrollBar().valueChanged.connect(self.syncLineNumberScroll)
        self.rightEditor.verticalScrollBar().valueChanged.connect(self.syncLineNumberScroll)

        btnOpenLeft = QPushButton('Open Left')
        btnOpenLeft.clicked.connect(self.openLeftFile)
        btnOpenRight = QPushButton('Open Right')
        btnOpenRight.clicked.connect(self.openRightFile)
        btnPasteLeft = QPushButton('Paste to Left')
        btnPasteLeft.clicked.connect(self.pasteToLeft)
        btnPasteRight = QPushButton('Paste to Right')
        btnPasteRight.clicked.connect(self.pasteToRight)
        btnCompare = QPushButton('Compare')
        btnCompare.clicked.connect(self.compareTexts)
        btnCompare.setStyleSheet("background-color: #234f96; color: white;")  # Dark forest green background and white text

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(btnOpenLeft)
        btnLayout.addWidget(btnOpenRight)
        btnLayout.addWidget(btnPasteLeft)
        btnLayout.addWidget(btnPasteRight)
        btnLayout.addWidget(btnCompare)

        layout.addLayout(btnLayout)

        self.setLayout(layout)
        self.setWindowTitle('UglyDiff2')
        self.show()

    def syncScroll(self, value):
        sender = self.sender()
        if sender == self.leftEditor.verticalScrollBar():
            self.rightEditor.verticalScrollBar().setValue(value)
        elif sender == self.rightEditor.verticalScrollBar():
            self.leftEditor.verticalScrollBar().setValue(value)

    def syncLineNumberScroll(self, value):
        sender = self.sender()
        if sender == self.leftEditor.verticalScrollBar():
            self.leftLineNumbers.verticalScrollBar().setValue(value)
        elif sender == self.rightEditor.verticalScrollBar():
            self.rightLineNumbers.verticalScrollBar().setValue(value)

    def addLegendItem(self, layout, color, text):
        label = QLabel()
        label.setText(text)

        label.setStyleSheet(f"background-color: {color}; color: white; padding: 5px;")
        layout.addWidget(label)

    def updateLineNumbers(self, editor, listWidget):
        listWidget.clear()
        blockCount = editor.blockCount()
        for i in range(1, blockCount + 1):
            listWidget.addItem(str(i))

    def openLeftFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Left File", "", "All Files (*);;Text Files (*.txt)")
        if filePath:
            with open(filePath, 'r') as f:
                self.leftEditor.setPlainText(f.read())
            self.updateLineNumbers(self.leftEditor, self.leftLineNumbers)

    def openRightFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Right File", "", "All Files (*);;Text Files (*.txt)")
        if filePath:
            with open(filePath, 'r') as f:
                self.rightEditor.setPlainText(f.read())
            self.updateLineNumbers(self.rightEditor, self.rightLineNumbers)

    def pasteToLeft(self):
        clipboard = QApplication.clipboard()
        self.leftEditor.setPlainText(clipboard.text())
        self.updateLineNumbers(self.leftEditor, self.leftLineNumbers)

    def pasteToRight(self):
        clipboard = QApplication.clipboard()
        self.rightEditor.setPlainText(clipboard.text())
        self.updateLineNumbers(self.rightEditor, self.rightLineNumbers)



    # ... (your existing imports and code)

    def compareTexts(self):
        text1 = self.leftEditor.toPlainText().strip()
        text2 = self.rightEditor.toPlainText().strip()

        dmp = diff_match_patch()
        diffs = dmp.diff_main(text1, text2)
        dmp.diff_cleanupSemantic(diffs)  # Optional: clean up the diffs for better display

        left_cursor = self.leftEditor.textCursor()
        right_cursor = self.rightEditor.textCursor()

        # Define different formats for different types of changes
        left_only_format = QTextCharFormat()
        left_only_format.setBackground(QColor("#8B6508"))
        left_only_format.setForeground(QColor("white"))

        right_only_format = QTextCharFormat()
        right_only_format.setBackground(QColor("#8B0000"))
        right_only_format.setForeground(QColor("white"))

        changed_format = QTextCharFormat()
        changed_format.setBackground(QColor("#006400"))
        changed_format.setForeground(QColor("white"))

        left_pos = 0
        right_pos = 0

        for op, data in diffs:
            if op == 0:  # No change
                left_pos += len(data)
                right_pos += len(data)
            elif op == -1:  # Deletion (present in text1 but not text2)
                left_cursor.setPosition(left_pos)
                left_cursor.setPosition(left_pos + len(data), QTextCursor.MoveMode.KeepAnchor)
                left_cursor.mergeCharFormat(left_only_format)
                left_pos += len(data)
            elif op == 1:  # Insertion (present in text2 but not text1)
                right_cursor.setPosition(right_pos)
                right_cursor.setPosition(right_pos + len(data), QTextCursor.MoveMode.KeepAnchor)
                right_cursor.mergeCharFormat(right_only_format)
                right_pos += len(data)

        self.leftEditor.setTextCursor(left_cursor)
        self.rightEditor.setTextCursor(right_cursor)

    # ... (your other code)


if __name__ == '__main__':
    print(f"Debug webengine here: http://127.0.0.1:9222/")
    print("cli python uglyeditor.py --webEngineArgs --remote-debugging-port=9222")
    import sys

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    ex = App()
    sys.exit(app.exec()) # comment
