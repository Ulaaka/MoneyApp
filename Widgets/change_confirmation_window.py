from Widgets.change_confirmation import Ui_change_confirmation
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from system_functions import manage_seconds_qt, system_functions
class Change_confirmation_page(QDialog):
    finished = pyqtSignal() 

    def __init__(self, parent):
        super().__init__(parent)
        self.userID = parent.userID
        self._parent = parent
        self.duration = 90
        self.timer = QTimer(self)
        self.system = system_functions()
        self.code = self.system.send_reset_digits(6, userID=self.userID)

        self.ui = Ui_change_confirmation()
        self.ui.setupUi(self)

        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        self.change_information_signals_connection()
        self.change_information_show()

    def change_information_signals_connection(self):
        self.ui.code_submit_button.clicked.connect(self.submit_code)
        self.ui.resend_button.clicked.connect(self.resend_button)
        self.ui.timer_label.setText("01:30")

    def change_information_show(self):
        self.timer_manager = manage_seconds_qt(self.ui.timer_label, self.timer, self.duration, expire_func=self.expire_func)

    def start_time(self):
        self.timer_manager.begin_timer()

    def expire_func(self):
        code = self.system.send_reset_digits(
            6, userID=self.userID)
        self.code = code

    def resend_button(self):
        self.ui.confirmation_line.clear()
        self.expire_func()
        self.timer.stop()
        self.timer_manager.begin_timer()

    def submit_code(self):
        entered_code =self.ui.confirmation_line.text()
        if entered_code == str(self.code):
            self.finished.emit()
            self.timer.stop()
            self.close()
        else:
            return

    def closeEvent(self, event):
        self.timer.stop()
        self.accept()