import sys
import operator
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtWidgets import (QWidget, QLabel, 
     QLineEdit, QApplication, QPushButton)
from PyQt5.QtCore import QCoreApplication, pyqtSlot, QSize
from time import sleep


class Spinner():

    def __init__(self):
        self.first = '|'
        self.second = '/'
        self.third = '--'
        self.fourth = '\\'
        self.num_of_sprites = 4
        self.current = None
        self.speed = 0.1
        self.num_rotations = 6

    def get_next(self):
        if self.current == self.first:
            self.current = self.second
            return self.second
        elif self.current == self.second:
            self.current = self.third
            return self.third
        elif self.current == self.third:
            self.current = self.fourth
            return self.fourth
        elif self.current == self.fourth:
            self.current = self.first
            return self.first
        elif self.current is None:
            self.current = self.first
            return self.first

    def reset(self):
        self.current = self.first

    def calculate_rotations(self):
        return range(1, self.num_rotations * self.num_of_sprites + 2) # Extra 2 for the start and end animations


class Game(QWidget):
    
    def __init__(self):
        super().__init__()
        self.spinner = Spinner()
        self.tries_remaining = 3
        self.game_end_fail = False
        self.game_end_success = False
        self.default_message = 'Waiting for database key ...'
        self.secret_keys = {'TEST': ['1', False, 'Imagine'],
                            'TEST2': ['2', False, 'A'],
                            'TEST3': ['3', False, 'Password'],
                            'TEST4': ['4', False, 'Here']}
        self.initUI()
        
    def initUI(self):
        oImage = QImage(r"./images/Webster_Notes.png" )
        sImage = oImage.scaled(QSize(1500, 800))
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))
        self.setPalette(palette)

        self.qline_edit = QLineEdit(self)
        self.message_label = QLabel(self.default_message, self)
        self.code_label = QLabel(self)
        self.qbutton = QPushButton('Submit', self)

        self.qline_edit.move(600, 380)
        self.qbutton.move(800, 375)
        self.message_label.move(600, 280)
        self.code_label.move(750, 480)

        self.qline_edit.returnPressed.connect(self.qbutton.click)
        self.qbutton.clicked.connect(self.on_qbutton_clicked)

        self.qbutton.resize(self.qbutton.sizeHint())
        self.setGeometry(300, 300, 1500, 800)
        self.setWindowTitle('Secure Database')
        self.show()

    def tries_left(self):
        self.tries_remaining = self.tries_remaining - 1
        return self.tries_remaining

    def update_label(self, label, text):
        label.setText(text)
        label.adjustSize()
        QApplication.processEvents()

    def check_message(self, text):
        return 'Entering key ({0}) to the secure database {1}'.format(text, self.spinner.get_next())

    def not_found_message(self):
        message = 'Key not accepted, you have {0} {1} remaining'
        if self.tries_remaining == 2:
            return message.format(self.tries_left(), 'try')
        else:
            return message.format(self.tries_left(), 'tries')

    def check_test_sleep(self, text):
        for i in self.spinner.calculate_rotations():
            self.update_label(self.message_label, self.check_message(text))
            sleep(self.spinner.speed)
        self.update_label(self.message_label, 'Done')
        self.spinner.reset()
        sleep(0.5)

    def check_text(self, text):
        self.check_test_sleep(text)   
        code_text = None
        num_guessed = 0

        for key, value in self.secret_keys.items():
            if text.upper() == key:
                message_text = 'Key entered'
                code_text = 'Key accepted'
                value[1] = True
                break

        if code_text is None:
            message_text = self.not_found_message()
            code_text = ''

        for key, value in self.secret_keys.items():
            if value[1]:
                num_guessed += 1

        if num_guessed == len(self.secret_keys.keys()):
            message_text = 'Key Success: Code obtained'
            code_text = ''
            self.game_end_success = True
            sorted_keys = sorted(self.secret_keys.items(), key=operator.itemgetter(1))
            for value in sorted_keys:
                code_text += value[1][2]

        # Game over
        if self.tries_remaining == 0 and code_text == '':
            message_text = 'Database shutdown, system intrusion detected'
            self.game_end_fail = True

        return message_text, code_text

    def game_end_check(self):
        if self.game_end_fail:
            self.qline_edit.hide()
            self.code_label.hide()
            self.qbutton.hide()
        if self.game_end_success:
            self.qline_edit.hide()
            self.qbutton.hide()
        
    @pyqtSlot()
    def on_qbutton_clicked(self):
        input_text = self.qline_edit.text()
        self.qline_edit.clear()
        self.update_label(self.code_label, '')
        message_text, code_text = self.check_text(input_text)
        self.update_label(self.message_label, message_text)
        self.update_label(self.code_label, code_text)

        # Hide all the things!
        self.game_end_check()

        if not self.game_end_fail and not self.game_end_success:
            sleep(2)
            self.update_label(self.message_label, self.default_message)
            self.update_label(self.code_label, '')

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    game = Game()
    sys.exit(app.exec_())
