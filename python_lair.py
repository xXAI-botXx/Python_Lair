from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor, QTextCursor, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize, QEvent
from PyQt5 import QtGui
import sys
import code_ex

class WriteBlock(QTextEdit):
    ID = 0

    def __init__(self, txt="", parent=None):
        super().__init__(txt, parent)
        txt  = "\n"+txt
        self.setPlainText(txt)
        self.parent = parent
        self.id_ = WriteBlock.ID
        WriteBlock.ID += 1
        self.history = ["\n"]
        #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.size = 150
        self.resize_block()
        self.setMinimumWidth(800)
        self.setMaximumWidth(800)
        self.setMaximumHeight(self.size)
        self.setMinimumHeight(self.size)
        self.setStyleSheet("""
                            QTextEdit
                            {
                            background-color:white;
                            font: 75 11pt \'MS Shell Dlg 2\';
                            color:black;
                            border-style: none;
                            }
                            QTextEdit:focus
                            {
                            border-style:solid;
                            border-width:2px;
                            border-color:black;
                            }
                            /*QTextEdit:hover
                            {
                            border-style:solid;
                            border-width:2px;
                            border-color:black;
                            }*/""")

    def keyPressEvent(self, e):
        #print(e.key())
        self.check_line_0()
        should_not_run = (16777237, 16777235, 16777217, 16777249, 67)
        if not(e.key() in should_not_run):
            super(WriteBlock, self).keyPressEvent(e)
        if e.key() == 16777220: # enter
            self.resize_block()
        elif e.key() == 16777219: # back
            if self.textCursor().position() == 0:
                self.insertPlainText("\n")
                c = self.textCursor()
                c.setPosition(1)
                self.setTextCursor(c)
            self.resize_block()
        elif e.key() == 16777237: # pfeil unten
            c = self.textCursor()
            old_pos = c.position()
            super(WriteBlock, self).keyPressEvent(e)
            c_new = self.textCursor()
            new_pos = c_new.position()
            if new_pos == old_pos:
                c.movePosition(QTextCursor.EndOfLine)
                self.setTextCursor(c)
            self.check_line_0()
        elif e.key() == 16777235: # pfeil oben
            super(WriteBlock, self).keyPressEvent(e)
            self.check_line_0()
        elif e.key() == 86 and Qt.ControlModifier: # strg + v
            self.check_line_0()
            self.resize_block()
        elif e.key() == 90 and Qt.ControlModifier: # strg + z
            self.step_back()
            self.resize_block()
            self.check_line_0()
        elif e.key() == 67: # c
            s_txt = self.textCursor().selectedText()
            if len(s_txt) != 0:
                self.get_app().clipboard().setText(s_txt)
            else:
                super().keyPressEvent(e)
        elif e.key() == 16777217:   # Tab
            self.insertPlainText("    ")

        # Pfeiltasten
        if e.key() not in (16777235, 16777237, 16777234, 16777236):
            self.coloring()
            self.add_to_history()

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.check_line_0()

    def mouseRealeaseEvent(self, e):
        super().mouseReleaseEvent
        self.check_line_0()
    
    def insertFromMimeData(self, event):
        super().insertFromMimeData(event)
        self.resize_block()
        self.check_line_0()
        self.coloring()

    def show_event(self, e):
        self.resize_block()

    def check_line_0(self):
        if self.textCursor().position() == 0:
            c = self.textCursor()
            c.setPosition(1)
            self.setTextCursor(c)

    def resize_block(self):
        c = self.textCursor()
        c.movePosition(QTextCursor.End)
        n_lines = c.blockNumber()
        self.size = 18*n_lines+35
        self.setMinimumHeight(self.size)
        self.setMaximumHeight(self.size)
        self.parent.set_size(self.size) 
        while self.verticalScrollBar().maximum() != 0:
            self.size += 35
            self.setMinimumHeight(self.size)
            self.setMaximumHeight(self.size)
            self.parent.set_size(self.size)

    def add_to_history(self):
        if len(self.history) == 0:
             self.history += [self.toPlainText()]
        elif self.history[-1] != self.toPlainText():
            self.history += [self.toPlainText()]
            if len(self.history) > 51:
                self.history = self.history[1:]

    def step_back(self):
        c = self.textCursor()
        if len(self.history) > 1:
            self.clear()
            self.history = self.history[0:-1]
            self.setPlainText(self.history[-1])
            self.history = self.history[0:-1]
            self.resize_block()
            c.movePosition(QTextCursor.EndOfLine)
            self.setTextCursor(c)

    def coloring(self):
        cursor_pos = self.textCursor().position()

        txt = self.toPlainText()
        self.clear()

        keys = (" ", ".", "(", ")", "[", "]", "=", "{", "}", "\n", "#")
        new_txt = []
        at_a_word = False
        last_word = ""
        last_important_key = ""
        cache = ""
        for c in txt:
            if at_a_word == False and c in keys:
                cache += c
                if c == "#" or c == "\n":
                    last_important_key = c
            elif at_a_word == False and c not in keys:
                at_a_word = True
                new_txt += [cache]
                self.add_colored_text(cache, last_word, last_important_key)
                cache = c
            elif at_a_word == True and c not in keys:
                cache += c
            elif at_a_word == True and c in keys:
                at_a_word = False
                new_txt += [cache]
                self.add_colored_text(cache, last_word, last_important_key)
                last_word = cache
                if c == "#" or c == "\n":
                    last_important_key = c
                cache = c
        if cache != "":
            new_txt += [cache]
            self.add_colored_text(cache, last_word, last_important_key)
        
        cursor = self.textCursor()
        cursor.setPosition(cursor_pos)
        self.setTextCursor(cursor)

    #ADD and CHANGE COLERING
    def add_colored_text(self, txt, last_word, last_important_key):
        blue = QColor(0,0,255)
        red = QColor(255,0,0)
        light_yellow = QColor(255,185,15)
        green = QColor(0,100,0)
        purple = QColor(139,34,82)
        gray = QColor(66,66,66)

        control_keywords = ("if", "elif", "else:", "return", "yield", "while", "for", "with", "import", "from", "super", "in", "print", "pass", "try:", "except", "except:", "break", "continue")
        oop_keywords = ("class", "def", "self")

        if last_important_key == "#":
            self.setTextColor(green)
        elif txt in control_keywords:
            self.setTextColor(purple)
        elif txt in oop_keywords:
            self.setTextColor(blue)
        elif last_word == "def" or last_word == "class":
            self.setTextColor(light_yellow)
        else:
            self.setTextColor(gray)

        self.insertPlainText(txt)

    def set_read_only(self):
        self.setReadOnly(True)

    def get_code(self):
        txt = "#%%"
        txt += self.toPlainText()
        #txt += "\n"
        txt += "\n#%%"
        return txt

    def get_clean_code(self):
        return self.toPlainText()

    def get_app(self):
        return self.parent.get_app()


