from database_connection import database
from datetime import datetime
import re
from nltk.corpus import stopwords
from geotext import GeoText
import json
import pandas as pd
import pymysql
from datetime import datetime

class query_processor:

    """
    Contains the functions for querying the database
    """

    def __init__(self):
        self.connection = database()
        connection = self.connection
        self.db = connection.db
        self.cursor = connection.cursor
        # Stopwords in english dictionary
        self.stop_words = set(stopwords.words('english'))

        # https://stackoverflow.com/a/51534662
        # Identified stopwords
        new_stopwords = {'ltd', 'limited', 'inc', 'stores', 'gb', 'uk'}

        # Add the new identified stopwords
        self.stop_words.update(new_stopwords)

    # ACCOUNT QUERIES
    # Creates new user, and inserts information into the database
    def insert_into_users(self, username, hashed_password, email):
        sql = "INSERT INTO users (username, hashed_password, email_address) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (username, hashed_password, email))
        userID = self.cursor.lastrowid
        self.db.commit()
        return userID

    # Creates new account, and inserts information into the database
    def insert_into_accounts(self, userID, acc_name, acc_type, acc_currency):
        sql = "INSERT INTO accounts (userID, account_name, account_type, account_currency) VALUES (%s, %s, %s, %s)"
        self.cursor = self.connection.cursor
        self.cursor.execute(sql, ( userID, acc_name, acc_type, acc_currency))
        accountID = self.cursor.lastrowid
        self.db.commit()
        return accountID

    # Inserts new transaction into the database
    def insert_into_transactions(self, transaction_list):
        sql = """INSERT IGNORE INTO transactions (accountID, file_ID, transaction_date, transaction_type, description, category, amount, balance) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        self.cursor.executemany(sql, transaction_list)
        self.db.commit()

    # Inserts new category into the database
    def insert_into_categories(self, userID, accountID, category_sentence, category_list, category_name):
        query = "INSERT INTO categories (userID, accountID, category_sentence, category_list, category_name) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(query, (userID, accountID, category_sentence, json.dumps(category_list), category_name))
        categoryID = self.cursor.lastrowid
        self.db.commit()
        return categoryID

    def insert_into_files(self, accountID,  filename, new_filename, size_file, file_type):
        new_query = "INSERT INTO files (accountID, file_name, hashed_name, file_size, file_type) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(new_query, (accountID,  filename, new_filename, size_file, file_type))
        file_ID = self.cursor.lastrowid
        self.db.commit()
        return file_ID

    # New user insertion with check of if the user already exists
    def insert_user(self, username, hashed_password, email):
        userID = self.get_userID(username)
        if userID is None:
            try:
                userID = self.insert_into_users(username, hashed_password, email)
            except:
                print("User registration error")
        return userID

    # New account insertion with check of if the account already exists
    def insert_account(self, userID, acc_name, acc_type, acc_currency):
        accountID = self.get_accountID(acc_name, userID)
        if accountID is None:
            accountID = self.insert_into_accounts(userID, acc_name, acc_type, acc_currency)
        return accountID

    def insert_category(self, userID, accountID, category_sentence, category_list, category_name):
        exist = True
        categoryID = self.get_matching_category(accountID, category_list)
        if categoryID is None:
            exist = False
            categoryID = self.insert_into_categories(userID, accountID, category_sentence, category_list, category_name)
        return categoryID, exist

    def change_category_name(self, category_name, categoryID):
            query = """
                UPDATE categories
                SET category_name = %s
                WHERE categoryID = %s
            """
            self.cursor.execute(query, (category_name, categoryID))
            self.db.commit()

    def change_category_description(self, category_sentence, category_list, category_name, categoryID):
            query = """
                UPDATE categories
                SET category_sentence = %s, category_list = %s, category_name = %s
                WHERE categoryID = %s
            """
            self.cursor.execute(query, (category_sentence, json.dumps(category_list), category_name, categoryID))
            self.db.commit()

    # Deleted the user, resulting in cascading effect
    def delete_user(self, userID):
        """
        All data relating to the user is deleted
        """
        sql = "DELETE FROM users WHERE userID = %s"
        self.cursor.execute(sql, (userID,))
        self.db.commit()

    def get_category_info(self, userID, accountID, asDF=None):
        # categoryID, category_list, category_name
        sql_categories  = "SELECT categoryID, category_list, category_sentence, category_name FROM categories WHERE userID = %s and accountID = %s ORDER BY categoryID"
        self.cursor.execute(sql_categories, (userID, accountID))
        result = self.cursor.fetchall()
        if not asDF:
            return result if result else None
        else:
            header_columns = [column[0] for column in self.cursor.description]
            df = pd.DataFrame(result, columns=header_columns)
            return df

    # after category is deleted, finds the next best category to replace it
    def get_next_best_category(self, userID, accountID, category_list):
        # https://stackoverflow.com/a/37662298
        # https://dev.mysql.com/doc/refman/8.4/en/json-search-functions.html
        try:
            result = self.get_category_info(userID, accountID)
            category_dictionary = {tuple(json.loads(category_list)): (categoryID, category_name) for categoryID, category_list, _, category_name in result}
            priority_list = [(len([item for item in category_list if item in i]), len(i)) for i in category_dictionary]
            max_category = max(priority_list, key=lambda x: (x[0], -x[1]))
            if max_category[0] == 0:
                return None

            position = priority_list.index(max_category)
            key = list(category_dictionary)[position]

            output = category_dictionary[key]
            # (categoryID, category_name)
            return output
        except:
            return None
    # get marching category
    def get_matching_category(self, accountID,  word_list):
        query = "SELECT categoryID from categories WHERE category_list = %s and accountID = %s"
        self.cursor.execute(query, (json.dumps(word_list), accountID))
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Returns userID
    def get_userID(self, username):
        sql = "SELECT userID FROM users WHERE username = %s"
        self.cursor.execute(sql, (username,))
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Returns accountID
    def get_accountID(self, account_name, userID):
        sql = "SELECT accountID FROM accounts WHERE account_name = %s and userID = %s"
        self.cursor.execute(sql, (account_name, userID))
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Returns the hashed name of the encrypted file
    def get_hashed_name(self, accountID, name_file=None, fileID=None):
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

    # return total transactions made by the account
    def get_transactions(self, accountID):
        query = """SELECT * FROM transactions WHERE accountID = %s"""
        self.cursor = self.connection.cursor
        self.cursor.execute(query, (accountID,))
        output = self.cursor.fetchall()
        header_columns = [column[0] for column in self.cursor.description]
        df = pd.DataFrame(output, columns=header_columns)
        return df

    def get_hashed_password(self, username=None, userID=None):
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

    # Returns the original name of the file from the hashed
    def get_file_name(self, accountID, hashed_name=None, fileID=None):
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
        sql = "SELECT file_ID FROM files WHERE accountID = %s AND file_name = %s"
        self.cursor.execute(sql, (accountID, filename))
        output = self.cursor.fetchone()
        return output[0] if output else None
    
    def update_account(self, accountID, account_name, account_type=None, account_currency=None):
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

    # Shows existing files IDs and filename submitted in the account
    def get_files(self, accountID):
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
        query = "SELECT account_type, account_currency FROM accounts WHERE account_name = %s AND userID = %s"
        self.cursor.execute(query, (account_name, userID))
        result = self.cursor.fetchone()
        return result if result else None

    def get_type_with_id(self, id):
        query = "SELECT account_type FROM accounts WHERE file_ID = %s"
        self.cursor.execute(query, (id, ))
        result = self.cursor.fetchone()
        return result if result else None

    def get_create_update_account(self,  account_name, userID):
        query = "SELECT created_at, updated_at FROM accounts WHERE account_name = %s AND userID = %s"
        self.cursor.execute(query, (account_name, userID))
        result = self.cursor.fetchone()
        return result if result else None

    def get_user_info(self, userID):
        query = "SELECT username, email_address, created_at FROM users WHERE userID = %s"
        self.cursor.execute(query, (userID,))
        result = self.cursor.fetchone()
        return result if result else None

    def get_number_of_accounts(self, userID):
        query = "SELECT account_name FROM accounts WHERE userID = %s"
        self.cursor.execute(query, (userID,))
        result = self.cursor.fetchall()
        return [account[0] for account in result] if result else []

    # Deleted the file, associating transactions
    def delete_file(self, file_ID):
        query = "DELETE FROM files WHERE file_ID = %s"
        self.cursor.execute(query, (file_ID, ))
        self.db.commit()

    def delete_account(self, accountID):
        query = "DELETE FROM accounts WHERE accountID = %s"
        self.cursor.execute(query, (accountID, ))
        self.db.commit()
    
    def delete_transaction(self, transactionID):
        query = "DELETE FROM transactions WHERE transactionID = %s"
        self.cursor.execute(query, (transactionID, ))
        self.db.commit()

    # Returns the list of words from the description of the selected transaction
    # plus_list = words to be used to identify close transactions
    # word_list = the list of the words passed
    def return_word_list(self, description):
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

    # Returns transaction ids of close transactions given the user selected description
    def find_close_transactions(self, description, accountID):
        # https://stackoverflow.com/questions/6259647/mysql-match-against-order-by-relevance-and-column
        parameters = [accountID]

        plus_list, word_list = self.return_word_list(description)
        parameters.extend([' '.join(plus_list)])
        query = "SELECT transactionID, description FROM transactions WHERE accountID = %s and MATCH(description) AGAINST(%s IN NATURAL LANGUAGE MODE)"
        self.cursor.execute(query, parameters)

        output = self.cursor.fetchall()
        selective_ids = [value[0] for value in output]

        return selective_ids, word_list

    def update_category(self, category, transactionID):
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

    # Returns the description of the transaction given the transaction ID
    def return_description_given_transactionID(self, transactionID):
        description_query =  """
            SELECT description
            FROM transactions
            WHERE transactionID = %s
        """
        self.cursor.execute(description_query, (transactionID, ))

        # the description of the transaction
        description = self.cursor.fetchone()[0]
        return description if description else None

    # needs to search for similar description to apply the same category in the database
    # Updates the category of the selected transaction and its close transactions
    def change_category_transaction(self, userID, accountID, category, transactionID):
        self.update_category(category, transactionID)
        description = self.return_description_given_transactionID(transactionID)
        close_transaction_ids, world_list = self.find_close_transactions(description, accountID)
        categoryID, exist = self.insert_category(userID, accountID, description, world_list, category)
        if exist:
            self.change_category_name(category, categoryID)
        self.update_category(category, close_transaction_ids)

    # Returns the most used category names
    def get_categories(self, userID):
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

    # Returns the updated category for new transactions
    # finds the closest matching category
    def return_updated_category(self, userID, accountID,  description):
        word_list = self.return_word_list(description)[1]
        output = self.get_next_best_category(userID, accountID, word_list)
        if (output is None):
            category = "Undefined"
        else:
            category = output[1]
        return category

    # Returns corresponding unique descriptions and categoryIDs of each category names
    def show_description_list_by_category_name(self, userID, category_name):
        query = """
            SELECT category_sentence, categoryID
            FROM categories
            WHERE userID = %s AND category_name = %s
            ORDER BY categoryID ASC
        """
        self.cursor.execute(query, (userID, category_name))
        result = self.cursor.fetchall()
        return result if result else None

    # add new category and update
    def add_category_update(self, userID, accountID, description, category_name):
        close_transaction_ids, word_list = self.find_close_transactions(description, accountID)
        categoryID, exist = self.insert_category(userID, accountID, description, word_list, category_name)
        if exist:
            self.change_category_name(category_name, categoryID)

        self.update_category(category_name, close_transaction_ids)
        return categoryID if categoryID else None

    # after the description list is shown, the user can remove category
    def delete_category(self, categoryID):
        query_delete = """
            DELETE FROM categories
            WHERE categoryID = %s"""

        self.cursor.execute(query_delete, (categoryID, ))
        self.db.commit()

    # use the category name of the removed description of the category
    # when category is deleted, updates the transactions
    def update_transaction_after_deletion_description(self, userID, accountID, category_name):
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

    # Changes the description of the transaction, needs to change the category after that
    def change_transaction_description_and_update(self, userID, accountID,  new_description, transactionID):
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
        accounts = self.return_accounts_given_userID(userID)
        options_list = [account[1] for account in accounts] if accounts else []
        return options_list if options_list else None


    # GRAPH QUERIES 

    # Finds min or max value of the given column (Amount, balance, date etc)
    def find_min_max(self, accountID, column, max_toggle=True):
        toggle = "MAX" if max_toggle else "MIN"

        query = f"SELECT {toggle}({column})from transactions WHERE accountID = {accountID}"
        self.cursor.execute(query)
        output = self.cursor.fetchone()
        return output[0] if output else None

    # transfer toggle = if true find the total income
    # at least one of the transfer_toggle and max_toggle should be included
    # grouping by the type of transaction is useful too
    def total_transfer_or_extreme_value(self, userID, accountID, transfer_toggle=None, max_toggle=None, date_lower=None, date_upper=None):
            # string to datetime conversion, could get useful
        parameter = [userID, accountID]
        toggle = "SUM"

        base_query = f"SELECT {toggle}(T.amount)" 

        body_query = """
                FROM users U
                JOIN accounts A ON A.userID = U.userID
                JOIN transactions T ON T.accountID = A.accountID
                WHERE U.userID = %s and A.accountID = %s
        """

        if (max_toggle is not None):
            toggle = "MAX" if max_toggle else "MIN"

        if (max_toggle is not None or transfer_toggle is not None):
            base_query =  f"SELECT ABS({toggle}(T.amount))" 

        query = base_query + body_query

        if (transfer_toggle is not None):
            toggle = ">" if transfer_toggle else "<"
            query+=f" and T.amount {toggle} 0"

        if (date_lower):
            query += " and T.transaction_date >= %s"
            parameter.append(date_lower)

        if (date_upper):
            query += " and T.transaction_date <= %s"
            parameter.append(date_upper)

        self.cursor.execute(query, tuple(parameter))
        output = self.cursor.fetchone()
        return output[0] if output[0] is not None else 0

    # Finds the total amount of the repeating transactions of data range of the account
    def common_transactions(self, userID, limit, accountID=None, transfer_toggle=None, date_lower=None, date_upper=None):
        head_query = """
            SELECT REPLACE(TRIM(T.description), '[^A-Za-z0-9 ]', '') AS new_desc, SUM(ABS(T.amount)) as sumof
            FROM users U
            JOIN accounts A ON A.userID = U.userID
            JOIN transactions T ON T.accountID = A.accountID
        """

        where_query = f" WHERE U.userID = {userID}"

        if (accountID):
            where_query+=f" and A.accountID = {accountID}"

        if (transfer_toggle is not None):
            toggle = ">" if transfer_toggle else "<"
            where_query+=f" and T.amount {toggle} 0"

        if (date_lower):
            where_query += f" and T.transaction_date >= '{date_lower}'"

        if (date_upper):
            where_query += f" and T.transaction_date <= '{date_upper}'"

        tail_query = f" GROUP BY new_desc ORDER BY sumof DESC LIMIT {limit}"

        query = head_query + where_query + tail_query
        self.cursor.execute(query)

        output = self.cursor.fetchall()
        return output

    # Finds subscriptions from the transactions 
    def find_subscriptions(self, userID, account_name=None):
        head_query = f"""
            SELECT T.description, SUM(ABS(T.amount)) as total_sent , COUNT(*)
            FROM transactions T
            JOIN accounts A ON T.accountID = A.accountID
            JOIN users U ON U.userID = A.userID
            WHERE U.userID = {userID} and T.amount < 0
        """

        where_query = ""
        if (account_name):
            where_query+=f" and A.account_name = '{account_name}'"

        tail_query = " GROUP BY T.description, ABS(T.amount) HAVING COUNT(*) > 3 and COUNT(DISTINCT ABS(T.amount)) = 1 ORDER BY total_sent DESC LIMIT 5"

        query = head_query + where_query + tail_query
        self.cursor.execute(query)
        output = self.cursor.fetchall()
        return output

    def show_by_category(self, account_name):
        head_query = f"""
            SELECT T.category, COUNT(*), SUM(ABS(T.amount))
            FROM transactions T
            JOIN accounts A ON T.accountID = A.accountID
            JOIN users U ON U.userID = A.userID
        """

        where_query = ""
        if (account_name):
            where_query+=f" and A.account_name = '{account_name}'"

        tail_query = " GROUP BY T.category"

        query = head_query + where_query + tail_query
        self.cursor.execute(query)
        output = self.cursor.fetchall()
        return output

    def show_by_type(self, userID, date_lower, date_upper, account_name=None):
        head_query = f"""
            SELECT T.transaction_type, COUNT(*), SUM(ABS(T.amount))
            FROM transactions T
            JOIN accounts A ON T.accountID = A.accountID
            JOIN users U ON U.userID = A.userID
            WHERE U.userID = {userID}
        """
        where_query = ""
        if (account_name):
            where_query += f" and A.account_name = '{account_name}'"

        if (date_lower):
            where_query += f" and T.transaction_date >= '{date_lower}'"

        if (date_upper):
            where_query += f" and T.transaction_date <= '{date_upper}'"

        tail_query = " GROUP BY T.transaction_type"

        query = head_query + where_query + tail_query
        self.cursor.execute(query)
        output = self.cursor.fetchall()
        return output


    def show_by_category(self, userID, date_lower, date_upper, account_name=None):
        head_query = f"""
            SELECT T.category, COUNT(*), SUM(ABS(T.amount))
            FROM transactions T
            JOIN accounts A ON T.accountID = A.accountID
            JOIN users U ON U.userID = A.userID
            WHERE U.userID = {userID}
        """
        where_query = ""
        if (account_name):
            where_query += f" and A.account_name = '{account_name}'"

        if (date_lower):
            where_query += f" and T.transaction_date >= '{date_lower}'"

        if (date_upper):
            where_query += f" and T.transaction_date <= '{date_upper}'"

        tail_query = " GROUP BY T.category"

        query = head_query + where_query + tail_query
        self.cursor.execute(query)
        output = self.cursor.fetchall()
        return output

