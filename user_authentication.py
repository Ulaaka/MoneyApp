import os, sys, certifi, django
from functools import partial

from PyQt5.QtWidgets import  QWidget, QMainWindow, QApplication, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from qtwidgets import PasswordEdit

from decouple import config
from database_connection import database
from BASE_Classes import password_class, cryptography
from system_functions import system_functions, manage_seconds_qt
from queries import query_processor
from MainWindow import MainWindow
from ui_support_functions import ui_support_functions
import secrets,  base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.algorithms import AES

class login_page(QWidget):
    def __init__(self, controller, db, cursor):
        super().__init__()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.system = system_functions()
        self.query = query_processor()

        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Finance Login')
        self.setFixedSize(400, 500)

        # set the color of the background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(ui_support_functions.color_dic["login_page"]["background_color"]))
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
        title_color.setColor(QPalette.WindowText, QColor(ui_support_functions.color_dic["login_page"]["title_color"]))
        title.setPalette(title_color)

        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.setObjectName("input_field")
        self.username.setFont(QFont('Arial', 15))


        # Password input
        self.password = QLineEdit()
        self.password.setPlaceholderText('Password')

        # hiding the password
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setObjectName("input_field")
        self.password.setFont(QFont('Arial', 15))

        # Login button
        login_btn = QPushButton('Log In')
        login_btn.setStyleSheet(ui_support_functions.handle_button_style(True, ui_support_functions.color_dic["login_page"]['login_button_color']["normal"], ui_support_functions.color_dic["login_page"]['login_button_color']["focus"], underline_flag=False))
        login_btn.setFont(QFont('Arial', 15, QFont.Bold))
        login_btn.setFixedHeight(50)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)

        # sign up button
        signup_btn = QPushButton('Create new account')
        signup_btn.setStyleSheet(ui_support_functions.handle_button_style(True, ui_support_functions.color_dic["login_page"]["sign_up_button_color"]["normal"], ui_support_functions.color_dic["login_page"]["sign_up_button_color"]["focus"], underline_flag=False))
        signup_btn.setFont(QFont('Arial', 15, QFont.Bold))
        signup_btn.setFixedHeight(50)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.clicked.connect(self.handle_sign_up)

        # Forgot password link
        forgot_password = QPushButton('Forgotten password?')
        forgot_password.setStyleSheet(ui_support_functions.handle_button_style(False, "transparent", "green",  underline_flag=True))
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
        query = query_processor()
        password_manager = password_class()
        crypto = cryptography()

        if not username_local or not password_local:
            QMessageBox.warning(self, 'Error', 'Please enter both of the credentials, thank you')
            return

        result = query.get_hashed_password(username=username_local)

        if result and password_manager.check_password(password_local, result[0]):
                userID = query.get_userID(username_local)
                enc_data_key, salt = query.get_data_key_salt(userID)
                wrapping_key = crypto.generate_key(password_local, salt)
                data_key = crypto.decrypt_data_key(wrapping_key, enc_data_key)
                self.controller.show_dashboard(data_key, userID)
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

        self.random_digits = self.system.send_reset_digits(6, username=username_local)
        if self.random_digits:
            self.controller.show_validation_page()
        else:
            # needs to make it more sophisticated
            QMessageBox.warning(self, 'Error', 'The user Does Not Exist')
            return

class sign_up_page(QWidget):

    # https://doc.qt.io/qt-6/stylesheet-reference.html
    def __init__(self, controller, db, cursor):
        super().__init__()
        self.controller = controller
        self.db = db
        self.cursor = cursor
        self.user_interface()
        self.query = query_processor()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Sign Up')
        self.setFixedSize(400, 500)
        # set the color of the background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(ui_support_functions.color_dic["sign_up_page"]["background_color"]))
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
        title_color.setColor(QPalette.WindowText, QColor(ui_support_functions.color_dic["sign_up_page"]['title_color']))
        title.setPalette(title_color)

        # Username input
        self.username = QLineEdit()
        self.username.setPlaceholderText('Username')
        self.username.setObjectName("input_field")
        self.username.setFont(QFont('Arial', 15))

        # Password input
        self.password = PasswordEdit()
        self.password.setPlaceholderText('Password')
        self.password.setObjectName("input_field")
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
        self.email.setObjectName("input_field")
        self.email.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(ui_support_functions.handle_button_style(True, ui_support_functions.color_dic["sign_up_page"]["submit_button_color"]["normal"], ui_support_functions.color_dic["sign_up_page"]["submit_button_color"]["focus"], underline_flag=False))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_submit)

        # already have an account?
        got_account = QPushButton('Already have an account?')
        got_account.setStyleSheet(ui_support_functions.handle_button_style(False, "transparent", 'green',  underline_flag=True))
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

        result = self.query.get_userID(username_local)

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

        # random salt
        crypto = cryptography()

        salt = os.urandom(32)
        wrapping_key = crypto.generate_key(password_local, salt)
        data_key = base64.urlsafe_b64encode(secrets.token_bytes(32))
        encrypted_data_key = crypto.encrypt_data_key(wrapping_key, data_key)

        hashed_password = password_manager.hash_password(password_local)
        self.query.insert_user(username_local, hashed_password, email_local, encrypted_data_key, salt)
        self.controller.show_login()

