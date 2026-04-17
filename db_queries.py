import re, pandas as pd, json
from datetime import datetime
from nltk.corpus import stopwords
from geotext import GeoText
from datetime import datetime

from db_connection import Database

class QueryProcessor:

    """
    Contains the functions for querying the database
    """

    def __init__(self):
        """
        Constructor for database querying class
        """

        # database connection
        self.connection = Database()
        connection = self.connection
        self.db = connection.db
        self.cursor = connection.cursor


        # Stop words in english language + custom
        # Later used to distinguish key words from description
        self.stop_words = set(stopwords.words('english'))
        new_stop_words = {'ltd', 'limited', 'inc', 'stores', 'gb', 'uk'}
        self.stop_words.update(new_stop_words)

    # ==========================   INSERT INTO QUERIES    =========================

    def insert_into_users(self, username, hashed_password, email, encrypted_data_key, salt):
        """
        Creates new user, and inserts user information into the database
        :param encrypted_data_key: encrypted version of data key used for cryptography of files
        :param salt: salt used for getting wrapping key for encrypt/decrypting data key

        :return: unique user ID
        """
        sql = "INSERT INTO users (username, hashed_password, email_address, enc_data_key, salt) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(sql, (username, hashed_password, email, encrypted_data_key, salt))
        # Unique user ID
        userID = self.cursor.lastrowid
        self.db.commit()
        return userID

    def insert_into_accounts(self, userID, acc_name, acc_type, acc_currency):
        """
        Creates new account, and inserts information into the database
        :param acc_name: name of the account
        :param acc_type: type of the account (fast payment, card etc)
        :param acc_currency: currency of the account
        :return: unique account ID
        """

        sql = "INSERT INTO accounts (userID, account_name, account_type, account_currency) VALUES (%s, %s, %s, %s)"
        self.cursor = self.connection.cursor
        self.cursor.execute(sql, ( userID, acc_name, acc_type, acc_currency))
        accountID = self.cursor.lastrowid
        self.db.commit()
        return accountID

    def insert_into_transactions(self, transaction_list):
        """
        Inserts transaction into the database
        To get a better querying runtime, transactions are given as a list to allow for executemany
        It ignores duplicate transactions (already exist in the database) by "INSERT IGNORE INTO"
        :param transaction_list: list of transactions to be inserted
        """

        "print"
        sql = """INSERT IGNORE INTO transactions (accountID, file_ID, transaction_date, transaction_type, description, category, amount, balance) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        self.cursor.executemany(sql, transaction_list)
        self.db.commit()

    def insert_into_categories(self, userID, accountID, category_sentence, category_list, category_name):
        """
        Creates new category, and inserts information into the database
        :param category_sentence: description of the category
        :param category_list: unique key-word list of the category
        :param category_name: name of the category
        :return: unique category ID
        """
        query = "INSERT INTO categories (userID, accountID, category_sentence, category_list, category_name) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(query, (userID, accountID, category_sentence, json.dumps(category_list), category_name))
        categoryID = self.cursor.lastrowid
        self.db.commit()
        return categoryID

    def insert_into_files(self, accountID,  filename, new_filename, size_file, file_type):
        """
        Creates new file, and inserts information into the database
        :param filename: name of the file
        :param new_filename: hashed name of the file
        :param size_file: the size of the file (B, KB etc)
        :param file_type: PDF or CSV
        :return: unique file ID
        """
        new_query = "INSERT INTO files (accountID, file_name, hashed_name, file_size, file_type) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(new_query, (accountID,  filename, new_filename, size_file, file_type))
        file_ID = self.cursor.lastrowid
        self.db.commit()
        return file_ID

    def insert_user(self, username, hashed_password, email, encrypted_data_key, salt):
        """
        New user insertion with check of if the user already exists 
        :return: unique user ID
        """
        userID = self.get_userID(username)
        if userID is None:
            try:
                userID = self.insert_into_users(username, hashed_password, email, encrypted_data_key, salt)
            except:
                print("could not insert the user")
        return userID

    def insert_account(self, userID, acc_name, acc_type, acc_currency):
        """
        New account insertion with check of if the account already exists 
        :return: unique account ID
        """
        accountID = self.get_accountID(acc_name, userID)
        if accountID is None:
            accountID = self.insert_into_accounts(userID, acc_name, acc_type, acc_currency)
        return accountID

    def insert_category(self, userID, accountID, category_sentence, category_list, category_name):
        """
        New category insertion with check of if the category already exists 
        :return: unique category ID
        """
        exist = True
        categoryID = self.get_matching_category(accountID, category_list)
        if categoryID is None:
            exist = False
            categoryID = self.insert_into_categories(userID, accountID, category_sentence, category_list, category_name)
        return categoryID, exist

    def get_category_info(self, userID, accountID, asDF=None):
        """
        Returns key category information
        If return as a dataframe, it is used for category table creation for the app
        :return: category information as a dataframe or list of tuples
        """
        sql_categories  = "SELECT categoryID, category_list, category_sentence, category_name FROM categories WHERE userID = %s and accountID = %s ORDER BY categoryID"
        self.cursor.execute(sql_categories, (userID, accountID))
        result = self.cursor.fetchall()
        if not asDF:
            return result if result else None
        else:
            header_columns = [column[0] for column in self.cursor.description]
            df = pd.DataFrame(result, columns=header_columns)
            return df

    def get_next_best_category(self, userID, accountID, category_list):
        """
        After category is deleted, finds the next best category to replace category names of related transactions

        :param category_list: given key-words list, it goes through existing categories to find the next best match
        :return: next best category or None if not successful
        """
        try:
            result = self.get_category_info(userID, accountID)

            category_dictionary = {tuple(json.loads(category_list)): (categoryID, category_name) for categoryID, category_list, _, category_name in result}

            priority_list = [(len([item for item in category_list if item in i]), len(i)) for i in category_dictionary]

            # the best next match
            max_category = max(priority_list, key=lambda x: (x[0], -x[1]))
            if max_category[0] == 0:
                return None

            position = priority_list.index(max_category)
            key = list(category_dictionary)[position]

            output = category_dictionary[key]
            return output
        except:
            return None

    def get_matching_category(self, accountID,  word_list):
        """
        Returns category ID given key-word list
        """
        query = "SELECT categoryID from categories WHERE category_list = %s and accountID = %s"
        self.cursor.execute(query, (json.dumps(word_list), accountID))
        output = self.cursor.fetchone()
        return output[0] if output else None

    def get_userID(self, username):
        """
        Returns user ID given username
        """
        sql = "SELECT userID FROM users WHERE username = %s"
        self.cursor.execute(sql, (username,))
        output = self.cursor.fetchone()
        return output[0] if output else None

    def get_accountID(self, account_name, userID):
        """
        Returns account ID given account name and user ID
        """
        sql = "SELECT accountID FROM accounts WHERE account_name = %s and userID = %s"
        self.cursor.execute(sql, (account_name, userID))
        output = self.cursor.fetchone()
        return output[0] if output else None

    def get_hashed_name(self, accountID, name_file=None, fileID=None):
        """
        Returns hashed name of the encrypted file by name of the file or file ID
        """
        if name_file:
            new_sql = "SELECT hashed_name FROM files WHERE accountID = %s and file_name = %s"
            selected = name_file
        if fileID:
            new_sql = "SELECT hashed_name FROM files WHERE accountID = %s and file_ID = %s"
            selected = fileID
        self.cursor = self.connection.cursor
        self.cursor.execute(new_sql, (accountID, selected))
        output = self.cursor.fetchone()
        return output[0] if output else None

    def get_transactions(self, accountID):
        """
        Returns total transactions made by the account given account ID
        """
        query = """SELECT * FROM transactions WHERE accountID = %s"""
        self.cursor = self.connection.cursor
        self.cursor.execute(query, (accountID,))
        output = self.cursor.fetchall()
        header_columns = [column[0] for column in self.cursor.description]
        df = pd.DataFrame(output, columns=header_columns)
        return df

    def get_hashed_password(self, username=None, userID=None):
        """
        Returns hashed password of the user given username or ID
        """
        if username:
            sql = "SELECT hashed_password FROM users WHERE username = %s"
            select = username
        elif userID:
            sql = "SELECT hashed_password FROM users WHERE userID = %s"
            select = userID
        self.cursor = self.connection.cursor
        self.cursor.execute(sql, (select, ))
        result = self.cursor.fetchone()
        return result if result else None

    def get_file_name(self, accountID, hashed_name=None, fileID=None):
        """
        Returns name of the file given hashed name or ID
        """
        if hashed_name:
            new_sql = "SELECT file_name FROM files WHERE accountID = %s and hashed_name = %s"
            select = hashed_name
        elif fileID:
            new_sql = "SELECT file_name FROM files WHERE accountID = %s and file_ID = %s"
            select = fileID
        self.cursor.execute(new_sql, (accountID, select))
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Returns accountID
    def get_file_ID(self, accountID, filename):
        """
        Returns ID of the file given corresponding account ID name and name of the file
        """

        sql = "SELECT file_ID FROM files WHERE accountID = %s AND file_name = %s"
        self.cursor.execute(sql, (accountID, filename))
        output = self.cursor.fetchone()
        return output[0] if output else None

    def get_files(self, accountID):
        """
        Returns information of the files associated with account ID
        """

        query = """
        SELECT file_ID, file_name, file_size, file_type, added_at
        FROM files
        WHERE accountID = %s
        ORDER BY added_at DESC
        """
        self.cursor = self.connection.cursor
        self.cursor.execute(query, (accountID,))
        result = self.cursor.fetchall()
        return result if result else None

    def get_type_account_currency(self, account_name, userID):
        """
        Returns type and currency of the account given name of the account and user ID
        """

        query = "SELECT account_type, account_currency FROM accounts WHERE account_name = %s AND userID = %s"
        self.cursor.execute(query, (account_name, userID))
        result = self.cursor.fetchone()
        return result if result else None

    def get_type_with_id(self, id):
        """
        Returns type of the account given file ID
        """
        query = "SELECT account_type FROM accounts WHERE file_ID = %s"
        self.cursor.execute(query, (id, ))
        result = self.cursor.fetchone()
        return result if result else None

    def get_create_update_account(self,  account_name, userID):
        """
        Returns timestamps of account given name of the account and user ID
        """
        query = "SELECT created_at, updated_at FROM accounts WHERE account_name = %s AND userID = %s"
        self.cursor.execute(query, (account_name, userID))
        result = self.cursor.fetchone()
        return result if result else None

    def get_user_info(self, userID):
        """
        Returns user information given user ID
        """
        query = "SELECT username, email_address, created_at FROM users WHERE userID = %s"
        self.cursor.execute(query, (userID,))
        result = self.cursor.fetchone()
        return result if result else None

    def get_number_of_accounts(self, userID):
        """
        Returns a list containing the names of the accounts associated with user ID
        """
        query = "SELECT account_name FROM accounts WHERE userID = %s"
        self.cursor.execute(query, (userID,))
        result = self.cursor.fetchall()
        return [account[0] for account in result] if result else []

    def get_categories(self, userID):
        """
        Returns the most used category names given userID
        :return: description and name of the account
        """
        query = """
            SELECT COUNT(categoryID) AS total_descriptions, category_name
            FROM categories
            WHERE userID = %s
            GROUP BY category_name
            ORDER BY total_descriptions DESC
        """

        self.cursor.execute(query, (userID, ))
        result = self.cursor.fetchall()
        return result if result else None

    def get_data_key_salt(self, userID):
        """
        Returns encrypted data key and salt of the user given ID
        """
        query = """
            SELECT enc_data_key, salt
            FROM users
            WHERE userID = %s
        """
        self.cursor.execute(query, (userID, ))
        result = self.cursor.fetchone()
        return result if result else None

    # ==========================   UPDATE QUERIES    =============================

    def update_account(self, accountID, account_name, account_type=None, account_currency=None):
        """
        Updates account information fields
        """

        parameter = [account_name]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        top_query = "UPDATE accounts SET account_name = %s"
        bottom_query = " WHERE accountID = %s"

        if account_type:
            top_query+=", account_type = %s"
            parameter.append(account_type)

        if account_currency:
            top_query+=", account_currency = %s"
            parameter.append(account_currency)

        top_query+=", updated_at = %s"
        parameter.extend([current_time, accountID])
        query = top_query + bottom_query
        self.cursor.execute(query, parameter)
        self.db.commit()

    def update_user(self, userID, new_username=None, new_email=None):
        """
        Updates user information (username and email)
        """

        parameter = []
        top_query = "UPDATE users SET"
        bottom_query = " WHERE userID = %s"
        if new_username:
            top_query+=" username = %s"
            parameter.append(new_username)

        if new_email:
            if new_username:
                top_query+=", email_address = %s"
            else:
                top_query+=" email_address = %s"
            parameter.append(new_email)

        query = top_query + bottom_query
        parameter.append(userID)

        if len(parameter) != 0:
            self.cursor.execute(query, parameter)
            self.db.commit()
        else:
            print("could not update the user information")


    def update_category_name(self, category_name, categoryID):
        """
        Updates the name of the category given category ID
        """

        query = """
            UPDATE categories
            SET category_name = %s
            WHERE categoryID = %s
        """
        self.cursor.execute(query, (category_name, categoryID))
        self.db.commit()

    def update_category_description(self, category_sentence, category_list, category_name, categoryID):
        """
        Updates description, key-words list and name of the category
        """
        query = """
            UPDATE categories
            SET category_sentence = %s, category_list = %s, category_name = %s
            WHERE categoryID = %s
        """
        self.cursor.execute(query, (category_sentence, json.dumps(category_list), category_name, categoryID))
        self.db.commit()

    def update_key_salt(self, enc_data_key, salt, userID):
        """
        Updates encrypted data key and salt with new ones given user ID
        """
        query = """
            UPDATE users
            SET enc_data_key = %s, salt = %s
            WHERE userID = %s
        """
        self.cursor.execute(query, (enc_data_key, salt, userID))
        self.db.commit()

    # ==========================   DELETE QUERIES    =============================


    def delete_file(self, file_ID):
        """
        Delete the file from database given file ID, resulting in cascading effect of deletion of associated transactions
        """
        query = "DELETE FROM files WHERE file_ID = %s"
        self.cursor.execute(query, (file_ID, ))
        self.db.commit()

    def delete_account(self, accountID):
        """
        Delete the account from database given account ID, resulting in cascading effect of deletion of associated transactions
        """
        query = "DELETE FROM accounts WHERE accountID = %s"
        self.cursor.execute(query, (accountID, ))
        self.db.commit()
    
    def delete_transaction(self, transactionID):
        """
        Delete transaction from database given transaction ID
        """
        query = "DELETE FROM transactions WHERE transactionID = %s"
        self.cursor.execute(query, (transactionID, ))
        self.db.commit()

    # Deleted the user, resulting in cascading effect
    def delete_user(self, userID):
        """
        All data relating to the user is deleted
        """
        sql = "DELETE FROM users WHERE userID = %s"
        self.cursor.execute(sql, (userID,))
        self.db.commit()

    def delete_user_files(self, userID):
        """
        Delete all related encrypted files associated with user given user ID
        """
        sql = "DELETE FROM files WHERE accountID IN (SELECT accountID FROM accounts WHERE userID = %s)"
        self.cursor.execute(sql, (userID,))
        self.db.commit()

    # ==========================   CATEGORY FEATURE RELATED QUERIES    =============================


    def return_word_list(self, description):
        """
            Returns the list of words from the description of the selected transaction
            plus_list = words to be used to identify close transactions
            word_list = the list of the words passed
        """
        # removing words with length of 2-3 and extra white space between words in the description
        clean_description = re.sub(r'\b\w{2,3}\b', '', " ".join(description.lower().split()))
        places = (GeoText(clean_description.title()).cities + GeoText(clean_description.title()).countries)
        places_set = {place.lower() for place in places}

        regex = re.compile(r'\b[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*\b')
        str_list = regex.findall(clean_description)
        plus_list = []
        word_list = []
        for  word in str_list:
            # does not include the word in stopwords set
            if (word.lower() not in (places_set | self.stop_words)):
                # since the case does not matter
                plus_list.append(f'+{word}')
                word_list.append(word)

        return plus_list, word_list

    def find_close_transactions(self, description, accountID):
        """
        Returns transaction IDs of close transactions given the user selected description
        :param description: description of the transaction
        :param accountID: account ID
        :return: transaction IDs of close transactions in the account
        """
        parameters = [accountID]

        plus_list, word_list = self.return_word_list(description)
        parameters.extend([' '.join(plus_list)])
        query = "SELECT transactionID, description FROM transactions WHERE accountID = %s and MATCH(description) AGAINST(%s IN NATURAL LANGUAGE MODE)"
        self.cursor.execute(query, parameters)

        output = self.cursor.fetchall()
        selective_ids = [value[0] for value in output]

        return selective_ids, word_list

    def return_description_given_transactionID(self, transactionID):
        """
        Returns the description of the transaction given the transaction ID
        """
        description_query =  """
            SELECT description
            FROM transactions
            WHERE transactionID = %s
        """
        self.cursor.execute(description_query, (transactionID, ))

        description = self.cursor.fetchone()[0]
        return description if description else None


    def update_category(self, category, transactionID):
        """
        Updates the category name of the transaction/s 
        :param category: category name
        :param transactionID: transaction ID/s in a list
        """
        if not isinstance(transactionID, list):
            transactionID = [transactionID]

        if not transactionID:
            return

        s_list = []
        for i in range(len(transactionID)):
            s_list.append("%s")
        s_string = ', '.join(s_list)

        query = f"""
            UPDATE transactions
            SET category = %s
            WHERE transactionID IN ({s_string})
        """

        parameters = [category] + transactionID

        self.cursor.execute(query, parameters)
        self.db.commit()


    def change_category_transaction(self, userID, accountID, category, transactionID):
        """
        Updates category name of the given transaction by its transaction ID and its close transactions
        """
        self.update_category(category, transactionID)
        description = self.return_description_given_transactionID(transactionID)
        close_transaction_ids, world_list = self.find_close_transactions(description, accountID)
        categoryID, exist = self.insert_category(userID, accountID, description, world_list, category)
        if exist:
            self.update_category_name(category, categoryID)
        self.update_category(category, close_transaction_ids)

    def return_updated_category(self, userID, accountID,  description):
        """
        Returns the updated category for new incoming transactions by
        finding finds the closest matching category
        :return: best matching category or "Undefined
        """
        word_list = self.return_word_list(description)[1]
        output = self.get_next_best_category(userID, accountID, word_list)
        if (output is None):
            category = "Undefined"
        else:
            category = output[1]
        return category

    # Returns corresponding unique descriptions and categoryIDs of each category names
    def show_description_list_by_category_name(self, userID, category_name):
        """
        Returns corresponding unique descriptions and categoryIDs of each category 
        given category name and user ID in ascending order
        """
        query = """
            SELECT category_sentence, categoryID
            FROM categories
            WHERE userID = %s AND category_name = %s
            ORDER BY categoryID ASC
        """
        self.cursor.execute(query, (userID, category_name))
        result = self.cursor.fetchall()
        return result if result else None

    def add_category_update(self, userID, accountID, description, category_name):
        """
        Adds new category and update matching transactions' category name
        """
        close_transaction_ids, word_list = self.find_close_transactions(description, accountID)
        categoryID, exist = self.insert_category(userID, accountID, description, word_list, category_name)
        if exist:
            self.update_category_name(category_name, categoryID)

        self.update_category(category_name, close_transaction_ids)
        return categoryID if categoryID else None

    def delete_category(self, categoryID):
        """
        Delete category from database given category ID
        """
        query_delete = """
            DELETE FROM categories
            WHERE categoryID = %s"""

        self.cursor.execute(query_delete, (categoryID, ))
        self.db.commit()

    def update_transaction_after_deletion_description(self, userID, accountID, category_name):
        """
        Finds next matching category of the transactions after category is deleted
        :param category_name: name of the category to be deleted
        :param accountID: account ID
        """
        query = """
            SELECT transactionID, description
            FROM transactions
            WHERE category = %s
        """

        self.cursor.execute(query, (category_name, ))
        result = self.cursor.fetchall()
        if result:
            for (i, j)in result:
                new_category = self.return_updated_category(userID, accountID, j)
                self.update_category(new_category, i)

    def change_transaction_description_and_update(self, userID, accountID,  new_description, transactionID):
        """
        Changes the description of the transaction and update the category
        """
        query = """
            UPDATE transactions
            SET description = %s
            WHERE transactionID = %s
        """

        self.cursor.execute(query, (new_description, transactionID))
        self.db.commit()
        new_category = self.return_updated_category(userID, accountID, new_description)
        self.update_category(new_category, transactionID)

    def return_accounts_given_userID(self, userID):
        """
        Return account information of the related accounts given user ID
        """
        query = """
            SELECT accountID, account_name
            FROM accounts
            WHERE userID = %s
        """
        self.cursor = self.connection.cursor
        self.cursor.execute(query, (userID,))
        result = self.cursor.fetchall()
        return result if result else None

    def compute_account_options(self, userID):
        """
        Return list containing names of the accounts associated with user ID
        """
        accounts = self.return_accounts_given_userID(userID)
        options_list = [account[1] for account in accounts] if accounts else []
        return options_list if options_list else None
