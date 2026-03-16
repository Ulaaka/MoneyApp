from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5 import QtCore
from database_connection import database
from BASE_Classes import password_class
from qtwidgets import PasswordEdit
from system_functions import system_functions
import os, certifi, sys
from system_functions import system_functions
from functools import partial

color_dic = {
"login_page": {
    "title_color" :"#32CD32",
    "background_color":"#000000",
    "login_button_color":{
        "normal":"#32CD32",
        "focus":"#00FF7F"
    },
    "sign_up_button_color":{
        "normal":"#1877F2",
        "focus":"#18d5f2"
    }
},
"sign_up_page":{
    "title_color":"#1877F2", 
    "background_color":"#000000", 
    "submit_button_color":{
        "normal":"#1877F2", 
        "focus":"#18d5F2"
    }
},
"validation_page":{
    "title_color":"#1877F2", 
    "background_color":"#000000", 
    "submit_button_color":{
        "normal":"#1877F2", 
        "focus":"#18d5F2"
    }
}, 
'reset_password':{
    "title_color":"#1877F2", 
    "background_color":"#000000", 
    "submit_button_color":{
        "normal":"#1877F2", 
        "focus":"#18d5F2"
    }
}}

system = system_functions()

# setting django up
sys.path.insert(0, '/Users/nyamdorjbat-erdene/Final_year')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import django
django.setup()

# https://stackoverflow.com/questions/45623918/using-qstackedwidget-for-multi-windowed-pyqt-application
# https://doc.qt.io/qt-6/stylesheet-reference.html
input_style = '''
    QLineEdit {
        background-color: dark;
        border: 2px solid grey;
        border-radius: 1px;
        padding: 12px;
        color: white;
        font-size: 14px;
    }
    QLineEdit:focus {
        border: 1px solid white;
    }
    '''

random_digit_box_style = '''
    QLineEdit {
        border: 2px solid #ccc;
        border-radius: 8px;
        background: #f9f9f9;
        color: #333;
        font-size: 15px;
        text-align: center;
        min-width: 50px;
        max-width: 50px;
        min-height: 55px;
        max-height: 55px;
    }
    QLineEdit:focus {
        border: 2px solid #6C63FF;
        background: white;
    }

'''
# if underline_button, button_color = "transparent"
def handle_button_style(if_handle, button_color, hover_color):
        handle_button_additional = """
            border-radius: 25px;
            padding: 15px;
        """

        underline_button_additional = """
            text-decoration: underline;
            font-size: 15px;
        """
        
        if if_handle:
            add_text = handle_button_additional
            add_color = "background-color"
        else:
            add_text = underline_button_additional
            add_color = "color"

        line = f'''
            QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                {add_text}
            }}
            QPushButton:hover {{
                {add_color}: {hover_color};
            }}
        '''
        return line

def secs_to_minsec(secs: int):
    mins = secs // 60
    secs = secs % 60
    minsec = f'{mins:02}:{secs:02}'
    return minsec

