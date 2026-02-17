from database_connection import database
from BASE_Classes import password_class, ParsingBase
from datetime import datetime
from decimal import Decimal
from queries import query_processor
import pandas as pd


class ProcessingDF:
    def __init__(self, df, username, password, email,  account_name, account_type, file_ID, account_currency):

        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

        self.query = query_processor()

        self.username = username
        self.password = password
        self.email = email
        self.acc_name = account_name
        self.acc_type = account_type
        self.acc_currency = account_currency
        self.file_ID = file_ID

        if isinstance(df, list):
            for i in df:
                self.insert_all(i)
        else:
            self.insert_all(df)

    def delete_user(self):
        """
        All data relating to the user is deleted
        """
        sql = f"DELETE FROM users WHERE username = %s"
        self.cursor.execute(sql, (self.username,))
        self.db.commit()

    def insert_all(self, dtb):
        userID = self.query.insert_user(self.username, self.password, self.email)
        accountID = self.query.insert_account(userID, self.acc_name, self.acc_type, self.acc_currency)
        dtb.apply(lambda row: self.insert_transaction(userID=userID, accountID=accountID, row=row), axis=1)

    def insert_transaction(self, userID, accountID, row):
        parser = ParsingBase()
        query = query_processor()

        row = list(map(str, row.tolist()))
        word_list = query.return_word_list(row[2])[1]
        
        output = query.get_category(userID, word_list)
        if (output is None):
            category = "Undefined"
        else:
            category = output[1]

        sql = f"SELECT 1 FROM transactions WHERE accountID = %s AND file_ID = %s AND transaction_date = %s AND transaction_type = %s AND description = %s AND category = %s AND amount = %s AND balance = %s"
        self.cursor.execute(sql, (accountID, self.file_ID, self.change_to_date(row[0]), row[1], row[2], category, Decimal(row[3]),  Decimal(row[4])))
        result = self.cursor.fetchone()

        if not result:
            row[1] = parser.classify_transaction_type(row[1])
            self.query.insert_into_transactions(accountID, self.file_ID, self.change_to_date(row[0]), row[1], row[2], category, Decimal(row[3]),  Decimal(row[4]))

    def change_to_date(self, date_string):
        date = datetime.strptime(date_string, "%d/%m/%Y")
        return date


