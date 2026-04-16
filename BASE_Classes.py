import dateutil.parser
from database_connection import database
from datetime import datetime
from queries import query_processor
import bcrypt
import pandas as pd
from fuzzywuzzy import fuzz
import numpy as np
from cryptography.fernet import Fernet
import os
from database_connection import database
import base64
from Crypto.Hash import SHA256
from hashlib import pbkdf2_hmac
import re
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from Crypto.Cipher import ARC4 
class ParsingBase:

    """
    Contains shared functions used for parsing different types of user transaction files(pdf, csv)
    """

    def __init__(self):
        # The list defining the target columns of the input files that should be extracted
        # The nested list contains different forms of the target word
        self.expecting = [["Date"], ["Type" , "Category"], [ "Details", "Description", "Reference", "Narrative"], ["Money Out", "Paid Out", "Debit" "Debit Amount", "Withdrawal"], ["Money In", "Paid In", "Credit", "Credit Amount", "Received", "Deposit"], ["Balance"]]

        # Different abbreviations of the transaction type 'card payment'
        self.card = {'DEB', ')))', 'VIS', 'Card payment', 'Debit Card Transaction', 'DD'}

        # Different abbreviations of the transaction type 'atm'
        self.atm = {'CPT', 'PIM', 'ATM', 'Cash withdrawal'}

        # Different abbreviations of the transaction type 'fast payment'
        self.fast_payment = {'FPO', 'BP', 'Mobile/Online Transaction',  'FPI', 'Faster payment'}

        # Different abbreviations of the transaction type 'fast payment'
        self.salary = {'BGC', 'GIRO'}
        self.general_in ={'Automated Credit'}
        self.refund = {'CR'}

    # Classifies the type of the transaction
    def classify_transaction_type(self, transaction_type):
        if (transaction_type in self.card):
            return 'Deposit'
        elif (transaction_type in self.atm):
            return 'ATM'
        elif (transaction_type in self.fast_payment):
            return 'Fast Payment'
        elif (transaction_type in self.fast_payment):
            return 'Salary'
        elif (transaction_type in self.general_in):
            return 'General Credit'
        elif (transaction_type in self.refund):
            return 'Refund'
        else:
            return transaction_type

    # Checks the datetime version of the date values
    def check_date_type(self, test_date):
        try:
            datetime.strptime(test_date, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    # https://stackoverflow.com/questions/52206973/convert-different-date-formats-to-a-given-unique-date-format-in-python
    # Conforms date column into a standard form (%d/%m/%Y)
    def change_type(self, test_date, column, dataframe):
        if not self.check_date_type(test_date):
            for i in column:
                column = column.replace([i], dateutil.parser.parse(i).strftime("%d/%m/%Y"))
        dataframe[dataframe.columns[0]] = column

    # Standardizes the amount columns (removing non-conforming values)
    def unify_amount_columns(self, df):
        new_df = df.copy()
        length = len(df.columns)
        if (length == 6):
            new_df[new_df.columns[-3]] = pd.to_numeric(new_df[new_df.columns[-3]], errors='coerce')
            new_df[new_df.columns[-2]] = pd.to_numeric(new_df[new_df.columns[-2]], errors='coerce')

            # needs to algin the columns
            corrected = (abs(new_df[new_df.columns[-2]].fillna(0)) - abs(new_df[new_df.columns[-3]].fillna(0)))
            pos = len(new_df.columns) - 3
            new_df.insert(pos, "Unified_Amount", corrected)
            new_df.drop(columns=[new_df.columns[-3], new_df.columns[-2]], inplace=True)
        else:
            new_df[new_df.columns[-2]] = pd.to_numeric(new_df[new_df.columns[-2]], errors='coerce').fillna(0)
        return new_df

    # Checks if the target columns are selected, if not, plugs in default values depending on the type
    def order_dataframe(self, df, columns):
        missing = sorted(list(set(range(7)) - set(columns)))
        if (not missing):
            return df
        new_df = df.copy()
        extra = 0
        for i in missing:
            pos = i + extra
            if (i == 1):
                new_df.insert(pos, "Type", "Unknown")
            elif (i == 2):
                new_df.insert(pos, "Description", "Unknown")
            elif(i == 5):
                new_df.insert(pos, "Balance", 0)
        return new_df

    # Finds the target columns names by computing the partial ratios (the overlapping ratio of the word with the target)
    # Selects the the columns names with the highest ratio
    def choose_ratio(self, columns):
        mat1 = [None]*len(self.expecting)
        used = set()
        chosen_columns = []

        # list for debug
        result_list = []
        above = 50
        for idx, i in enumerate(self.expecting):
            highest_column_name = None
            highest_column_index = None
            highest = -1

            score_list = [None]*len(i)
            for extra_idx,  j in enumerate(i):
                sub_list = []
                for sub_idx, column in enumerate(columns):
                    if (sub_idx in used):
                        continue

                    grade = fuzz.partial_ratio(j, column)
                    sub_list.append((column, grade))
                    if (grade > highest and grade > above):
                        highest = grade
                        highest_column_name = column
                        highest_column_index = sub_idx

                score_list[extra_idx] = sub_list

            result_list.append(score_list)
            if (highest_column_index is not None):
                mat1[idx] = highest_column_name
                chosen_columns.append(idx)
                used.add(highest_column_index)

        mat2 = []
        for i in mat1:
            if (i is not None):
                mat2.append(i)
        return mat2, chosen_columns

class password_class:

    """
    Contains functions for managing the password
    """

    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

    # https://stackoverflow.com/questions/74932694/checking-password-validation-in-python
    # Checks the composition of the password
    # The password must be at least 8 characters and should include a combination of numbers, letters and special characters (!$@%).
    def check_password_safety(self, password):
        if len(password) >= 8 and re.search(r"\d", password) and re.search(r"[A-Za-z]", password) and re.search(r"[!$@%]", password):
            return True
        else:
            return False

    # Hashes the input password
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Checks the stored hashed password with the user input when checking credentials
    def check_password(self, plain_text_password, hashed_password):
        password_byte = plain_text_password.encode('utf-8')
        hashed_password = hashed_password.encode('utf-8')

        return bcrypt.checkpw(password_byte, hashed_password)

    # Changes the user password in the database (hashed)
    def change_password(self, userID, new_password):
        hashed = self.hash_password(new_password)
        query = f"""
            UPDATE users
            SET hashed_password = %s
            WHERE userID = %s
        """
        self.cursor.execute(query, (hashed, userID))
        self.db.commit()
        print("changed the password successfully")
        return hashed

    # https://www.geeksforgeeks.org/python/check-if-email-address-valid-or-not-in-python/
    # Checks the validity of the input email by checking the composition requirements
    def check_email_validity(self, email):
        regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"

        if re.fullmatch(regex, email):
            return True
        return False

#https://stackoverflow.com/questions/66218337/encrypt-and-protect-file-with-python
#https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
class cryptography:

    """
    Contains functions for securing user files and accessing later
    """

    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.query = query_processor()

    # Produces the key used in encryption and decryption of the user files given  password
    def generate_key(self, password, salt):
        password = password.encode()
        hashed = pbkdf2_hmac("sha256", password, salt, 10000, dklen=32)
        return base64.urlsafe_b64encode(hashed)

    # Encrypts the user file (filename) from folder_path to the save_folder
    # Returns the unique file id
    def encrypt(self, save_folder, folder_path, filename, key, accountID, size_file, file_type):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'rb') as file:
            data = file.read()

        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)

        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        pure_filename = filename[:-4]
        new_filename = pure_filename + str(timestamp)

        destination = os.path.join(save_folder, new_filename)
        with open(destination, 'wb') as file:
            file.write(encrypted)

        file_ID = self.query.insert_into_files(accountID,  filename, new_filename, size_file, file_type)
        return file_ID
    
    def encrypt_data_key(self, wrapping_key, data_key):
        fernet = Fernet(wrapping_key)
        encrypted = fernet.encrypt(data_key)
        return encrypted.decode()
    
    def decrypt_data_key(self, wrapping_key, enc_data_key):
        enc_data_key = enc_data_key.encode()
        fernet = Fernet(wrapping_key)
        decrypted = fernet.decrypt(enc_data_key)
        return decrypted

    # Decrypts the user file given filename or hashed_filename
    def decrypt(self, enc_storage_path, key, accountID, filename=None, hashed_filename=None, fileID=None):
        if filename:
            # even if the account name is changed, ID would stay the same
            hashed_name = self.query.get_hashed_name(accountID, name_file=filename)
        elif hashed_filename:
            hashed_name = hashed_filename
        elif fileID:
            hashed_name = self.query.get_hashed_name(accountID, fileID=fileID)

        file_path = os.path.join(enc_storage_path,  hashed_name)
        with open(file_path, "rb") as file:
            data = file.read()

        fernet = Fernet(key)
        decrypted = fernet.decrypt(data)

        return decrypted