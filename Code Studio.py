import sys
import builtins
import webbrowser
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QFileDialog, QAction, QPushButton, QLineEdit, QLabel, QComboBox, QDialog, QToolBar, QShortcut, QInputDialog, QColorDialog, QScrollArea
from PyQt5.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter, QFont, QKeySequence


class OutputRedirector:
    def __init__(self, text_edit_widget: QTextEdit):
        self.text_edit_widget = text_edit_widget

    def write(self, text: str):
        """Redirect text output to the output widget (console)."""
        cursor = self.text_edit_widget.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.text_edit_widget.setTextCursor(cursor)

    def flush(self):
        """Flush the output (no-op for this use case)."""
        pass


class SyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, language="python"):
        super(SyntaxHighlighter, self).__init__(parent)
        self.language = language
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(255, 0, 0))
        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(0, 255, 0))
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(128, 128, 128))
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(0, 255, 255))
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(255, 255, 0))

        if self.language == "python":
            self.keywords = QRegExp(r'\b(?:def|class|if|else|elif|for|while|return|import|from|try|except|finally)\b')
            self.functions = QRegExp(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?=\()')
            self.comments = QRegExp(r'#.*')
            self.strings = QRegExp(r'".*?"|\'.*?\'')
            self.numbers = QRegExp(r'\b\d+\b')
        elif self.language == "cpp":
            self.keywords = QRegExp(r'\b(?:int|float|double|char|if|else|while|for|return|class|public|private|protected|void|new|delete)\b')
            self.functions = QRegExp(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?=\()')
            self.comments = QRegExp(r'//.*|/\*.*?\*/')
            self.strings = QRegExp(r'".*?"|\'.*?\'')
            self.numbers = QRegExp(r'\b\d+\b')
        elif self.language == "csharp":
            self.keywords = QRegExp(r'\b(?:int|float|double|string|bool|if|else|while|for|return|class|public|private|protected|void|new)\b')
            self.functions = QRegExp(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?=\()')
            self.comments = QRegExp(r'//.*|/\*.*?\*/')
            self.strings = QRegExp(r'".*?"|\'.*?\'')
            self.numbers = QRegExp(r'\b\d+\b')

    def highlightBlock(self, text):
        self.highlight_text(self.keywords, self.keyword_format, text)
        self.highlight_text(self.functions, self.function_format, text)
        self.highlight_text(self.comments, self.comment_format, text)
        self.highlight_text(self.strings, self.string_format, text)
        self.highlight_text(self.numbers, self.number_format, text)

    def highlight_text(self, regex, format, text):
        index = regex.indexIn(text)
        while index >= 0:
            length = regex.matchedLength()
            self.setFormat(index, length, format)
            index = regex.indexIn(text, index + length)


class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Code Studio")
        self.setGeometry(100, 100, 800, 600)

        # Create widgets
        self.editor_widget = QTextEdit(self)
        self.editor_widget.setFont(QFont("Courier", 10))

        self.output_widget = QTextEdit(self)
        self.output_widget.setFont(QFont("Courier", 10))
        self.output_widget.setStyleSheet("background-color: black; color: green;")
        self.output_widget.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.editor_widget)
        layout.addWidget(self.output_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Redirect output to console (output_widget)
        self.output_redirector = OutputRedirector(self.output_widget)
        sys.stdout = self.output_redirector  
        sys.stderr = self.output_redirector 

        # Set up toolbar
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Run button
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.run_code)
        self.toolbar.addWidget(self.run_button)

        # Save button
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_file)
        self.toolbar.addWidget(self.save_button)

        # Language selector
        self.language_selector = QComboBox(self)
        self.language_selector.addItems(["Python","HTML"])  
        self.language_selector.currentIndexChanged.connect(self.change_language)
        self.toolbar.addWidget(self.language_selector)

        # Language label
        self.language_label = QLabel("Language: Python", self)
        self.toolbar.addWidget(self.language_label)

        # Info button
        self.info_button = QPushButton("Info", self)
        self.info_button.clicked.connect(self.show_info)
        self.toolbar.addWidget(self.info_button)

        # Debug button
        self.debug_button = QPushButton("Debug", self)
        self.debug_button.clicked.connect(self.show_debug)
        self.toolbar.addWidget(self.debug_button)

        self.language = "python"
        self.setup_shortcuts()

        # Theme options
        themes_menu = self.menuBar().addMenu("Themes")

        default_action = QAction("Default", self)
        default_action.triggered.connect(self.set_default_theme)
        themes_menu.addAction(default_action)

        dark_blue_action = QAction("Dark Blue", self)
        dark_blue_action.triggered.connect(self.set_dark_blue_theme)
        themes_menu.addAction(dark_blue_action)

        dark_red_action = QAction("Dark Red", self)
        dark_red_action.triggered.connect(self.set_dark_red_theme)
        themes_menu.addAction(dark_red_action)

        light_gray_action = QAction("Light Gray", self)
        light_gray_action.triggered.connect(self.set_light_gray_theme)
        themes_menu.addAction(light_gray_action)

        solarized_dark_action = QAction("Solarized Dark", self)
        solarized_dark_action.triggered.connect(self.set_solarized_dark_theme)
        themes_menu.addAction(solarized_dark_action)

        solarized_light_action = QAction("Solarized Light", self)
        solarized_light_action.triggered.connect(self.set_solarized_light_theme)
        themes_menu.addAction(solarized_light_action)

        self.set_default_theme()

        # Initialize syntax highlighter
        self.highlighter = SyntaxHighlighter(self.editor_widget.document(), self.language)

    def set_default_theme(self):
        self.setStyleSheet("background-color: #2e2e2e;")  
        self.editor_widget.setStyleSheet(""" 
            background-color: #2e2e2e; 
            color: white;
        """)
        self.output_widget.setStyleSheet(""" 
            background-color: #000000; 
            color: #00ff00;
        """)

    def set_dark_blue_theme(self):
        self.setStyleSheet("background-color: #001f3d;")  
        self.editor_widget.setStyleSheet(""" 
            background-color: #001f3d; 
            color: #a0c1d1;
        """)
        self.output_widget.setStyleSheet(""" 
            background-color: #000000; 
            color: #00ff00;
        """)

    def set_dark_red_theme(self):
        self.setStyleSheet("background-color: #3e0b00;")  
        self.editor_widget.setStyleSheet(""" 
            background-color: #3e0b00; 
            color: #ff4040;
        """)
        self.output_widget.setStyleSheet(""" 
            background-color: #000000; 
            color: #ff8080;
        """)

    def set_light_gray_theme(self):
        self.setStyleSheet("background-color: #dcdcdc;")  
        self.editor_widget.setStyleSheet(""" 
            background-color: #dcdcdc; 
            color: black;
        """)
        self.output_widget.setStyleSheet(""" 
            background-color: #f0f0f0; 
            color: black;
        """)

    def set_solarized_dark_theme(self):
        self.setStyleSheet("background-color: #002b36;")  
        self.editor_widget.setStyleSheet(""" 
            background-color: #002b36; 
            color: #839496;
        """)
        self.output_widget.setStyleSheet(""" 
            background-color: #000000; 
            color: #93a1a1;
        """)

    def set_solarized_light_theme(self):
        self.setStyleSheet("background-color: #fdf6e3;")  
        self.editor_widget.setStyleSheet(""" 
            background-color: #fdf6e3; 
            color: #657b83;
        """)
        self.output_widget.setStyleSheet(""" 
            background-color: #f0f0f0; 
            color: #586e75;
        """)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;HTML Files (*.html);;All Files (*)")
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.editor_widget.toPlainText())

    def run_code(self):
        """Execute the code in the editor."""
        code = self.editor_widget.toPlainText()
        if self.language == 'html':
            # Save HTML to a temporary file
            with open('temp_preview.html', 'w') as f:
                f.write(code)
            # Open the file in the default web browser
            webbrowser.open('temp_preview.html')
        else:
            if 'discord' in code:
                self.output_widget.append("https://discord.gg/H6JvfVNS")
            elif 'TheVrEnthusiast' in code:
                self.output_widget.append("https://www.youtube.com/channel/UCNmQ6yNgwT0KsL8oQgA656g")
            else:
                try:
                    def safe_input(prompt):
                        user_input, ok = QInputDialog.getText(self, "Input", prompt)
                        return user_input if ok else ""

                    builtins.input = safe_input  # Redirect input to QInputDialog
                    exec(code)
                except Exception as e:
                    self.output_widget.append(f"Error executing code: {e}")

    def change_language(self):
        """Change the language for syntax highlighting."""
        self.language = self.language_selector.currentText().lower()
        self.language_label.setText(f"Language: {self.language.capitalize()}")
        self.highlighter.language = self.language
        self.highlighter.rehighlight()

    def setup_shortcuts(self):
        """Set up keyboard shortcuts."""
        self.run_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.run_shortcut.activated.connect(self.run_code)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_file)

        self.quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.quit_shortcut.activated.connect(self.close)

    def show_info(self):
        info_dialog = QDialog(self)
        info_layout = QVBoxLayout(info_dialog)
        info_label = QLabel(""" 
     Code Studio v0.1.0
            developed by: Analog Algorithm Studios

            Supported Languages:
            - Python
            - HTML
            -C# AND C++ REMOVED.

            Shortcuts:
            - Ctrl+S: Save file
            - Ctrl+R: Run code
            - Ctrl+Q: Close application

            Themes:
            - Default (Dark)
            - Dark Blue
            - Dark Red
            - Light Gray
            - Solarized Dark
            - Solarized Light

            Enjoy coding!
        """, info_dialog)
        info_layout.addWidget(info_label)

        info_dialog.setWindowTitle("About Code Studio")
        info_dialog.exec_()

    def show_debug(self):
        """Show the debug dialog with installation instructions and backend code."""
        debug_dialog = QDialog(self)
        debug_layout = QVBoxLayout(debug_dialog)

        debug_label = QLabel(""" 
            To install Python packages using pip, open a terminal or command prompt and run:
            
            pip install <package-name>

            Example:
            pip install PyExample
            
            Backend Code:
            This is the current backend code running in the editor.
            """, debug_dialog)
        debug_layout.addWidget(debug_label)

        scroll_area = QScrollArea(debug_dialog)
        backend_code = QTextEdit(debug_dialog)
        backend_code.setText(self.editor_widget.toPlainText())
        backend_code.setReadOnly(True)
        backend_code.setFont(QFont("Courier", 10))
        scroll_area.setWidget(backend_code)
        debug_layout.addWidget(scroll_area)

        debug_dialog.setWindowTitle("Debug Information")
        debug_dialog.resize(600, 400)
        debug_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeEditor()
    window.show()
    sys.exit(app.exec_())