class CodeBlock(QWidget):
    def __init__(self, index, parent=None, txt="", many_features=True):
        super().__init__()
        #self.code = CodeSegment()
        #self.block = QTextEdit("moin", self)
        self.block = WriteBlock(txt, self)
        if many_features == False:
            self.block.set_read_only()
        self.parent = parent
        self.many_features = many_features
        self.index = index
        self.run_btn = QPushButton(">", self)
        self.run_btn.setGeometry(5, 4, 40,17)
        self.run_btn.setAutoFillBackground(False)
        self.run_btn.setToolTip("<span style=\"color:white;\">Click me, to <b>run the current Codeblock</b>.</span>")
        self.run_btn.clicked.connect(self.run_btn_clicked)
        self.run_btn.setStyleSheet("""
                                    QPushButton
                                    {
                                    background-color:#445d87;
                                    font: 75 10pt \"MS Shell Dlg 2\";
                                    color:white;
                                    border-style: none;
                                    }
                                    QPushButton:pressed
                                    {
                                    background-color:#424242;
                                    }
                                    QPushButton:hover
                                    {
                                    border-style:solid;
                                    border-width:2px;
                                    border-color:black;
                                    }
                                    """)
        self.run_btn.setVisible(many_features)

        self.del_btn = QPushButton("-", self)
        self.del_btn.setGeometry(600, 4, 40,17)
        self.del_btn.setAutoFillBackground(False)
        self.del_btn.setToolTip("<span style=\"color:white;\">Click me, to <b>delete the current Codeblock</b>.</span>")
        self.del_btn.clicked.connect(self.del_btn_clicked)
        self.del_btn.setStyleSheet("""
                                    QPushButton
                                    {
                                    background-color:#445d87;
                                    font: 75 10pt \"MS Shell Dlg 2\";
                                    color:white;
                                    border-style: none;
                                    }
                                    QPushButton:pressed
                                    {
                                    background-color:#424242;
                                    }
                                    QPushButton:hover
                                    {
                                    border-style:solid;
                                    border-width:2px;
                                    border-color:black;
                                    }
                                    """)

        self.up_btn = QPushButton("^", self)
        self.up_btn.setGeometry(700, 4, 40,17)
        self.up_btn.setAutoFillBackground(False)
        self.up_btn.setToolTip("<span style=\"color:white;\">Click me, to <b>move this Codeblock one up</b>.</span>")
        self.up_btn.clicked.connect(self.up_btn_clicked)
        self.up_btn.setStyleSheet("""
                                    QPushButton
                                    {
                                    background-color:#445d87;
                                    font: 75 10pt \"MS Shell Dlg 2\";
                                    color:white;
                                    border-style: none;
                                    }
                                    QPushButton:pressed
                                    {
                                    background-color:#424242;
                                    }
                                    QPushButton:hover
                                    {
                                    border-style:solid;
                                    border-width:2px;
                                    border-color:black;
                                    }
                                    """)
        self.up_btn.setVisible(many_features)

        self.down_btn = QPushButton("v", self)
        self.down_btn.setGeometry(750, 4, 40,17)
        self.down_btn.setAutoFillBackground(False)
        self.down_btn.setToolTip("<span style=\"color:white;\">Click me, to <b>move this Codeblock one down</b>.</span>")
        self.down_btn.clicked.connect(self.down_btn_clicked)
        self.down_btn.setStyleSheet("""
                                    QPushButton
                                    {
                                    background-color:#445d87;
                                    font: 75 10pt \"MS Shell Dlg 2\";
                                    color:white;
                                    border-style: none;
                                    }
                                    QPushButton:pressed
                                    {
                                    background-color:#424242;
                                    }
                                    QPushButton:hover
                                    {
                                    border-style:solid;
                                    border-width:2px;
                                    border-color:black;
                                    }
                                    """)
        self.down_btn.setVisible(many_features)

        self.step_back_btn = QPushButton("<-", self)
        self.step_back_btn.setGeometry(550, 4, 40,17)
        self.step_back_btn.setAutoFillBackground(False)
        self.step_back_btn.setToolTip("<span style=\"color:white;\">Click me, to <b>take a step back</b>.</span>")
        self.step_back_btn.clicked.connect(self.step_back_btn_clicked)
        self.step_back_btn.setStyleSheet("""
                                    QPushButton
                                    {
                                    background-color:#445d87;
                                    font: 75 10pt \"MS Shell Dlg 2\";
                                    color:white;
                                    border-style: none;
                                    }
                                    QPushButton:pressed
                                    {
                                    background-color:#424242;
                                    }
                                    QPushButton:hover
                                    {
                                    border-style:solid;
                                    border-width:2px;
                                    border-color:black;
                                    }
                                    """)
        self.step_back_btn.setVisible(many_features)

        label = parent.get_block_nr()
        self.nr_label = QLabel(str(label), self)
        self.nr_label.setGeometry(5, 4, 40, 17)
        self.nr_label.setAlignment(Qt.AlignCenter)
        self.nr_label.setStyleSheet("""
                                    QLabel
                                    {
                                    background-color:#445d87;
                                    font: 75 10pt \"MS Shell Dlg 2\";
                                    color:white;
                                    border-style: none;
                                    }
                                    """)
        self.nr_label.setVisible(not(many_features))

    def txt(self):
        txt = self.block.toPlainText()

    def set_size(self, height):
        height = height + 50
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def set_index(self, i:int):
        self.index = i

    def set_parent(self, parent):
        self.setParent(parent)

    def get_code(self):
        return self.block.get_code()

    def get_clean_code(self):
        return self.block.get_clean_code()

    def get_id(self):
        return self.block.id_

    def get_app(self):
        return self.parent.get_app()

    def run_btn_clicked(self, event):
        self.runned_code = self.block.get_code()
        self.parent.run(self.block.id_, self.block.get_code())

    def del_btn_clicked(self, event):
        self.setParent(None)
        self.parent.delete_item(self.index)

    def up_btn_clicked(self, event):
        if self.index > 0:
            self.parent.switch_item(self.index, self.index-1)

    def down_btn_clicked(self, event):
        if self.index < self.parent.get_last_index():
            self.parent.switch_item(self.index, self.index+1)

    def step_back_btn_clicked(self, event):
        self.block.step_back()
        self.block.check_line_0()
        self.block.coloring()
        self.block.add_to_history()

    def coloring(self):
        self.block.coloring()

    def resize(self):
        self.block.resize_block()

