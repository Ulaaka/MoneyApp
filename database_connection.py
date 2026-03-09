import mysql.connector
from decouple import config

class database:

    def __init__(self):

        self.db = mysql.connector.connect(
            host = config('DATABASE_HOST'),
            user = config('DATABASE_USER'),
            password = config('DATABASE_PASSWORD'),
            database =config('DATABASE_NAME')
        )

        self.cursor = self.db.cursor(buffered=True)

db  = database()