import random, os, matplotlib.pyplot as plt
from decouple import config
from matplotlib.backends.backend_pdf import PdfPages
from pathlib import Path
from datetime import datetime

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from db_connection import Database
from db_queries import QueryProcessor
from base_classes import CryptoHelper
class SystemHelpers:

    """
    Manages the functions for system helper functions
    """

    def __init__(self):
        connection = Database()
        self.db = connection.db
        self.query = QueryProcessor()
        self.cursor = connection.cursor
        self.crypto = CryptoHelper()

    def generate_random_digits(self, digits_size):
        """
        Generates random digits for user authentication for two factor verification
        :param digits_size: the size of confirmation code
        :return: random confirmation code as a string
        """
        digits_string = ''
        for i in range(digits_size):
            number = random.randint(0, 9)
            digits_string+=str(number)

        return digits_string

    def send_reset_digits(self, digits_size, username=None, userID=None):
        """
        Sends random confirmation code of dynamic size to the user's registered email
        Inspired from:
        https://sendlayer.com/blog/how-to-send-email-with-django/

        :param digits_size: the number of digits to send
        :return: the sent random code
        """
        try:
            if username:
                email_query = "SELECT email_address FROM users WHERE username = %s"
                self.cursor.execute(email_query, (username, ))
                user_email = self.cursor.fetchone()[0]

            if userID:
                user_email = self.query.get_user_info(userID)[1]

            number = self.generate_random_digits(digits_size)
            subject = "Reset Password"
            html_message = render_to_string('reset_form.html', {
                'user_email': user_email,
                'site_name': 'Finance App',
                'number': number
            })

            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email=config('EMAIL_HOST_USER'),
                to=[user_email]
            )
            email.content_subtype = 'html'
            email.send()
            print(number)
            return number
        except:
            return None

    def create_pdf(self, account_name, df):
        """
        Downloads pdf file to the user's download folder
        """
        current_time = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{account_name}_financial_report_{current_time}.pdf"
        file_path = str(Path.home() / "Downloads"/file_name)

        df = df.iloc[:, 3:]
        rows_count = 9
        with PdfPages(file_path) as pdf:
            for mark in range(0, len(df), rows_count):
                section = df.iloc[mark:mark + rows_count]
                fig, ax = plt.subplots(figsize=(8, 6))

                info = ax.table(cellText= section.values, colLabels=section.columns, loc='center')
                ax.axis('off')
                info.set_fontsize(20)
                info.scale(1.2,2.5)
                pdf.savefig(fig)
                plt.close(fig) 

    def create_csv(self, account_name, df):
        """
        Downloads csv file to the user's download folder
        """
        df = df.iloc[:, 3:]
        current_time = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{account_name}_financial_report_{current_time}.csv"
        file_path = str(Path.home() / "Downloads"/file_name)
        df.to_csv(file_path, sep=',', encoding='utf-8', index=False, header=True)

    def set_select_dates(self, transactions):
        """
        Finds the minimum and maximum date of the given transaction list
        As well as ordering the transaction

        :param transactions: list of transaction
        :return: minimum, maximum date and ordered transaction list
        """
        if transactions is None:
            return
        transactions = transactions.sort_values(by=transactions.columns[3], ascending=False)
        date_list = transactions.iloc[:, 3].tolist()

        if len(date_list) == 0:
            min_date = None
            max_date = None
            return

        min_date = min(date_list).date()
        max_date = max(date_list).date()
        return min_date, max_date, transactions

    def update_data_key(self, prev_password, next_password, userID):
        """
        Updates the encrypted data key and salt in the database

        :param prev_password: old password
        :param next_password: new password
        :param userID: user ID
        :return: new encrypted data key, and new salt
        """
        enc_data_key, salt = self.query.get_data_key_salt(userID)
        wrapping_key = self.crypto.generate_key(prev_password, salt)
        data_key = self.crypto.decrypt_data_key(wrapping_key, enc_data_key)

        next_salt = os.urandom(32)
        next_wrapping_key = self.crypto.generate_key(next_password, next_salt)
        next_enc_data_key = self.crypto.encrypt_data_key(next_wrapping_key, data_key)
        return next_enc_data_key, next_salt

class TimerHelper():
    """
    Manages the countdown of confirmation page for user verification
    """
    def __init__(self, label, timer, duration, expire_func=None):
        """
        Constructor for confirmation countdown manager
        """

        # Duration of confirmation time in secs
        self.duration = duration

        self.timer = timer

        # Countdown Label
        self.label = label

        # Function to active when time runs out
        self.expire_func = expire_func
        # Update the timer
        self.timer.timeout.connect(self.time_out)

    def begin_timer(self):
        """
        Starts the timer, let it tick by a sec
        """
        self.remaining = self.duration
        self.timer.start(1000)

    def time_out(self):
        """
        Counts the remaining time down
        """
        self.remaining -= 1
        if self.remaining == 0:
            self.remaining = self.duration
            if self.expire_func:
                self.expire_func()
        self.update_label()

    def update_label(self):
        """
        Updates the label with formatted time
        """
        time = self.convert_secs(self.remaining)
        self.label.setText(time)

    def convert_secs(self, seconds):
        """
        Formats the remaining time in format MIN:SECS
        :return: formatted seconds
        """
        return f'{seconds // 60:02}:{seconds % 60:02}'