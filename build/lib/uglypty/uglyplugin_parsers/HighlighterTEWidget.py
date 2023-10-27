import re
from PyQt6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter
from PyQt6.QtCore import Qt

class SyntaxHighlighter(QSyntaxHighlighter):

    def __init__(self, document):
        QSyntaxHighlighter.__init__(self, document)

        # Keywords
        self.keywords = []
        self.syntax_type = None  # Added syntax type attribute

    def load_keywords_from_file(self, file_path):
        with open(file_path, 'r') as file:
            self.keywords = [line.strip() for line in file]

    def set_syntax_type(self, syntax_type):  # Added setter for syntax type
        self.syntax_type = syntax_type

    def highlightBlock(self, text):
        if self.syntax_type == "keyword":
            self.highlight_keywords(text)
        elif self.syntax_type == "yaml":
            self.highlight_yaml(text)
        elif self.syntax_type == "json":
            self.highlight_json(text)
        elif self.syntax_type == "jinja":
            self.highlight_jinja(text)

    def highlight_keywords(self, text):
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        format.setForeground(Qt.GlobalColor.darkMagenta)

        for keyword in self.keywords:
            pattern = f"\\b{keyword}\\b"
            self.highlight_pattern(text, pattern, format)

    def highlight_yaml(self, text):
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        format.setForeground(Qt.GlobalColor.green)
        pattern = r"\b[a-zA-Z_][a-zA-Z0-9_]*\b(?=\s*:)"  # Match keys before colon
        self.highlight_pattern(text, pattern, format)

    def highlight_json(self, text):
        format = QTextCharFormat()
        format.setFontWeight(QFont.Weight.Bold)
        format.setForeground(Qt.GlobalColor.yellow)
        pattern = r"\".*?\": "  # Match key-value pair structure of JSON
        self.highlight_pattern(text, pattern, format)

    def highlight_jinja(self, text):
        format1 = QTextCharFormat()
        format1.setFontWeight(QFont.Weight.Bold)
        format1.setForeground(Qt.GlobalColor.darkCyan)
        format1.setUnderlineStyle(QTextCharFormat.UnderlineStyle.SingleUnderline)
        pattern1 = r"\{\{.*?\}\}"  # Match Jinja2-style variable syntax
        self.highlight_pattern(text, pattern1, format1)

        format2 = QTextCharFormat()
        format2.setFontWeight(QFont.Weight.Bold)
        format2.setForeground(Qt.GlobalColor.green)
        pattern2 = r"\{%\s*for.*?%\}"  # Match Jinja2-style for loop syntax
        self.highlight_pattern(text, pattern2, format2)

        format3 = QTextCharFormat()
        format3.setFontWeight(QFont.Weight.Bold)
        format3.setForeground(Qt.GlobalColor.blue)
        pattern3 = r"\{%\s*(if|elif|else).*?%\}"  # Match Jinja2-style if/elif/else syntax
        self.highlight_pattern(text, pattern3, format3)

        format4 = QTextCharFormat()
        format4.setFontWeight(QFont.Weight.Bold)
        format4.setForeground(Qt.GlobalColor.green)
        pattern4 = r"\{%\s*end(for|if).*?%\}"  # Match Jinja2-style endfor/endif syntax
        self.highlight_pattern(text, pattern4, format4)

    def highlight_pattern(self, text, pattern, format):
        expression = re.compile(pattern)
        index = expression.search(text)

        while index:
            start, end = index.span()
            length = end - start
            self.setFormat(start, length, format)
            index = expression.search(text, start + length)

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication, QTextEdit

    app = QApplication(sys.argv)

    text_edit = QTextEdit()
    highlighter = SyntaxHighlighter(text_edit.document())
    highlighter.set_syntax_type("jinja")
    text_edit.show()

    sys.exit(app.exec())