class Box(QWidget):
    def __init__(self, parent, window, many_features=True):
        super().__init__()

        self.items = []
        self.window = window
        self.many_features = many_features

        # Add Widgets
        self.scroll_content = QWidget()
        self.layout = QVBoxLayout(self)
        self.scroll_content.setLayout(self.layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.scroll_area.setStyleSheet(""" 
                                QScrollBar:vertical {
                                    /*border: none;*/
                                    background: none;
                                    width: 20px;
                                    margin: 26px 0 26px 0;
                                }

                                QScrollBar::handle:vertical {
                                    background: #bfbfbf;
                                    min-height: 26px;
                                    border-style:solid;
                                    border-radius:8px;
                                    border-width:2px;
                                    border-color:black;
                                }

                                QScrollBar::add-line:vertical {
                                    background: none;
                                    height: 26px;
                                    subcontrol-position: bottom;
                                    subcontrol-origin: margin;
                                }

                                QScrollBar::sub-line:vertical {
                                    background: none;
                                    height: 26px;
                                    subcontrol-position: top left;
                                    subcontrol-origin: margin;
                                    position: absolute;
                                }

                                QScrollBar:up-arrow:vertical, QScrollBar::down-arrow:vertical {
                                    width: 26px;
                                    height: 26px;
                                    background: none;
                                }

                                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                                    background: none;
                                }""")
        
        parent.addWidget(self.scroll_area)

    def get_last_index(self) -> int:
        return len(self.items)-1

    def add_item(self, item:QWidget, txt="", inverse=False, coloring=False):
        item = item(len(self.items), self, txt, self.many_features)
        self.items += [item]
        self.layout.addWidget(item)
        if inverse == True:
            index = len(self.items)-1
            for i in range(len(self.items)-2, -1, -1):
                self.switch_item(index, i)
                index -= 1
        if coloring == True:
            item.coloring()
        item.resize()

    def insert_item(self, item:QWidget, index=None):
        if index == None:
            index = self.layout.count()-1
        self.items.insert(index, item)
        self.layout.insertWidget(index, item)

    def delete_item(self, index):
        new_items = self.items[0:index]
        counter = 0
        for i in self.items[index:]:
            if counter == 0:
                counter += 1
            else:
                new_items += [i]
                index = len(new_items)-1
                i.set_index(index)
        self.items = new_items
            
    def switch_item(self, from_:int, to_:int):
        self.items[from_].set_index(to_)
        self.items[to_].set_index(from_)
        self.items[from_], self.items[to_] =  self.items[to_], self.items[from_]
        for i in self.items:
            i.set_parent(None)

        for i in self.items:
            i.set_parent(self)
            self.layout.addWidget(i)

    def clear(self):
        for i in self.items:
            i.set_parent(None)
        self.items = []

    def get_code(self):
        code = ""
        for i, x in enumerate(self.items):
            if i > 0: code += "\n"
            code += x.get_code()
        return code

    def get_clean_code(self):
        code = ""
        for i, x in enumerate(self.items):
            if i > 0: code += "\n"
            code += x.get_clean_code()
        return code[1:]

    def get_output(self):
        output = ""
        for i, x in enumerate(self.items):
            if i > 0: 
                output += "\n"
            else:
                output += "----------------\n"
            code = x.get_clean_code()
            if code[:1] == "\n":
                output += code[1:]
            else:
                output += code
            output += "\n----------------"
        return output

    def get_items(self):
        return self.items

    def get_block_nr(self) -> int:
        return self.layout.count()

    def get_app(self):
        return self.window.get_app()

    def run(self, id_:int, code:str):
        self.window.run(id_, code)
    
    def resize(self):
        for item in self.items:
            item.resize()

class Window(QWidget):
    def __init__(self, app:QApplication):
        super().__init__()

        # XXX Window Settings XXX
        self.setWindowTitle("Python Lair - a Python IDE")
        self.setWindowIcon(QtGui.QIcon("logo_blue_big.png"))
        self.setStyleSheet("baclground-color:#424242")
        self.setGeometry(0,0,1920, 1080)
        self.setStyleSheet("background-color:#424242")

        self.app = app
        self.save_place = None
        self.code = code_ex.Code_Executer()

        # XXX add Widgets XXX
        self.auto_saver = QTimer(self)
        self.auto_saver.setInterval(30000)    # 30 Sekunden
        self.auto_saver.timeout.connect(self.auto_saving)
        self.auto_saver.stop()
        self.resize_timer = QTimer(self)
        self.resize_timer.setInterval(5) 
        self.resize_timer.timeout.connect(self.resize_event)
        self.resize_timer.stop()
        self.should_auto_saving = False

        self.font = QFont()
        self.font.setFamily(u"MS Shell Dlg 2")
        self.font.setPointSize(14)
        self.font.setBold(False)
        self.font.setItalic(False)
        self.font.setWeight(9)
        self.font.setKerning(True)
        self.font.setStyleStrategy(QFont.PreferAntialias)

        # Input Field
        self.input_area = QFrame(self)
        self.input_area.setGeometry(30, 70, 871, 921)
        self.input_area.setStyleSheet(u"background-color:#445d87;\n"
                                        "border-style:solid;\n"
                                        "border-radius:8px;\n"
                                        "/*border-width:5px;*/\n"
                                        "border-color:black;\n"
                                        "")
        self.input_area_layout = QVBoxLayout(self.input_area)
        #self.input_area_layout.setGeometry(0, 0, 871, 921)
        self.input_box = Box(self.input_area_layout, self)
        #self.input_box.setGeometry(30, 30, 500, 700)

        # Output Field
        self.output_area = QFrame(self)
        self.output_area.setGeometry(1020, 70, 871, 921)
        self.output_area.setStyleSheet(u"background-color:#445d87;\n"
                                        "border-style:solid;\n"
                                        "border-radius:8px;\n"
                                        "/*border-width:5px;*/\n"
                                        "border-color:black;\n"
                                        "")
        self.output_area_layout = QVBoxLayout(self.output_area)
        #self.output_area_layout.setGeometry(0, 0, 871, 921)
        self.output_box = Box(self.output_area_layout, self, False)
        #self.output_box.setGeometry(30, 30, 500, 700)

        # Buttons
        self.add_btn = QPushButton("+", self)
        self.add_btn.setGeometry(175, 40, 81, 31)
        self.add_btn.setFont(self.font)
        self.add_btn.setAutoFillBackground(False)
        self.add_btn.setToolTip("Click me, to <b>add another Codeblock</b>.")
        self.add_btn.clicked.connect(self.clicked_add_btn)
        self.add_btn.setStyleSheet(u"QPushButton\n"
                                    "{\n"
                                    "background-color:#445d87;\n"
                                    "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                    "color:white;\n"
                                    "border-style: none;\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton::pressed\n"
                                    "{\n"
                                    "background-color:#424242;\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton:hover\n"
                                    "{\n"
                                    "border-style:solid;\n"
                                    "border-width:2px;\n"
                                    "border-color:black;\n"
                                    "}\n"
                                    "")

        self.del_btn = QPushButton("-", self)
        self.del_btn.setGeometry(265, 40, 81, 31)
        self.del_btn.setFont(self.font)
        self.del_btn.setAutoFillBackground(False)
        self.del_btn.setToolTip("Click me, to <b>delete all Codeblocks</b>.<br><br>Attention: You cant bring back these Codeblocks!")
        self.del_btn.clicked.connect(self.clicked_del_btn)
        self.del_btn.setStyleSheet(u"QPushButton\n"
                                    "{\n"
                                    "background-color:#445d87;\n"
                                    "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                    "color:white;\n"
                                    "border-style: none;\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton::pressed\n"
                                    "{\n"
                                    "background-color:#424242;\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton:hover\n"
                                    "{\n"
                                    "border-style:solid;\n"
                                    "border-width:2px;\n"
                                    "border-color:black;\n"
                                    "}\n"
                                    "")

        self.play_btn = QPushButton(">", self)
        self.play_btn.setGeometry(55, 40, 81, 31)
        self.play_btn.setFont(self.font)
        self.play_btn.setAutoFillBackground(False)
        self.play_btn.setToolTip("Click me, to <b>run your complete code</b>.")
        self.play_btn.clicked.connect(self.clicked_play_btn)
        self.play_btn.setStyleSheet(u"QPushButton\n"
                                    "{\n"
                                    "background-color:#445d87;\n"
                                    "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                    "color:white;\n"
                                    "border-style: none;\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton::pressed\n"
                                    "{\n"
                                    "background-color:#424242;\n"
                                    "}\n"
                                    "\n"
                                    "QPushButton:hover\n"
                                    "{\n"
                                    "border-style:solid;\n"
                                    "border-width:2px;\n"
                                    "border-color:black;\n"
                                    "}\n"
                                    "")

        self.export_btn = QPushButton(">>", self)
        self.export_btn.setGeometry(785, 40, 81, 31)
        self.export_btn.setFont(self.font)
        self.export_btn.setAutoFillBackground(False)
        self.export_btn.setToolTip("Click me, to <b>export your Python code</b> as a clean Python file.<br><br>\
                                    Note:<br>In that form, you can't import that code in future as more than one block.<br>\
                                    To import your code in future in more than one block, you have to use the \"s\"-Button or<br>\"s as\"-Button.")
        self.export_btn.clicked.connect(self.clicked_export_btn)
        self.export_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")
                            
        self.import_btn = QPushButton("<<", self)
        self.import_btn.setGeometry(695, 40, 81, 31)
        self.import_btn.setFont(self.font)
        self.import_btn.setAutoFillBackground(False)
        self.import_btn.setToolTip("Click me, to <b>add/import another Python file</b>.<br>Not the Python file will be imported, rather the code of this file will be added to the actual Python file.")
        self.import_btn.clicked.connect(self.clicked_import_btn)
        self.import_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        self.save_btn = QPushButton("s", self)
        self.save_btn.setGeometry(480, 40, 81, 31)
        self.save_btn.setFont(self.font)
        self.save_btn.setAutoFillBackground(False)
        self.save_btn.setToolTip("Click me, to <b>save your file</b>.<br><br>If you dont have set an location yet, you going to be ask, where to save the file and then the file going to be saved.")
        self.save_btn.clicked.connect(self.clicked_save_btn)
        self.save_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        self.save_as_btn = QPushButton("s as", self)
        self.save_as_btn.setGeometry(570, 40, 81, 31)
        self.save_as_btn.setFont(self.font)
        self.save_as_btn.setAutoFillBackground(False)
        self.save_as_btn.setToolTip("Click me, to <b>set a location</b> for saving your file.<br><br>I will save your file too.")
        self.save_as_btn.clicked.connect(self.clicked_save_as_btn)
        self.save_as_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        self.auto_save_btn = QPushButton("auto s", self)
        self.auto_save_btn.setGeometry(390, 40, 81, 31)
        self.auto_save_btn.setFont(self.font)
        self.auto_save_btn.setAutoFillBackground(False)
        self.auto_save_btn.setToolTip("With clicking me, you activating or deactiving me.<br> You can see that on my color.\
                                        <br>Deep Blue = Activate<br>Normal Blue = Deactivate<br><br>\
                                        When i'm active and you have set a location to save this file, i will <b>automatically save your file every 30 Seconds</b>.<br><br>\
                                        To set a location for your file, click \"s\"-Button or \"s as\"-Button.")
        self.auto_save_btn.clicked.connect(self.clicked_auto_save_btn)
        self.auto_save_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        self.clean_btn = QPushButton("c", self)
        self.clean_btn.setGeometry(1050, 40, 81, 31)
        self.clean_btn.setFont(self.font)
        self.clean_btn.setAutoFillBackground(False)
        self.clean_btn.setToolTip("Click me, if you want to <b>clean the Output</b>. The runned code will stay there.")
        self.clean_btn.clicked.connect(self.clicked_clean_btn)
        self.clean_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        self.clear_btn = QPushButton("x", self)
        self.clear_btn.setGeometry(1140, 40, 81, 31)
        self.clear_btn.setFont(self.font)
        self.clear_btn.setAutoFillBackground(False)
        self.clear_btn.setToolTip("Click me, if you want to <b>clean the Output</b> and <b>delete the code</b> which <b>runned already</b>.")
        self.clear_btn.clicked.connect(self.clicked_clear_btn)
        self.clear_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        self.show_runned_code_btn = QPushButton("show", self)
        self.show_runned_code_btn.setGeometry(1400, 40, 81, 31)
        self.show_runned_code_btn.setFont(self.font)
        self.show_runned_code_btn.setAutoFillBackground(False)
        self.show_runned_code_btn.setToolTip("Click me, if you want to <b>see the code</b> which <b>runned already</b>.")
        self.show_runned_code_btn.clicked.connect(self.clicked_show_runned_code_btn)
        self.show_runned_code_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        self.export_output_btn = QPushButton(">>", self)
        self.export_output_btn.setGeometry(1770, 40, 81, 31)
        self.export_output_btn.setFont(self.font)
        self.export_output_btn.setAutoFillBackground(False)
        self.export_output_btn.setToolTip("Click me, if you want to <b>see the code</b> which <b>runned already</b>.")
        self.export_output_btn.clicked.connect(self.clicked_export_output_btn)
        self.export_output_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

        # logo show at beginning
        self.start_background = QFrame(self)
        self.start_background.setStyleSheet("background-color:#424242")
        self.start_background.setGeometry(0, 0, 1920, 1080)
        self.logo_label = QLabel(self)
        self.logo = QPixmap('logo_blue_big_2.png')
        w = int(self.logo.width()/2)
        h = int(self.logo.height()/2)
        self.logo = self.logo.scaled(QSize(w,h))
        self.logo_2 = QPixmap('logo_blue_big.png')
        w = int(self.logo_2.width()/2)
        h = int(self.logo_2.height()/2)
        self.logo_2 = self.logo_2.scaled(QSize(w,h))
        self.logo_label.setPixmap(self.logo)
        x = int(self.width()/2 - self.logo.width()/2)
        y = int(self.height()/2 - self.logo.height()/2 - 150)
        self.logo_label.move(x, y)
        self.logo_text = QLabel("Starting Python Lair...", self)
        self.logo_text.setStyleSheet(u"QLabel\n"
                                        "{\n"
                                        "color:black;\n"
                                        "font-weight:bold;\n"
                                        "font: 75 36pt \"MS Shell Dlg 2\";\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "")
        x = int(self.width()/2 - 200)
        y = int(self.height()/2 + 230)
        self.logo_text.move(x, y)
        self.logo_under_text = QLabel("A blockbased Python IDE", self)
        self.logo_under_text.setStyleSheet(u"QLabel\n"
                                        "{\n"
                                        "color:black;\n"
                                        "font: 75 16pt \"MS Shell Dlg 2\";\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "")
        x = int(self.width()/2 - 110)
        y = int(self.height()/2 + 310)
        self.logo_under_text.move(x, y)
        self.logo_counter = 0
        self.logo_timer = QTimer(self)
        self.logo_timer.setInterval(750)
        self.logo_timer.timeout.connect(self.logo_time_over)
        self.logo_timer.start()

    # Click Methoden
    def clicked_add_btn(self, event):
        self.input_box.add_item(CodeBlock)

    def clicked_del_btn(self, event):
        self.input_box.clear()

    def clicked_play_btn(self, event): # before coding, it has to save in a file
        self.code.clear()
        codeblocks = self.input_box.get_items()
        if len(codeblocks) > 0:
            for codeblock in codeblocks:
                txt = self.code.run_entry(codeblock.get_id(), codeblock.get_code())
                self.output_box.add_item(CodeBlock, txt.rstrip(), inverse=True)
                self.resize_timer.start()

    def clicked_export_btn(self, event):
        file_name = QFileDialog.getSaveFileName(self, 'Save File')
        if file_name[0] != "":
            if not(file_name[0].endswith(".py")):
                file_name = (file_name[0]+".py", file_name[1])
            
            code = self.input_box.get_clean_code()
            
            if file_name[0] != "":
                with open(file_name[0], 'w') as f:
                    f.write(code)
                    #f.close() #mit with braucht man das nicht mehr?

    def clicked_export_output_btn(self, event):
        file_name = QFileDialog.getSaveFileName(self, 'Save File')
        if file_name[0] != "":
            if not(file_name[0].endswith(".txt")):
                file_name = (file_name[0]+".txt", file_name[1])
            
            code = self.output_box.get_output()
            
            if file_name[0] != "":
                with open(file_name[0], 'w') as f:
                    f.write(code)

    def clicked_import_btn(self, event):
        file_name = QFileDialog.getOpenFileName(self, 'OpenFile', "*.py")
        if file_name[0] != "":
            if file_name[0].endswith(".py"):
                with open(file_name[0], 'r') as f:
                    lines = f.readlines()
                # gehe lines durch und adde neue blöcke
                is_in_block = False
                without_block = ""
                for i in lines:
                    if i.replace(" ", "")[0:3] == "#%%" and is_in_block == False:
                        txt = ""
                        is_in_block = True
                    elif i.replace(" ", "")[0:3] == "#%%" and is_in_block == True: # save inhalt und erstelle block
                        self.input_box.add_item(CodeBlock, txt[:-1], coloring=True)
                        is_in_block = False
                        txt = ""
                    elif is_in_block == False:
                        without_block += i
                    else:
                        content = i.rstrip()+"\n"
                        txt += content  

                if without_block != "":
                    self.input_box.add_item(CodeBlock, without_block.rstrip(), coloring=True)
        self.resize_timer.start()

    def clicked_save_btn(self, event):
        if self.save_place == None:
            self.save_as_btn.click()
        else:
            file_name = self.save_place
            code = self.input_box.get_code()
            if file_name != "":
                with open(file_name, 'w') as f:
                    f.write(code)

    def clicked_save_as_btn(self, event):
        file_name = QFileDialog.getSaveFileName(self, 'Save File')
        if file_name[0] != "":
            if not(file_name[0].endswith(".py")):
                file_name = (file_name[0]+".py", file_name[1])
            self.save_place = file_name[0]
            code = self.input_box.get_code()
            if file_name[0] != "":
                with open(file_name[0], 'w') as f:
                    f.write(code)

    def clicked_auto_save_btn(self, event):
        if self.should_auto_saving:
            self.should_auto_saving = False
            self.auto_saver.stop()
            self.auto_save_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#445d87;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")
        else:
            self.should_auto_saving = True
            self.auto_saver.start()
            self.auto_save_btn.setStyleSheet(u"QPushButton\n"
                                        "{\n"
                                        "background-color:#27408B;\n"
                                        "font: 75 14pt \"MS Shell Dlg 2\";\n"
                                        "color:white;\n"
                                        "border-style: none;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton::pressed\n"
                                        "{\n"
                                        "background-color:#424242;\n"
                                        "}\n"
                                        "\n"
                                        "QPushButton:hover\n"
                                        "{\n"
                                        "border-style:solid;\n"
                                        "border-width:2px;\n"
                                        "border-color:black;\n"
                                        "}\n"
                                        "")

    def clicked_clear_btn(self, event):
        self.output_box.clear()
        self.code.clear()

    def clicked_clean_btn(self, event):
        self.output_box.clear()

    def clicked_show_runned_code_btn(self, event):
        txt = self.code.get_code()
        self.output_box.add_item(CodeBlock, txt.rstrip(), inverse=True, coloring=True)

    def auto_saving(self):
        if self.save_place != None:
            self.save_btn.click()

    def resize_event(self):
        self.resize_timer.stop()
        self.input_box.resize()
        self.output_box.resize()

    def logo_time_over(self):
        self.logo_counter += 1
        if self.logo_counter >= 4:
            self.logo_timer.stop()
            self.logo_label.setVisible(False)
            self.logo_text.setVisible(False)
            self.logo_under_text.setVisible(False)
            self.start_background.setVisible(False)
        elif self.logo_counter == 3:
            self.logo_label.setPixmap(self.logo)
        elif self.logo_counter == 2:
            self.logo_label.setPixmap(self.logo_2)
        elif self.logo_counter == 1:
            self.logo_label.setPixmap(self.logo_2)

    def keyPressEvent(self, e):
        super().keyPressEvent(e)

    def run(self, id_:int, code:str):
        txt = self.code.run_entry(id_, code)
        self.output_box.add_item(CodeBlock, txt.rstrip(), inverse=True)
        self.resize_timer.start()
        
    def get_app(self):
        return self.app


app = QApplication(sys.argv)
window = Window(app)
window.showMaximized()
app.exec_()