class validation_page(QWidget):
    def __init__(self, controller, login_page,  db, cursor):
        super().__init__()
        self.duration = 90
        self.time_left_int = self.duration
        self.timer = QTimer(self)
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
        palette.setColor(QPalette.Window, QColor(ui_support_functions.color_dic["validation_page"]['background_color']))
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
        title_color.setColor(QPalette.WindowText, QColor(ui_support_functions.color_dic["validation_page"]['title_color']))
        title.setPalette(title_color)

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(ui_support_functions.handle_button_style(True, ui_support_functions.color_dic["validation_page"]['submit_button_color']['normal'],ui_support_functions.color_dic["validation_page"]['submit_button_color']['focus'], underline_flag=False))
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
            square.setObjectName("digit_box")

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

        self.timer_manager = manage_seconds_qt(label=self.timerLabel, timer=self.timer, duration=self.duration, expire_func=self.expire_func)

    def expire_func(self):
        self.login_page.random_digits = self.system.send_reset_digits(
            6, username=self.login_page.username.text()
        )
        for square in self.squares:
            square.clear()

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
            QMessageBox.warning(
                self,
                'mismatch',
                'Codes dont not match"'
            )
            return

    def start_time(self):
        self.timer_manager.begin_timer()

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
        palette.setColor(QPalette.Window, QColor(ui_support_functions.color_dic["reset_password"]["background_color"]))
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
        title_color.setColor(QPalette.WindowText, QColor(ui_support_functions.color_dic["reset_password"]["title_color"]))
        title.setPalette(title_color)

        # New Password input
        self.password_1 = PasswordEdit()
        self.password_1.setPlaceholderText('New Password')
        self.password_1.setObjectName("input_field")

        self.password_1.setFont(QFont('Arial', 15))

        # Retype New Password
        self.password_2 = PasswordEdit()
        self.password_2.setPlaceholderText('Re-type New Password')
        self.password_2.setObjectName("input_field")
        self.password_2.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(ui_support_functions.handle_button_style(True, ui_support_functions.color_dic["reset_password"]["submit_button_color"]['normal'], ui_support_functions.color_dic["reset_password"]["submit_button_color"]['focus'], underline_flag=False))
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
        password_manager  = password_class()
        query = query_processor()
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
            username = self.login_page.username.text()
            new_password = self.password_1.text()
            userID = query.get_userID(username)
            password_manager.change_password(userID,new_password)
            # create new key and everything

            # random salt
            crypto = cryptography()

            new_salt = os.urandom(32)
            new_wrapping_key = crypto.generate_key(new_password, new_salt)
            new_data_key = base64.urlsafe_b64encode(secrets.token_bytes(32))
            new_encrypted_data_key = crypto.encrypt_data_key(new_wrapping_key, new_data_key)
            query.change_data_key_salt(new_encrypted_data_key, new_salt, userID)
            self.controller.show_login()

class User_authentication(QMainWindow):
    def __init__(self):
        super().__init__()

        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

        self.django_setup()

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

        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.sign_up_page)
        self.stacked_widget.addWidget(self.validation_page)
        self.stacked_widget.addWidget(self.reset_password)

    def show_dashboard(self, key, userID):
        self.main_window = MainWindow(self, key, userID)
        self.main_window.show()
        self.close()

    def show_login(self):
        self.stacked_widget.setCurrentWidget(self.login_page)
        self.setMaximumSize(400, 500)

    def show_sign_up(self):
        self.stacked_widget.setCurrentWidget(self.sign_up_page)
        self.setMaximumSize(400, 500)

    def show_validation_page(self):
        self.stacked_widget.setCurrentWidget(self.validation_page)
        self.setMaximumSize(400, 500)
        self.validation_page.start_time()

    def show_reset_password(self):
        self.stacked_widget.setCurrentWidget(self.reset_password)
        self.setMaximumSize(400, 500)

    # setting up django for authentication by email
    def django_setup(self):
        sys.path.insert(0, config("CURRENT_FOLDER"))
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        os.environ['SSL_CERT_FILE'] = certifi.where()
        os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
        django.setup()

    def start_login(self):
        self.login = User_authentication()
        self.login.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # reading style file
    style_path = os.path.join(os.path.dirname(__file__), "style_resource", "style.qss")
    with open(style_path, 'r') as styling:
        style = styling.read()

    app.setStyleSheet(style)
    window = User_authentication()
    window.show()

    sys.exit(app.exec())