class login_page(QWidget):
    def __init__(self, controller, db, cursor):
        super().__init__()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.system = system_functions()

        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Finance Login')
        self.setFixedSize(400, 500)

        # set the color of the background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color_dic["login_page"]["background_color"]))
        self.setPalette(palette)

        # layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 70, 50, 70)
        layout.setSpacing(25)

        # Title
        title = QLabel('Finance Reporter')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title_color = title.palette()
        title_color.setColor(QPalette.WindowText, QColor(color_dic["login_page"]["title_color"]))
        title.setPalette(title_color)

        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.setStyleSheet(input_style)
        self.username.setFont(QFont('Arial', 15))

        # Password input
        self.password = QLineEdit()
        self.password.setPlaceholderText('Password')

        # hiding the password
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setStyleSheet(input_style)
        self.password.setFont(QFont('Arial', 15))

        # Login button
        login_btn = QPushButton('Log In')
        login_btn.setStyleSheet(handle_button_style(True, color_dic["login_page"]['login_button_color']["normal"], color_dic["login_page"]['login_button_color']["focus"]))
        login_btn.setFont(QFont('Arial', 15, QFont.Bold))
        login_btn.setFixedHeight(50)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)

        # sign up button
        signup_btn = QPushButton('Create new account')
        signup_btn.setStyleSheet(handle_button_style(True, color_dic["login_page"]["sign_up_button_color"]["normal"], color_dic["login_page"]["sign_up_button_color"]["focus"]))
        signup_btn.setFont(QFont('Arial', 15, QFont.Bold))
        signup_btn.setFixedHeight(50)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.clicked.connect(self.handle_sign_up)

        # Forgot password link
        forgot_password = QPushButton('Forgotten password?')
        forgot_password.setStyleSheet(handle_button_style(False, "transparent", "green"))
        forgot_password.setCursor(Qt.PointingHandCursor)
        forgot_password.clicked.connect(self.handle_forgot_password)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(login_btn)
        layout.addWidget(forgot_password, alignment=Qt.AlignCenter)
        layout.addWidget(signup_btn)
        layout.addStretch()
        self.setLayout(layout)

    def handle_sign_up(self):
        self.controller.show_sign_up()

    def handle_login(self):
        username_local = self.username.text()
        password_local = self.password.text()
        password_manager = password_class()

        if not username_local or not password_local:
            QMessageBox.warning(self, 'Error', 'Please enter both of the credentials, thank you')
            return

        # needs to add a timer of 1 minute
        sql = f"SELECT hashed_password FROM users WHERE username = %s"
        self.cursor.execute(sql, (username_local, ))
        result = self.cursor.fetchone()

        if result and password_manager.check_password(password_local, result[0]):
                self.controller.show_dashboard()
        else:
            QMessageBox.warning(self, 'Error', 'Password or Username is wrong')
            return

    # finished to be later
    def handle_forgot_password(self):
        username_local = self.username.text()

        if not username_local:
            QMessageBox.information(
                self,
                'Forgot Password',
                'Please enter your username first, then click "Forgot your password?"'
            )
            return

        self.random_digits = self.system.send_reset_digits(6, username_local)
        self.controller.show_validation_page()
        """        QMessageBox.information(
            self,
            'Password Reset',
            f'A password reset link has been sent to the email associated with username: {username_local}'
        )"""


class sign_up_page(QWidget):

    # https://doc.qt.io/qt-6/stylesheet-reference.html
    def __init__(self, controller, db, cursor):
        super().__init__()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Sign Up')
        self.setFixedSize(400, 500)
        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color_dic["sign_up_page"]["background_color"]))
        self.setPalette(palette)

        # layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 70, 50, 70)
        layout.setSpacing(25)

        # Title
        title = QLabel('Create a new account')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title_color = title.palette()
        title_color.setColor(QPalette.WindowText, QColor(color_dic["sign_up_page"]['title_color']))
        title.setPalette(title_color)

        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.setStyleSheet(input_style)
        self.username.setFont(QFont('Arial', 15))

        # Password input
        self.password = PasswordEdit()
        self.password.setPlaceholderText('Password')
        self.password.setStyleSheet(input_style)
        self.password.setFont(QFont('Arial', 15))
        self.password.setToolTip(
            "Your password must be at least 8 characters \n"
            "should include: \n"
            "- a combination of numbers\n"
            "- letters\n"
            "- special characters (!$@%)"
        )

        # email input
        self.email = QLineEdit()
        self.email.setPlaceholderText('Email')
        self.email.setStyleSheet(input_style)
        self.email.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(handle_button_style(True, color_dic["sign_up_page"]["submit_button_color"]["normal"], color_dic["sign_up_page"]["submit_button_color"]["focus"]))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_submit)

        # already have an account?
        got_account = QPushButton('Already have an account?')
        got_account.setStyleSheet(handle_button_style(False, "transparent", 'green'))
        got_account.setCursor(Qt.PointingHandCursor)
        got_account.clicked.connect(self.handle_got_account)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.email)
        layout.addWidget(submit_btn)
        layout.addWidget(got_account, alignment=Qt.AlignCenter)
        layout.addStretch()
        self.setLayout(layout)

    def handle_got_account(self):
        self.controller.show_login()
        pass

    def handle_submit(self):
        username_local = self.username.text()
        password_local = self.password.text()
        email_local = self.email.text()

        password_manager = password_class()

        sql = f"SELECT userID FROM users WHERE username = %s"
        self.cursor.execute(sql, (username_local,))
        result = self.cursor.fetchone()

        if not username_local or not password_local or not email_local:
            QMessageBox.warning(self, 'Error', 'Please enter all  the credentials, thank you')
            return

        if result:
            QMessageBox.warning(self, 'Error', 'Username already exists, please try another username')
            return

        if not password_manager.check_password_safety(password_local):
            QMessageBox.warning(self, 'Not Satisfied', 'Password Requirement not satisfied')
            return

        if not password_manager.check_email_validity(email_local):
            QMessageBox.warning(self, 'Invalid', 'Invalid email')
            return

        try:
            hashed_password = password_manager.hash_password(password_local)
            new_sql = f"INSERT INTO users (username, hashed_password, email_address) VALUES (%s, %s, %s)"
            self.cursor.execute(new_sql, (username_local, hashed_password, email_local))
            self.db.commit()
            self.controller.show_login()
            print("Credentials added successfully")
        except:
            print("could not commit")

