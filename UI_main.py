import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
import mysql.connector
from database_connection import database
from BASE_Classes import password_class
from qtwidgets import PasswordEdit
from system_functions import system_functions
import os
import certifi
import sys
from system_functions import system_functions
from functools import partial


system = system_functions()
# Add the project root to Python path
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
    
forgot_button_style = '''
    QPushButton {
        background-color: transparent;
        color: white;
        border: none;
        text-decoration: underline;
        font-size: 15px;
    }
    QPushButton:hover {
        color: green;
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
def handle_button_style(button_color, hover_color):
        line = f'''
            QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                border-radius: 25px;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        '''
        return line

class login_page(QWidget):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.system = system_functions()

        self.user_interface()
        
    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Finance Login')
        self.setFixedSize(400, 500)
        
        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("dark"))
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
        title_color.setColor(QPalette.WindowText, QColor("limegreen"))
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
        login_btn.setStyleSheet(handle_button_style("limegreen", "springgreen"))
        login_btn.setFont(QFont('Arial', 15, QFont.Bold))
        login_btn.setFixedHeight(50)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        
        # sign up button
        signup_btn = QPushButton('Create new account')
        signup_btn.setStyleSheet(handle_button_style("#1877F2", "#18d5f2"))
        signup_btn.setFont(QFont('Arial', 15, QFont.Bold))
        signup_btn.setFixedHeight(50)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.clicked.connect(self.handle_sign_up)

        # Forgot password link
        forgot_password = QPushButton('Forgotten password?')
        forgot_password.setStyleSheet(forgot_button_style)
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
        
        email_query = "SELECT email_address FROM users WHERE username = %s"
        self.cursor.execute(email_query, (username_local, ))
        email_user = self.cursor.fetchone()[0]

        self.random_digits = self.system.send_reset_digits(6, email_user)
        print(self.random_digits)

        self.controller.show_reset_form()
        """        QMessageBox.information(
            self, 
            'Password Reset', 
            f'A password reset link has been sent to the email associated with username: {username_local}'
        )"""
    def get_random_digits(self):
        return self.random_digits
    
    def get_username(self):
        return self.username.text()

class reset_from_page(QWidget):
    def __init__(self, controller, login_page):
        super().__init__()
        self.controller = controller
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.login_page = login_page
        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Reset Password')
        self.setFixedSize(400, 500)
        
        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("dark"))
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
        title_color.setColor(QPalette.WindowText, QColor("#1877F2"))
        title.setPalette(title_color)


        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(handle_button_style("#1877F2", "#18d5F2"))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_reset_password)

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
        if (self.login_page.get_random_digits() == entered):
            self.controller.show_reset_password()
        else:
            QMessageBox.information(
                self, 
                'Code does not match', 
                'Please try again"'
            )
            return

class reset_password(QWidget):

    def __init__(self, controller, login_page):
        super().__init__()
        self.controller = controller
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.login_page = login_page

        self.user_interface()

    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Enter New Password')
        self.setFixedSize(400, 500)
        
        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("dark"))
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
        title_color.setColor(QPalette.WindowText, QColor("#1877F2"))
        title.setPalette(title_color)

        # New Password input
        self.password_1 = PasswordEdit()
        self.password_1.setPlaceholderText('New Password')
        self.password_1.setStyleSheet(input_style)
        self.password_1.setFont(QFont('Arial', 15))

        # Retype New Password
        self.password_2 = PasswordEdit()
        self.password_2.setPlaceholderText('New Password')
        self.password_2.setStyleSheet(input_style)
        self.password_2.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(handle_button_style("#1877F2", "#18d5F2"))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.compare_password)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.password_1)
        layout.addWidget(self.password_2)
        layout.addWidget(submit_btn)
        layout.addStretch()
        
        self.setLayout(layout)

    def compare_password(self):
        if self.password_1.text() == self.password_2.text():
           print("New Password Matches")

           password_manager = password_class()

           hashed_password = password_manager.hash_password(self.password_1.text())
           username = self.login_page.get_username()
           
           query = "UPDATE users SET hashed_password = %s WHERE username = %s"
           self.cursor.execute(query, (hashed_password, username))
           self.db.commit()

           self.controller.show_login()
        else:
            QMessageBox.information(
                self, 
                'Password do not match', 
                'Check your password again"'
            )
            return

class sign_up_page(QWidget):

    # https://doc.qt.io/qt-6/stylesheet-reference.html

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

        self.user_interface()
        
    def user_interface(self):
        # set the size and name
        self.setWindowTitle('Sign Up')
        self.setFixedSize(400, 500)
        
        # set the color of the background 
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("dark"))
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
        title_color.setColor(QPalette.WindowText, QColor("#1877F2"))
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

        # email input
        self.email = QLineEdit()
        self.email.setPlaceholderText('Email')
        self.email.setStyleSheet(input_style)
        self.email.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(handle_button_style("#1877F2", "#18d5F2"))
        submit_btn.setFont(QFont('Arial', 15, QFont.Bold))
        submit_btn.setFixedHeight(50)
        submit_btn.setCursor(Qt.PointingHandCursor)
        submit_btn.clicked.connect(self.handle_submit)
        
        # already have an account?
        got_account = QPushButton('Already have an account?')
        got_account.setStyleSheet(forgot_button_style)
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
            QMessageBox.warning(self, 'Error', 'Please enter both of the credentials, thank you')
            return
        
        if not result:
            try:
                hashed_password = password_manager.hash_password(password_local)
                new_sql = f"INSERT INTO users (username, hashed_password, email_address) VALUES (%s, %s, %s)"
                self.cursor.execute(new_sql, (username_local, hashed_password, email_local))
                self.db.commit()
                self.controller.show_login()
                print("Credentials added successfully")
            except:
                print("could not commit")
        else:
            QMessageBox.warning(self, 'Error', 'Username already exists, please try another username')
            return

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Finance Reporter")
        self.setFixedSize(400, 500)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.login_page = login_page(self) 
        self.sign_up_page = sign_up_page(self)

        #  # adding reset form page
        self.reset_form = reset_from_page(self, self.login_page)
        self.reset_password = reset_password(self, self.login_page)
        self.dashboard_page = QWidget()

        self.setup_dashboard()

        self.stacked_widget.addWidget(self.login_page)    
        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.sign_up_page)
        self.stacked_widget.addWidget(self.reset_form)
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
    
    def show_reset_form(self):
        self.stacked_widget.setCurrentIndex(3)
        self.setMaximumSize(400, 500)

    def show_reset_password(self):
        self.stacked_widget.setCurrentIndex(4)
        self.setMaximumSize(400, 500)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    main_window = MainApp()
    main_window.show()
    
    sys.exit(app.exec_())