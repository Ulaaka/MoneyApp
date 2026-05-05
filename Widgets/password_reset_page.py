import os,secrets,  base64

from PyQt5.QtWidgets import  QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette

from base_classes import PasswordHelper, CryptoHelper
from db_queries import QueryProcessor
from ui_helper import UserInterfaceHelper


class PasswordResetWindow(QWidget):
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
        palette.setColor(QPalette.Window, QColor(UserInterfaceHelper.color_dic["reset_password"]["background_color"]))
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
        title_color.setColor(QPalette.WindowText, QColor(UserInterfaceHelper.color_dic["reset_password"]["title_color"]))
        title.setPalette(title_color)

        # New Password input
        self.password_1 = QLineEdit()
        self.password_1.setEchoMode(QLineEdit.Password)
        self.password_1.setPlaceholderText('New Password')
        self.password_1.setObjectName("input_field")

        self.password_1.setFont(QFont('Arial', 15))

        # Retype New Password
        self.password_2 = QLineEdit()
        self.password_2.setEchoMode(QLineEdit.Password)
        self.password_2.setPlaceholderText('Re-type New Password')
        self.password_2.setObjectName("input_field")
        self.password_2.setFont(QFont('Arial', 15))

        # Login button
        submit_btn = QPushButton('Submit')
        submit_btn.setStyleSheet(UserInterfaceHelper.handle_button_style(True, UserInterfaceHelper.color_dic["reset_password"]["submit_button_color"]['normal'], UserInterfaceHelper.color_dic["reset_password"]["submit_button_color"]['focus'], underline_flag=False))
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
        password_manager  = PasswordHelper()
        query = QueryProcessor()
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
            username = self.login_page.username.text()
            new_password = self.password_1.text()
            userID = query.get_userID(username)
            password_manager.change_password(userID,new_password)

            # create new wrapping key and salt from new password
            # random salt
            crypto = CryptoHelper()

            new_salt = os.urandom(32)
            new_wrapping_key = crypto.generate_key(new_password, new_salt)

            _, _, encrypted_data_key_server = query.get_data_key_salt(userID)
            _, private_key = crypto.retrieve_keys_pem()
            data_key = crypto.decrypt_rsa(encrypted_data_key_server, private_key)

            new_encrypted_data_key = crypto.encrypt_data_key(new_wrapping_key, data_key)
            query.update_key_salt(new_encrypted_data_key, new_salt, userID)
            self.controller.show_login()