class validation_page(QWidget):
    def __init__(self, controller, login_page,  db, cursor):
        super().__init__()
        self.duration = 90
        self.time_left_int = self.duration
        self.myTimer = QtCore.QTimer(self)
        self.system = system_functions()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.login_page = login_page
        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Reset Password')
        self.setFixedSize(400, 500)

        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color_dic["validation_page"]['background_color']))
        self.setPalette(palette)

        # layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 70, 50, 70)
        layout.setSpacing(25)

        # Title
        title = QLabel('Reset Your Password')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title_color = title.palette()
        title_color.setColor(QPalette.WindowText, QColor(color_dic["validation_page"]['title_color']))
        title.setPalette(title_color)

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(handle_button_style(True, color_dic["validation_page"]['submit_button_color']['normal'],color_dic["validation_page"]['submit_button_color']['focus']))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_reset_password)

        self.timerLabel = QLabel("01:30", self)
        self.timerLabel.move(50, 50)
        self.timerLabel.setAlignment(Qt.AlignCenter)
        self.timerLabel.setStyleSheet("font: 17pt Helvetica;")

        self.squares = []
        centering = Qt.AlignCenter
        square_layout = QHBoxLayout()

        for idx in range(6):
            square = QLineEdit()
            square.setMaxLength(1)
            square.setAlignment(centering)
            square.setStyleSheet(random_digit_box_style)

            square.textChanged.connect(partial(self.to_next_box, idx))
            square.keyPressEvent = partial(self.to_prev_box, idx)

            square_layout.addWidget(square)
            self.squares.append(square)

        layout.addWidget(title)
        layout.addLayout(square_layout)
        self.setLayout(layout)
        layout.addWidget(submit_btn)
        layout.addWidget(self.timerLabel)
        layout.addStretch()

    # needs to be changed
    def to_next_box(self, idx, _):
        if idx < 5:
            self.squares[idx + 1].setFocus()

    def to_prev_box(self, idx, input):
        if input.key() == Qt.Key_Backspace:
            if not self.squares[idx].text() and idx > 0:
                self.squares[idx - 1].clear()
                self.squares[idx - 1].setFocus()

        QLineEdit.keyPressEvent(self.squares[idx], input)

    def handle_reset_password(self):
        entered = "".join(i.text() for i in self.squares)
        if (self.login_page.random_digits == entered):
            self.controller.show_reset_password()
        else:
            QMessageBox.information(
                self,
                'mismatch',
                'Codes dont not match"'
            )
            return

    # needs to be changed
    def startTimer(self):
        self.time_left_int = self.duration
        self.myTimer.timeout.connect(self.timerTimeout)
        self.myTimer.start(1000)

    def timerTimeout(self):
        self.time_left_int -= 1

        if self.time_left_int == 0:
            self.time_left_int = self.duration
            self.login_page.random_digits = self.system.send_reset_digits(6, self.login_page.username.text())
            for i in range(6):
                self.squares[i].clear()
        self.update_gui()

    def update_gui(self):
        minsec = secs_to_minsec(self.time_left_int)
        self.timerLabel.setText(minsec)

