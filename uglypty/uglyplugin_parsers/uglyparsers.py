from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QStyleFactory
from uglypty.Library.parser_examples import p_examples
from ttp import ttp
from jinja2 import Template
import yaml
import json
import jmespath
from uglypty.uglyplugin_parsers.HighlighterTEWidget import SyntaxHighlighter

class UglyParsingWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UglyParsingWidget, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.mode = "Mode"

        self.resize(1000, 600)
        self.setObjectName("parsers")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self)
        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.verticalLayout_5.addWidget(self.splitter)

        self.verticalLayoutWidget = QtWidgets.QWidget(self.splitter)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.teSource = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.teSource.setObjectName("teSource")
        self.verticalLayout.addWidget(self.teSource)

        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)

        self.teTemplate = QtWidgets.QTextEdit(self.verticalLayoutWidget)
        self.teTemplate.setObjectName("teTemplate")
        self.verticalLayout.addWidget(self.teTemplate)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.pbRender = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pbRender.setObjectName("pbRender")
        self.pbRender.clicked.connect(lambda: self.render(self.mode))
        self.horizontalLayout.addWidget(self.pbRender)

        self.pbClear = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pbClear.setObjectName("pbClear")
        self.pbClear.clicked.connect(lambda: self.clear())
        self.horizontalLayout.addWidget(self.pbClear)

        self.pbExample = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.pbExample.clicked.connect(lambda: self.loadExample(self.mode))
        self.pbExample.setObjectName("pbExample")
        self.horizontalLayout.addWidget(self.pbExample)

        self.modeComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.modeComboBox.setObjectName("comboBox")
        self.modeComboBox.addItem("")
        self.modeComboBox.addItem("")
        self.modeComboBox.addItem("")
        self.modeComboBox.addItem("")
        self.modeComboBox.currentIndexChanged.connect(self.modeComboBoxChanged)
        self.horizontalLayout.addWidget(self.modeComboBox)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.splitter)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)

        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_4.addWidget(self.label_3)

        self.teResult = QtWidgets.QTextEdit(self.verticalLayoutWidget_2)
        self.teResult.setObjectName("teResult")
        self.verticalLayout_4.addWidget(self.teResult)

        self.highlighterComboBox = QtWidgets.QComboBox(self.verticalLayoutWidget)
        self.highlighterComboBox.setObjectName("highlighterComboBox")
        self.highlighterComboBox.addItem("No Highlighter")
        self.highlighterComboBox.addItem("JSON Highlighter")
        self.highlighterComboBox.addItem("Cisco Highlighter")
        self.highlighterComboBox.addItem("Ansible Highlighter")
        self.highlighterComboBox.currentIndexChanged.connect(self.highlighterComboBoxChanged)
        self.verticalLayout_4.addWidget(self.highlighterComboBox)


        self.modeComboBox.setCurrentIndex(0)
        self.source_highlighter = SyntaxHighlighter(self.teSource.document())
        self.template_highlighter = SyntaxHighlighter(self.teTemplate.document())
        self.result_highlighter = SyntaxHighlighter(self.teResult.document())

        self.modeComboBox.currentIndexChanged.connect(self.modeComboBoxChanged)
        QtCore.QMetaObject.connectSlotsByName(self)

        _translate = QtCore.QCoreApplication.translate
        # MainWindow.setWindowTitle(_translate("MainWindow", "Ugly Parsing"))
        # self.setWindowTitle("Ugly Parsing")
        self.label.setText(_translate("parsers", "Source"))
        self.label_2.setText(_translate("parsers", "Template"))
        self.pbRender.setText(_translate("parsers", "Render"))
        self.pbClear.setText(_translate("parsers", "Clear"))
        self.pbExample.setText(_translate("parsers", "Example"))
        self.modeComboBox.setItemText(0, _translate("parsers", "Mode"))
        self.modeComboBox.setItemText(1, _translate("parsers", "TTP"))
        self.modeComboBox.setItemText(2, _translate("parsers", "Jinja2"))
        self.modeComboBox.setItemText(3, _translate("parsers", "JMesPath"))
        self.label_3.setText(_translate("parsers", "Result"))


    def highlighterComboBoxChanged(self, index):
        # Remove any existing highlighter
        if hasattr(self, "highlighter"):
            self.highlighter.setDocument(None)
            del self.highlighter

        # Add the selected highlighter
        self.highlighter = SyntaxHighlighter(self.teResult.document())
        if index == 1:  # Keywords Highlighter
            self.highlighter.set_syntax_type("json")
            # self.highlighter.load_keywords_from_file("./keywords/cisco_keywords.txt")
        elif index == 2:  # Strings Highlighter
            self.highlighter.set_syntax_type("keyword")
            self.highlighter.load_keywords_from_file("./keywords/cisco_keywords.txt")
        elif index == 2:  # Strings Highlighter
            self.highlighter.set_syntax_type("keyword")
            self.highlighter.load_keywords_from_file("./keywords/ansible_keywords.txt")



    def clear(self):
        self.teResult.clear()


    def modeComboBoxChanged(self, index):
        # Get the selected mode
        # if self.mode != "Mode":
        #     MainWindow.setWindowTitle(f"Ugly Parsing - {self.mode}")
        # else:
        #     MainWindow.setWindowTitle(f"Ugly Parsing")

        print(f"Mode before change: {self.mode}")
        self.mode = self.modeComboBox.currentText()
        print(f"Selected Index: {self.modeComboBox.currentText()}")
        if self.mode == "TTP":
            self.source_highlighter.set_syntax_type("jinja")
            self.template_highlighter.set_syntax_type("jinja")
            self.result_highlighter.set_syntax_type("json")
        elif self.mode == "Jinja2":
            self.source_highlighter.set_syntax_type("yaml")
            self.template_highlighter.set_syntax_type("jinja")
            self.result_highlighter.set_syntax_type("json")
        elif self.mode == "JMesPath":
            self.source_highlighter.set_syntax_type("json")
            self.template_highlighter.set_syntax_type("json")
            self.result_highlighter.set_syntax_type("json")

    def loadExample(self, mode):
        if mode != "Mode":
            print(f"Loading Example for Mode: {mode}")

            self.teSource.setText(p_examples[mode]['teSource'])
            self.teTemplate.setText(p_examples[mode]['teTemplate'])
        else:
            self.notify("Select Mode", "Please select a mode first ... TTP, Jinja etc")

    def notify(self, message, info):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        msg.setText(info)
        msg.setWindowTitle(message)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        retval = msg.exec()

    def render(self, mode):
        if mode == "Mode":
            self.notify("Select Mode", "Please select a mode first ... TTP, Jinja etc")

        if mode == "TTP":
            self.render_ttp()

        if mode == "Jinja2":
            self.render_jinja()

        if mode == "JMesPath":
            self.render_jpath()

    def render_jpath(self):
        print("JMesPath")
        parsed_output = ""
        try:
            parsed_output = json.loads(self.teSource.toPlainText())  # Load into dictionary
        except Exception as e:
            self.teResult.setText(f"Error loading json source")

        jp_qry = self.teTemplate.toPlainText()  # example query
        output_dict = {}
        try:
            outputdict = jmespath.search(jp_qry, parsed_output)  # run the query, output is a dictionary
        except Exception as e:
            # self.teResult.setText(f"Error Rendering JMesPath: {e}")
            outputdict = jmespath.search("[]", parsed_output)  # run the query, output is a dictionary
        try:
            result = json.dumps(outputdict, indent=2)  # Strip the outer list object
            self.teResult.setText(result)
        except Exception as e:
            self.teResult.setText(f"Error Rendering JMesPath JSON: {e}")



    def render_jinja(self):
        try:
            print("rendering jinja/json")
            config_dict = yaml.safe_load(self.teSource.toPlainText())
            template_text = self.teTemplate.toPlainText()
            jinja_template = Template(template_text)

            result = jinja_template.render(config_dict)
            self.teResult.setPlainText(result)
            print(result)
        except yaml.parser.ParserError as err:
            self.teResult.setPlainText(f"YAML Error: Parsing Erro: {err}")
            print(f"Yaml Parser Error: {err}")
        except Exception as e:
            self.teResult.setPlainText(str(e))

    def render_ttp(self):
        data_to_parse = self.teSource.toPlainText()
        ttp_template = self.teTemplate.toPlainText()

        try:
            parser = ttp(data=data_to_parse, template=ttp_template)
            parser.parse()
            result = parser.result(format='json')[0]
            self.teResult.setPlainText(result)

        except Exception as e:
            if "index out of range" in str(e):
                print(f"No Data?")
                e = str(e) + " ... No Data?"
            self.teResult.setPlainText(f"Error Parsing Via TTP: {e}")

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    MainWindow = QtWidgets.QMainWindow()
    ui = UglyParsingWidget()
    MainWindow.setCentralWidget(ui)  # Set the widget as the central widget
    MainWindow.show()
    sys.exit(app.exec())
