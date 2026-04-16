import dateutil.parser, os, base64, re, bcrypt, pandas as pd
from datetime import datetime
from fuzzywuzzy import fuzz
from cryptography.fernet import Fernet
from hashlib import pbkdf2_hmac

from db_connection import Database
from db_queries import QueryProcessor

#from Crypto.Hash import SHA256
class ParsingHelper:

    """
    Contains shared functions used for parsing different types of transaction files(pdf, (HSBC pdf), csv)
    """

    def __init__(self):
        """
        Constructor for the parser helper.
        """

        """
        Each nested list of the instance variable holds possible variation of the column name to be extracted
        The ordering of the nested lists dictates the final ordering of the dataframe columns
        """
        self.expecting = [["Date"], ["Type" , "Category"], [ "Details", "Description", "Reference", "Narrative"], 
            ["Money Out", "Paid Out", "Debit" "Debit Amount", "Withdrawal"], 
            ["Money In", "Paid In", "Credit", "Credit Amount", "Received", "Deposit"], ["Balance"]]


        self.card = {'DEB', ')))', 'VIS', 'Card payment', 'Debit Card Transaction', 'DD'}
        self.atm = {'CPT', 'PIM', 'ATM', 'Cash withdrawal'}
        self.fast_payment = {'FPO', 'BP', 'Mobile/Online Transaction',  'FPI', 'Faster payment'}
        self.salary = {'BGC', 'GIRO'}
        self.general_in ={'Automated Credit'}
        self.refund = {'CR'}

    def classify_transaction_type(self, transaction_type):
        """
        Classifies the type of transaction, name of the type does not exist, makes it its own type
        """

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

    def check_date_type(self, test_date):
        """
        Checks the format of the datetime, used to standardise the format
        """
        try:
            datetime.strptime(test_date, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def change_date_type(self, test_date, column, dataframe):
        """
        Conforms date column into a standard form (%d/%m/%Y)
        inspired from:
        https://stackoverflow.com/questions/52206973/convert-different-date-formats-to-a-given-unique-date-format-in-python
        """
        if not self.check_date_type(test_date):
            for i in column:
                column = column.replace([i], dateutil.parser.parse(i).strftime("%d/%m/%Y"))
        dataframe[dataframe.columns[0]] = column

    def unify_amount_columns(self, df):
        """
        Amount column could be picked separately for Debit and Credit Amount
        as it differs from bank to bank. Therefore, by checking the length,it
        standardizes the amount columns (removing non-conforming values)

        :return: Dataframe with only one amount column
        """

        new_df = df.copy()
        length = len(df.columns)
        if (length == 6):
            new_df[new_df.columns[-3]] = pd.to_numeric(new_df[new_df.columns[-3]], errors='coerce')
            new_df[new_df.columns[-2]] = pd.to_numeric(new_df[new_df.columns[-2]], errors='coerce')

            corrected = (abs(new_df[new_df.columns[-2]].fillna(0)) - abs(new_df[new_df.columns[-3]].fillna(0)))
            pos = len(new_df.columns) - 3
            new_df.insert(pos, "Unified_Amount", corrected)
            new_df.drop(columns=[new_df.columns[-3], new_df.columns[-2]], inplace=True)
        else:
            new_df[new_df.columns[-2]] = pd.to_numeric(new_df[new_df.columns[-2]], errors='coerce').fillna(0)
        return new_df


    def order_dataframe(self, df, columns):
        """
        Checks if the target columns are selected, if not, plugs in default values depending on the type

        :return: complete ordered dataframe
        """

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

    def choose_ratio(self, columns):
        """
        Finds the target columns names by computing the partial ratios
        (the overlapping ratio of the word with the target/its variations)
        Ranks target variations by its score and selects the the columns names with the highest ratio

        Inspired from:
        https://www.geeksforgeeks.org/python/how-to-do-fuzzy-matching-on-pandas-dataframe-column-using-python/

        :returns: ratio_score, target column names of the file
        """
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

class PasswordHelper:

    """
    Contains functions for managing password
    """

    def __init__(self):

        """
        Constructor for the password helper.
        """

        connection = Database()
        self.db = connection.db
        self.cursor = connection.cursor

    # https://stackoverflow.com/questions/74932694/checking-password-validation-in-python
    # Checks the composition of the password
    # The password must be at least 8 characters and should include a combination of numbers, letters and special characters (!$@%).
    def check_password_safety(self, password):
        """
        Checks the composition of the password given the requirement

        /requirement/
        (The password must be at least 8 characters and should include a combination of numbers,
        letters and special characters (!$@%))
        """

        if len(password) >= 8 and re.search(r"\d", password) and re.search(r"[A-Za-z]", password) and re.search(r"[!$@%]", password):
            return True
        else:
            return False

    def hash_password(self, password):
        """
        :return: Hashed password
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, plain_text_password, hashed_password):
        """
        Checks the stored hashed password with the user input password
        :return: True or False
        """
        password_byte = plain_text_password.encode('utf-8')
        hashed_password = hashed_password.encode('utf-8')

        return bcrypt.checkpw(password_byte, hashed_password)

    def change_password(self, userID, new_password):
        """
        Updates the user password in the database (hashed)

        :param new_password: new password to hash
        :result: hashed new password
        """
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

    def check_email_validity(self, email):
        """
        Checks the validity of the input email

        Inspired from:
        https://www.geeksforgeeks.org/python/check-if-email-address-valid-or-not-in-python/
        """
        regex = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"

        if re.fullmatch(regex, email):
            return True
        return False

class CryptoHelper:
    """
    Contains functions for securing user files and accessing later
    """

    def __init__(self):
        """
        Constructor for cryptography manager
        """
        connection = Database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.query = QueryProcessor()

    def generate_key(self, password, salt):
        """
        Generates key used for wrapping main data key for encryption and decryption of the files
        :params password, salt: the combination of password and salt used to derive wrapping key from
        :return: wrapping key
        """
        password = password.encode()
        hashed = pbkdf2_hmac("sha256", password, salt, 10000, dklen=32)
        return base64.urlsafe_b64encode(hashed)

    def encrypt(self, save_folder, folder_path, filename, key, accountID, size_file, file_type):
        """
        encrypts different files from submission folder given unique user data key
        :param save_folder: folder to be saved to
        :param folder_path: folder to be encrypted from (submission)
        :param filename: name of the file
        :param accountID: id of the account to be associated with
        :param size_file: size of the file
        :param file_type; the type of file (csv, pdf, hsbc/pdf)

        :return: unique file id to locate from database
        """
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
        """
        Encrypts user data key with wrapping key to later save it in database

        :return: encrypted data key
        """
        fernet = Fernet(wrapping_key)
        encrypted = fernet.encrypt(data_key)
        return encrypted

    def decrypt_data_key(self, wrapping_key, enc_data_key):
        """
        Decrypts encrypted data with the wrapping key

        :return: user data key
        """
        fernet = Fernet(wrapping_key)
        decrypted = fernet.decrypt(enc_data_key)
        return decrypted

    def decrypt(self, enc_storage_path, key, accountID, filename=None, hashed_filename=None, fileID=None):
        """
        decrypts files from encrypted files folder given unique user data key and other identifications

        :param enc_storage_path: encrypted files  folder to be read from
        :param key: unique user data key for decryption
        :param accountID: id of the account associated with
        :param filename, hashed_filename, fileID: file identifications

        :return: decrypted text of the file
        """
        if filename:
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