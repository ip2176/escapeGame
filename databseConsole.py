import sys
import os
import operator
from PyQt5.QtGui import QImage, QPalette, QBrush, QFont
from PyQt5.QtWidgets import (QWidget, QLabel, 
     QLineEdit, QApplication, QPushButton)
from PyQt5.QtCore import QCoreApplication, pyqtSlot, QSize, QTimer, QRunnable, QThreadPool
from time import sleep


class WaitLoop(QRunnable):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.is_running = True

    def stop(self):
        self.is_running = False

    @pyqtSlot()
    def run(self):
        code_text = None
        success_message_text = ''
        message_text = ''
        num_guessed = 0

        self.parent.input_text = self.parent.qline_edit.text()
        self.parent.qline_edit.clear()
        self.parent.update_label(self.parent.code_label, '')

        for i in self.parent.spinner.calculate_rotations():
            self.parent.update_label(self.parent.message_label, self.parent.check_message(self.parent.input_text))
            sleep(self.parent.spinner.speed)
        self.parent.update_label(self.parent.message_label, 'Done')
        self.parent.spinner.reset()
        sleep(0.5)

        for key, value in self.parent.secret_keys.items():
            if self.parent.input_text.upper() == key:
                message_text = 'Key entered'
                code_text = 'Key accepted'
                self.parent.secret_keys[key] = True
                break

        if code_text is None:
            message_text = self.parent.not_found_message()
            code_text = ''

        for key, value in self.parent.secret_keys.items():
            if value:
                num_guessed += 1

        if num_guessed == len(self.parent.secret_keys.keys()):
            message_text = 'Top Secret access granted. Welcome Agent 69-88'
            success_message_text = 'Document Password:'
                                
            code_text = self.parent.secret_password
            self.parent.game_end_keys_entered = True

        # Game over
        if self.parent.tries_remaining == 0 and code_text == '':
            message_text = 'Database shutdown, system intrusion detected'
            self.parent.game_end_fail = True

        # When we click the button make sure we update the messages after processing
        screen_updated = True
        if self.is_running:
            self.parent.update_label(self.parent.message_label, message_text)
            self.parent.update_label(self.parent.success_message_label, success_message_text)
            self.parent.update_label(self.parent.code_label, code_text)
        else:
            screen_updated = False

        # Hide all the things!
        self.parent.game_end_check(screen_updated)

        if self.is_running:
            if not self.parent.game_end_fail and not self.parent.game_end_keys_entered:
                sleep(2)
                if not self.parent.timed_out:
                    self.parent.update_label(self.parent.message_label, self.parent.default_message)
                    self.parent.update_label(self.parent.code_label, '')
                else:
                    self.parent.game_end_timeout()


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
        self.game_end_keys_entered = False
        self.timed_out = False
        self.default_message = 'Waiting for database key ...'
        self.secret_keys = {'9291184': False,
                            '117193': False,
                            'TEST3': False}
        self.secret_password = 'SecretPassword'
        self.background_image_path = self.resource_path("Webster_Notes.png")
        self.font = "Times"
        self.input_text = None
        self.font_size = 8
        self.timeout = 20 # in seconds
        self.wait_loop = None
        self.threadpool = QThreadPool()
        self.initUI()
        
    def initUI(self):
        myfont = QFont(self.font, self.font_size)
        self.threadpool.setMaxThreadCount(1)

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
        self.timer.timeout.connect(self.timer_tick)

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

    def update_timer_display(self):
        time = "%d:%02d" % (self.time_left/60, self.time_left % 60)
        self.update_label(self.timer_label, time)

    def start_timer(self):
        self.time_left = self.timeout
        self.update_timer_display()
        self.timer.start(1000)

    def timer_tick(self):
        self.time_left -= 1
        self.update_timer_display()
        if self.time_left <= 0:
           self.timer.stop()
           self.game_end_timeout()

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

    def stop_thread(self):
        self.wait_loop.stop()

    def game_end_timeout(self):
        if self.wait_loop is not None:
            if not self.wait_loop.is_running:
                message_text = 'Database shutdown, system intrusion detected'
                self.update_label(self.message_label, message_text)
        self.qline_edit.hide()
        self.code_label.hide()
        self.success_message_label.hide()
        self.qbutton.hide()
        self.timer.stop()
        self.timer_label.hide()
        self.game_end_fail = True
        self.timed_out = True
        if self.wait_loop is not None:
            self.stop_thread()

    def game_end_failure(self, screen_updated):
        if not screen_updated:
            message_text = 'Database shutdown, system intrusion detected'
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
        self.game_end_keys_entered = True

    def game_end_check(self, screen_updated):
        if self.game_end_fail:
            self.game_end_failure(screen_updated)
        if self.game_end_keys_entered:
            self.game_end_success()

    @pyqtSlot()
    def on_qbutton_clicked(self):
        self.wait_loop = WaitLoop(parent=self)
        self.threadpool.start(self.wait_loop)


if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    game = Game()
    game.start_timer()
    sys.exit(app.exec_())
