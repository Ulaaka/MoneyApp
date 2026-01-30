import mysql.connector
from database_connection import database
from BASE_Classes import password_class
from datetime import datetime
from decimal import Decimal

import pandas as pd


class ProcessingDF:

    def __init__(self, df, username, password, email,  account_name, account_type, account_currency):

        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

        self.username = username
        self.password = password
        self.email = email
        self.acc_name = account_name
        self.acc_type = account_type
        self.acc_currency = account_currency

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
        for i in range(len(dtb)):
            row = dtb.iloc[i].tolist()
            row_str = list(map(str, row))
            self.insert_user(row_str)
        self.db.commit()


    def insert_user(self, row):
        password_manager = password_class()
        sql = f"SELECT userID FROM users WHERE username = %s"
        self.cursor.execute(sql, (self.username,))
        result = self.cursor.fetchone()
        
        if not result: 
            hashed_password = password_manager.hash_password(self.password)

            new_sql = f"INSERT INTO users (username, hashed_password, email_address) VALUES (%s, %s, %s)"
            self.cursor.execute(new_sql, (self.username, hashed_password, self.email))
            userID = self.cursor.lastrowid
        else:
            userID = result[0]
        self.insert_account(userID, row)

    def insert_account(self, userID, row):
        sql = f"SELECT accountID FROM accounts WHERE account_name = %s and userID = %s"
        self.cursor.execute(sql, (self.acc_name, userID))
        result = self.cursor.fetchone()

        if not result:
            new_sql = f"INSERT INTO accounts (userID, account_name, account_type, account_currency) VALUES (%s, %s, %s, %s)"
            self.cursor.execute(new_sql, (userID, self.acc_name, self.acc_type, self.acc_currency))

            accountID = self.cursor.lastrowid
        else:
            accountID = result[0]

        self.insert_transaction(accountID, row)

    def insert_transaction(self, accountID, row):
        # ["Date", ["Type" , "Category"], [ "Details", "Description", "Reference", "Narrative"], ["Credit Amount", "Withdrawal", "Out"], ["In", "Debit Amount", "Received", "Deposit"], "Balance"]

        sql = f"SELECT 1 FROM transactions WHERE accountID = %s AND transaction_date = %s AND transaction_type = %s AND description = %s AND amount = %s AND balance = %s"

        self.cursor.execute(sql, (accountID, self.change_to_date(row[0]), row[1], row[2], Decimal(row[3]), Decimal(row[4])))
        result = self.cursor.fetchone()

        if not result:
            try:
                sql = f"INSERT INTO transactions (accountID, transaction_date, transaction_type, description, amount, balance) VALUES (%s,%s,%s,%s,%s,%s)"
                self.cursor.execute(sql, (accountID, self.change_to_date(row[0]), row[1], row[2], Decimal(row[3]),  Decimal(row[4])))
            except:
                print("the value doesnt match")

    def change_to_date(self, date_string):
        date = datetime.strptime(date_string, "%d/%m/%Y")
        return date






