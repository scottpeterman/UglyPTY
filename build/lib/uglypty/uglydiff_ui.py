from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView as QWebView
from PyQt6.QtWebChannel import QWebChannel
# from Library.settings_json import usettings
import difflib

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from bs4 import BeautifulSoup

class UI_Diff(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # MainWindow.setObjectName("MainWindow")
        # MainWindow.resize(1200, 636)
        # self.centralwidget = QtWidgets.QWidget(MainWindow)
        # self.centralwidget.setObjectName("centralwidget")
        # self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.leFile1 = QtWidgets.QLineEdit(self)
        self.leFile1.setObjectName("leFile1")
        self.horizontalLayout_2.addWidget(self.leFile1)
        self.pbFile1 = QtWidgets.QPushButton(self)
        self.pbFile1.setObjectName("pbFile1")
        self.pbFile1.clicked.connect(lambda: self.pbOpenFile(self.leFile1))
        self.horizontalLayout_2.addWidget(self.pbFile1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.leFile2 = QtWidgets.QLineEdit(self)
        self.leFile2.setObjectName("leFile2")

        self.horizontalLayout_5.addWidget(self.leFile2)
        self.pbFile2 = QtWidgets.QPushButton(self)
        self.pbFile2.setObjectName("rbFile2")
        self.pbFile2.clicked.connect(lambda: self.pbOpenFile(self.leFile2))
        self.horizontalLayout_5.addWidget(self.pbFile2)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        # self.browser = QtWidgets.QTextBrowser(self.centralwidget)
        # self.browser.setObjectName("browser")
        self.browser = QWebView()
        self.browser.page().setDevToolsPage(self.browser.page())
        self.browser.setObjectName("browser")
        self.browser.setZoomFactor(.75)

        # Create a placeholder widget with a grey background
        self.placeholderWidget = QWidget()
        self.placeholderWidget.setAutoFillBackground(True)
        palette = self.placeholderWidget.palette()
        palette.setColor(self.placeholderWidget.backgroundRole(), QColor("#393a3b"))
        self.placeholderWidget.setPalette(palette)


        self.browser.setVisible(False)
        self.verticalLayout_2.addWidget(self.placeholderWidget)
        self.verticalLayout_2.addWidget(self.browser)

        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.pbDiff = QtWidgets.QPushButton(self)
        self.pbDiff.setObjectName("pbDiff")
        self.pbDiff.clicked.connect(lambda: self.run_diff())
        self.horizontalLayout_4.addWidget(self.pbDiff)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        # MainWindow.setCentralWidget(self.centralwidget)
        self.setLayout(self.verticalLayout)
        self.label.setText( "File 1: ")
        self.pbFile1.setText("Select")
        self.label_2.setText("File 2:")
        self.pbFile2.setText("Select")
        self.pbDiff.setText( "Diff")
        # QtCore.QMetaObject.connectSlotsByName(MainWindow)



    def notify(self, message, info):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    def pbOpenFile(self, le_to_update):
        fd = QtWidgets.QFileDialog()
        options = fd.options()

        file_name, _ = fd.getOpenFileName(fd, "Open File", "./", "Text (*.txt);;All Files(*)",options=options)
        le_to_update.setText(file_name)

    def run_diff(self):
        print("diffing via python")
        file1_content = None
        file2_content = None
        try:
            fh1 = open(str(self.leFile1.text()), "r")
            file1_content = fh1.read()
        except Exception as e:
            self.notify("File 1 Error", f"error reading file 1\nError: {e}")

        try:
            fh2 = open(str(self.leFile2.text()), "r")
            file2_content = fh2.read()
        except Exception as e:
            self.notify("File 2 Error", f"error reading file 2\nError: {e}")

        try:
            delta = difflib.HtmlDiff(wrapcolumn=80).make_file(
                file1_content.splitlines(), file2_content.splitlines(), "File 1", "File 2"
            )

            # Create a BeautifulSoup object to parse the HTML
            soup = BeautifulSoup(delta, 'html.parser')

            # Define the new CSS style
            new_style = """
                body {
                    background-color: #333;
                    color: #fff;
                }
                table.diff {
                    font-family: Courier;
                    border: medium;
                    background-color: #333;
                    color: #fff;
                }
                .diff_header {
                    background-color: #444;
                    color: #fff;
                    text-align: right;
                }
                .diff_next {
                    background-color: #555;
                    color: #fff;
                }
                .diff_add {
                    background-color: #006400;
                    color: #fff;
                }
                .diff_chg {
                    background-color: #8B6508;
                    color: #fff;
                }
                .diff_sub {
                    background-color: #8B0000;
                    color: #fff;
                }
            """

            # Find the existing style tag and replace its content with the new style
            style_tag = soup.find('style', type='text/css')
            if style_tag:
                style_tag.string = new_style

            # Get the updated HTML content
            delta = str(soup)

            fhd = open("last_diff.html", "w")
            fhd.write(delta)
            fhd.close()
            self.browser.setHtml(delta)
            self.placeholderWidget.setVisible(False)
            self.browser.setVisible(True)
        except Exception as e:
            self.notify("Error in Difflib", f"Error Diffing Files\nError: {e}")



if __name__ == "__main__":
    # --webEngineArgs - -remote - debugging - port = 9222
    print(f"Debug webengine here: http://127.0.0.1:9222/")
    import sys
    # from qt_material import apply_stylesheet

    app = QtWidgets.QApplication(sys.argv)
    # if 'none' not in usettings['window_settings']['ttp_theme']:
    #     apply_stylesheet(app, theme=usettings['window_settings']['ttp_theme'])
    app.setStyle("fusion")
    MainWindow = QtWidgets.QMainWindow()
    ui = UI_Diff()
    # ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