class reset_password(QWidget):

    def __init__(self, controller, login_page, db, cursor):
        super().__init__()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.login_page = login_page
        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Enter New Password')
        self.setFixedSize(400, 500)

        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color_dic["reset_password"]["background_color"]))
        self.setPalette(palette)

        # layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 70, 50, 70)
        layout.setSpacing(25)

        # Title
        title = QLabel('Password Reset')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 20, QFont.Bold))
        title_color = title.palette()
        title_color.setColor(QPalette.WindowText, QColor(color_dic["reset_password"]["title_color"]))
        title.setPalette(title_color)

        # New Password input
        self.password_1 = PasswordEdit()
        self.password_1.setPlaceholderText('New Password')
        self.password_1.setStyleSheet(input_style)
        self.password_1.setFont(QFont('Arial', 15))

        # Retype New Password
        self.password_2 = PasswordEdit()
        self.password_2.setPlaceholderText('Re-type New Password')
        self.password_2.setStyleSheet(input_style)
        self.password_2.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(handle_button_style(True, color_dic["reset_password"]["submit_button_color"]['normal'], color_dic["reset_password"]["submit_button_color"]['focus']))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.compare_password)

        self.description = "Your password must be at least 8 characters and should include a combination of numbers, letters and special characters (!$@%)."
        # instruction for password requirement
        description_label = QLabel(self.description, self)
        description_label.move(100, 100)
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setFixedWidth(300)
        description_label.setStyleSheet("font: 15pt Helvetica;")

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.password_1)
        layout.addWidget(self.password_2)
        layout.addWidget(submit_btn)
        layout.addWidget(description_label)
        layout.addStretch()

        self.setLayout(layout)

    def compare_password(self):
        password_manager = password_class()
        safety = password_manager.check_password_safety(self.password_1.text())
        same = self.password_1.text() == self.password_2.text()
        if not safety:
            QMessageBox.information(
                self,
                'Password requirement not satisfied',
                self.description
            )
            return

        if not same:
            QMessageBox.information(
                self, 
                'Password do not match', 
                'Check your password again"'
            )
            return

        if safety and same:
           print("New Password Matches")

           hashed_password = password_manager.hash_password(self.password_1.text())
           username = self.login_page.username.text()

           query = "UPDATE users SET hashed_password = %s WHERE username = %s"
           self.cursor.execute(query, (hashed_password, username))
           self.db.commit()

           self.controller.show_login()


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

        self.setWindowTitle("Finance Reporter")
        self.setFixedSize(400, 500)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_page = login_page(self, self.db, self.cursor) 
        self.sign_up_page = sign_up_page(self, self.db, self.cursor)

        # adding reset form page
        self.validation_page = validation_page(self, self.login_page, self.db, self.cursor)
        self.reset_password = reset_password(self, self.login_page, self.db, self.cursor)
        self.dashboard_page = QWidget()

        self.setup_dashboard()

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.sign_up_page)
        self.stacked_widget.addWidget(self.validation_page)
        self.stacked_widget.addWidget(self.reset_password)

    def setup_dashboard(self):
        layout = QVBoxLayout()

        logout_btn = QPushButton("Log Out")
        logout_btn.clicked.connect(self.show_login)

        layout.addWidget(logout_btn)
        self.dashboard_page.setLayout(layout)

    def show_dashboard(self):
        self.stacked_widget.setCurrentIndex(1)
        self.setMinimumSize(1000, 700) 
        self.setMaximumSize(16777215, 16777215)

    def show_login(self):
        self.stacked_widget.setCurrentIndex(0)
        self.setMaximumSize(400, 500)

    def show_sign_up(self):
        self.stacked_widget.setCurrentIndex(2)
        self.setMaximumSize(400, 500)

    def show_validation_page(self):
        self.stacked_widget.setCurrentIndex(3)
        self.setMaximumSize(400, 500)
        self.validation_page.startTimer()

    def show_reset_password(self):
        self.stacked_widget.setCurrentIndex(4)
        self.setMaximumSize(400, 500)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainApp()
    main_window.show()

    sys.exit(app.exec_())
