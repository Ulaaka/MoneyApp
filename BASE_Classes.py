import dateutil.parser
from database_connection import database
from datetime import datetime
from queries import query_processor
import bcrypt
import pandas as pd
from fuzzywuzzy import process, fuzz
from collections import defaultdict
import numpy as np
from cryptography.fernet import Fernet
import os
from database_connection import database
import base64
from Crypto.Hash import SHA256

class ParsingBase:
    def __init__(self):
        self.expecting = ["Date", ["Type" , "Category"], [ "Details", "Description", "Reference", "Narrative"], ["Out", "Credit Amount", "Withdrawal"], ["In", "Debit Amount", "Received", "Deposit"], "Balance"]

    # check the first value of the date list
    def check_date_type(self, test_date):
        try:
            datetime.strptime(test_date, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    # https://stackoverflow.com/questions/52206973/convert-different-date-formats-to-a-given-unique-date-format-in-python
    def change_type(self, test_date, column, dataframe):
        if not self.check_date_type(test_date):

            for i in column:
                column = column.replace([i], dateutil.parser.parse(i).strftime("%d/%m/%Y"))
        dataframe[dataframe.columns[0]] = column

    # need to do more debugging 
    def unify_amount_columns(self, df):
        same = df[df.columns[-2]].equals(df[df.columns[-3]])
        
        if same:
            # since both columns are identical, even the name , needed to drop using iloc
            # https://stackoverflow.com/questions/33045364/how-to-select-columns-by-position-in-pandas
            columns = list(range(len(df.columns)))
            columns.pop(-2)
            df = df.iloc[:, columns]

        else:

            df[df.columns[-3]] = pd.to_numeric(df[df.columns[-3]], errors='coerce')
            df[df.columns[-2]] = pd.to_numeric(df[df.columns[-2]], errors='coerce')

            # needs to algin the columns
            corrected = (abs(df[df.columns[-2]].fillna(0)) - abs(df[df.columns[-3]].fillna(0)))
            pos = len(df.columns) - 3
            df.insert(pos, "Unified_Amount", corrected)
            df.drop(columns=[df.columns[-3], df.columns[-2]], inplace=True)
        
        return df

    def order_dataframe(self, df, columns):

        missing = sorted(list(set(range(6)) - set(columns)))

        if (not missing):
            return df
        print("missing values:\n")
        # print(missing)

        extra = 0
        for i in missing:
            pos = i + extra
            if (i == 1):
                df.insert(pos, "Type", "")
            elif (i == 2):
                df.insert(pos, "Description", "")
            elif(i == 5):
                df.insert(pos, "Balance", 0)
            else:
                raise Exception("Important column is not selected")
            extra+=1
        return df
    
    def choose_ratio(self, columns):
        mat1 = [0]*len(self.expecting)
        mat2 = []
        
        for idx, i in enumerate(self.expecting):
            if not isinstance(i, list):
                #mat1.append(process.extractOne(i, columns, scorer=fuzz.partial_ratio))
                mat1[idx] = process.extractOne(i, columns, scorer=fuzz.partial_ratio)
                
            else:
                group_results = []
                for j in i:
                    group_results.append(process.extractOne(j, columns, scorer=fuzz.partial_ratio))
                #mat1.append(group_results)
                mat1[idx] = group_results

        above = 60
        chosen_columns = []
        percentage = []
        for idx, i in enumerate(mat1):
            if not isinstance(i, list):
                if (i[1] > above):
                    mat2.append(i[0])
                    chosen_columns.append(idx)
                    percentage.append(i[1])
            else:
                highest = 0
                highIdx = None
                for sub_idx, j in enumerate(i):
                    if (j[1] > highest and j[1] >above):
                        highest = j[1]
                        highIdx = sub_idx

                if highIdx is not None:
                    element = i[highIdx][0]
                    mat2.append(element)
                    chosen_columns.append(idx)
                    percentage.append(highest)
        try:
            if (mat2[-1] == mat2[-2]):
                mat2.pop()
        except:
            print("The table is not related to transaction")
        # https://stackoverflow.com/questions/11236006/identify-duplicate-values-in-a-list-in-python

        Dict = defaultdict(list)
        for idx,item in enumerate(mat2):
            if (item not in [mat2[-3], mat2[-2]]):
                Dict[item].append(idx)

        indices = set()
        for key, value in Dict.items():
            if (len(value) > 1):
                max_value = 0
                max_ind = -1
                for i in value:
                    if (percentage[i] > max_value):
                        max_value = percentage[i]
                        max_ind = i

                indices = set(value) - {max_ind}
                
        for i in indices:
            chosen_columns.remove(i)
            mat2.pop(i)
        return mat2, chosen_columns


class password_class:
    
    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # later used to check the password
    def check_password(self, plain_text_password, hashed_password):
        return bcrypt.checkpw(plain_text_password, hashed_password)
    

# https://stackoverflow.com/questions/66218337/encrypt-and-protect-file-with-python
#https://stackoverflow.com/questions/42568262/how-to-encrypt-text-with-a-password-in-python
class cryptography:

    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.salt = b'HuhTengereesZayatai'
        self.query = query_processor()

    def generate_key(self, password):
        hashed = SHA256.new(password.encode()).digest()
        return base64.urlsafe_b64encode(hashed)

    def encrypt(self, save_folder, folder_path, filename, password, username, account_name):

        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'rb') as file:
            data = file.read()

        key = self.generate_key(password)
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)

        new_filename = filename[:-4] + str(datetime.now())

        destination = os.path.join(save_folder, new_filename)
        with open(destination, 'wb') as file:
            file.write(encrypted)
 
        userID = self.query.get_userID(username)
        accountID = self.query.get_accountID(account_name, userID)

        new_query = "INSERT INTO files (accountID, file_name, hashed_name) VALUES (%s, %s, %s)"
        self.cursor.execute(new_query, (accountID,  filename, new_filename))
        file_ID = self.cursor.lastrowid
        self.db.commit()
        return file_ID

        # file needs to be deleted from the original folder

    def decrypt(self, enc_storage_path, filename, password, username, account_name):

        userID = self.query.get_userID(username)
        accountID = self.query.get_accountID(account_name, userID)
        hashed_filename = self.query.get_hashed_name(accountID, filename)

        file_path = os.path.join(enc_storage_path, hashed_filename)


        with open(file_path, "rb") as file:
            data = file.read()

        key = self.generate_key(password)

        fernet = Fernet(key)

        decrypted = fernet.decrypt(data)

        print(decrypted)


