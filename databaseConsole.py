import sys
import os
import operator
from PyQt5.QtGui import QImage, QPalette, QBrush, QFont
from PyQt5.QtWidgets import (QWidget, QLabel, 
     QLineEdit, QApplication, QPushButton)
from PyQt5.QtCore import QCoreApplication, pyqtSlot, QSize, QTimer
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
        self.tries_remaining = 9
        self.game_end_fail = False
        self.game_end_triumph = False
        self.game_timeout = False
        self.screen_updated = False
        self.long_message_length = 10
        self.game_time = 1500
        self.default_message = 'Waiting for database key ...'
        self.game_failure_message = 'Database shutdown, system intrusion detected'
        self.secret_keys = {'9291184': False,
                            '117193': False,
                            '861364710132011141107': False}
        self.secret_password = '# 1261'
        self.background_image_path = self.resource_path("Webster_Notes.png")
        self.font = "Times"
        self.font_size = 8
        self.initUI()
        
    def initUI(self):
        myfont = QFont(self.font, self.font_size) 

        oImage = QImage(self.background_image_path)
        sImage = oImage.scaled(QSize(1500, 800))
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))
        self.setPalette(palette)

        self.timer_label = QLabel(self)
        self.timer = QTimer()

        self.qline_edit = QLineEdit(self)
        self.qline_edit.setFont(myfont)
        self.message_label = QLabel(self.default_message, self)
        self.message_label.setFont(myfont)
        self.code_label = QLabel(self)
        self.code_label.setFont(myfont)
        self.timer_label.setFont(myfont)
        self.success_message_label = QLabel(self)
        self.success_message_label.setFont(myfont)
        self.qbutton = QPushButton('Submit', self)
        self.qbutton.setFont(myfont)

        self.qline_edit.move(600, 380)
        self.qbutton.move(800, 375)
        self.message_label.move(600, 280)
        self.success_message_label.move(600, 480)
        self.code_label.move(755, 480)
        self.timer_label.move(500, 260)

        self.qline_edit.returnPressed.connect(self.qbutton.click)
        self.qbutton.clicked.connect(self.on_qbutton_clicked)
        self.timer.timeout.connect(self.timerTick)

        self.qbutton.resize(self.qbutton.sizeHint())
        self.setGeometry(300, 300, 1500, 800)
        self.setWindowTitle('Secure Database')
        self.show()

    def resource_path(self, relative_path):
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def updateTimerDisplay(self):
        time = "%d:%02d" % (self.time_left/60, self.time_left % 60)
        self.update_label(self.timer_label, time)

    def startTimer(self):
        self.time_left = self.game_time
        self.updateTimerDisplay()
        self.timer.start(1000)

    def timerTick(self):
        self.time_left -= 1
        self.updateTimerDisplay()
        if self.time_left <= 0:
           self.timer.stop()
           self.game_timeout = True
           self.game_end_timeout(self.screen_updated)
           

    def tries_left(self):
        self.tries_remaining = self.tries_remaining - 1
        return self.tries_remaining

    def update_label(self, label, text):
        label.setText(text)
        label.adjustSize()
        QApplication.processEvents()

    def check_message(self, text):
        if len(text) >= self.long_message_length:

            # If the message is too long, cut it down
            text = text[0:9] + "..."

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
        success_message_text = ''
        num_guessed = 0

        for key, value in self.secret_keys.items():
            if text == key:
                if self.secret_keys[key] == False:
                    message_text = 'Key entered'
                    code_text = 'Key accepted'
                    self.secret_keys[key] = True
                else:
                    message_text = 'Key already entered'
                    code_text = ''
                break

        if code_text is None:
            message_text = self.not_found_message()
            code_text = ''

        for key, value in self.secret_keys.items():
            if value:
                num_guessed += 1

        if num_guessed == len(self.secret_keys.keys()):
            message_text = 'Top Secret access granted. Welcome Agent 69-88'
            success_message_text = ''
                                
            code_text = self.secret_password
            self.game_end_triumph = True

        # Game over
        if self.tries_remaining == 0 and code_text == '':
            message_text = self.game_failure_message
            self.game_end_fail = True

        return message_text, code_text, success_message_text

    def game_end_timeout(self, screen_updated):
        if not screen_updated:
            message_text = self.game_failure_message
            self.update_label(self.message_label, message_text)
        self.qline_edit.hide()
        self.code_label.hide()
        self.success_message_label.hide()
        self.qbutton.hide()
        self.timer.stop()
        self.timer_label.hide()
        self.game_end_fail = True

    def game_end_failure(self, screen_updated):
        if not screen_updated:
            message_text = self.game_failure_message
            self.update_label(self.message_label, message_text)
        self.qline_edit.hide()
        self.code_label.hide()
        self.success_message_label.hide()
        self.qbutton.hide()
        self.timer.stop()
        self.timer_label.hide()
        self.game_end_fail = True

    def game_end_success(self):
        self.qline_edit.hide()
        self.qbutton.hide()
        self.timer.stop()
        self.game_end_triumph = True

    def game_end_check(self, screen_updated):
        if self.game_end_fail:
            self.game_end_failure(screen_updated)
        if self.game_timeout:
            self.game_end_timeout(screen_updated)
        if self.game_end_triumph:
            self.game_end_success()

    @pyqtSlot()
    def on_qbutton_clicked(self):
        input_text = self.qline_edit.text()
        self.qline_edit.clear()
        self.update_label(self.code_label, '')
        message_text, code_text, success_message_text = self.check_text(input_text)

        # When we click the button make sure we update the messages after processing
        self.update_label(self.message_label, message_text)
        self.update_label(self.success_message_label, success_message_text)
        self.update_label(self.code_label, code_text)

        self.screen_updated = True
            
        # Check for game end before returning to the main screen
        if not self.game_end_fail and not self.game_end_triumph and not self.game_timeout:
            sleep(2)
            self.update_label(self.message_label, self.default_message)
            self.update_label(self.code_label, '')

            # Reset the screen status
            self.screen_updated = False
        else:
            self.screen_updated = False
            self.game_end_check(self.screen_updated)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    game = Game()
    game.startTimer()
    sys.exit(app.exec_())
