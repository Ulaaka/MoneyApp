import random
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from database_connection import database

class system_functions:
    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

    def generate_random_digits(self, digits_size):
        digits_string = ''
        for i in range(digits_size):
            number = random.randint(0, 9)
            digits_string+=str(number)

        return digits_string

    # https://sendlayer.com/blog/how-to-send-email-with-django/
    def send_reset_digits(self, digits_size, username):

        email_query = "SELECT email_address FROM users WHERE username = %s"
        self.cursor.execute(email_query, (username, ))
        user_email = self.cursor.fetchone()[0]

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

