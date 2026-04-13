import random
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from database_connection import database
from queries import query_processor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.image import imread
from pathlib import Path
from datetime import datetime

class system_functions:

    """
    Manages the functions for authentication the user
    """

    def __init__(self):
        connection = database()
        self.db = connection.db
        self.query = query_processor()
        self.cursor = connection.cursor

    # Generates random digits for user authentication for 2FA
    def generate_random_digits(self, digits_size):
        digits_string = ''
        for i in range(digits_size):
            number = random.randint(0, 9)
            digits_string+=str(number)

        return digits_string

    # https://sendlayer.com/blog/how-to-send-email-with-django/
    # Sends the random digits the users email
    def send_reset_digits(self, digits_size, username=None, userID=None):
        try:
            if username:
                email_query = "SELECT email_address FROM users WHERE username = %s"
                self.cursor.execute(email_query, (username, ))
                user_email = self.cursor.fetchone()[0]

            if userID:
                user_email = self.query.get_user_info(userID)[1]

            number = self.generate_random_digits(digits_size)
            subject = "Reset Password"
            html_message = render_to_string('registration/reset_form.html', {
                'user_email': user_email,
                'site_name': 'Finance App',
                'number': number
            })

            email = EmailMessage(
                subject=subject,
                body=html_message,
                from_email='batzayabtrdn@gmail.com',
                to=[user_email]
            )
            email.content_subtype = 'html'
            email.send()
            print("random digits is successfully sent")
            print(number)
            return number
        except:
            return None

    # https://www.youtube.com/watch?v=JjamKgAmB-4&t=273s
    def create_pdf(self, account_name, df):
        # Source - https://stackoverflow.com/a/62662388
        current_time = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{account_name}_financial_report_{current_time}.pdf"
        file_path = str(Path.home() / "Downloads"/file_name)

        df = df.iloc[:, 3:]
        rows_count = 9
        with PdfPages(file_path) as pdf:
            for mark in range(0, len(df), rows_count):
                section = df.iloc[mark:mark + rows_count]
                _, ax = plt.subplots(figsize=(8, 6))

                info = ax.table(cellText= section.values, colLabels=section.columns, loc='center')
                ax.axis('off')
                info.set_fontsize(30)
                info.scale(1.2,2.5)
                pdf.savefig()

    def create_csv(self, account_name, df):
        df = df.iloc[:, 3:]
        # Source - https://stackoverflow.com/a/45141782
        current_time = datetime.now().strftime("%Y-%m-%d")
        file_name = f"{account_name}_financial_report_{current_time}.csv"
        file_path = str(Path.home() / "Downloads"/file_name)
        df.to_csv(file_path, sep=',', encoding='utf-8', index=False, header=True)


class manage_seconds_qt():
    def __init__(self, label, timer, duration, expire_func=None):
        self.duration = duration
        self.timer = timer
        self.label = label
        self.expire_func = expire_func
        # Update the timer
        self.timer.timeout.connect(self.time_out)

    def begin_timer(self):
        self.remaining = self.duration
        self.timer.start(1000)

    def time_out(self):
        self.remaining -= 1
        if self.remaining == 0:
            self.remaining = self.duration
            if self.expire_func:
                self.expire_func()
        self.update_label()

    def update_label(self):
        time = self.convert_secs(self.remaining)
        self.label.setText(time)

    def convert_secs(self, seconds):
        return f'{seconds // 60:02}:{seconds % 60:02}'