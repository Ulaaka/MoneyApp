from database_connection import database
from datetime import datetime
import re
from nltk.corpus import stopwords
from geotext import GeoText
import json
import pandas as pd
class query_processor:

    """
    Contains the functions for querying the database
    """

    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor
        # Stopwords in english dictionary
        self.stop_words = set(stopwords.words('english'))

        # https://stackoverflow.com/a/51534662
        # Identified stopwords
        new_stopwords = {'ltd', 'limited', 'inc', 'stores', 'gb', 'uk'}

        # Add the new identified stopwords
        self.stop_words.update(new_stopwords)

    # Finds min or max value of the given column (Amount, balance, date etc)
    def find_min_max(self, column, max_toggle=True):
        toggle = "MAX" if max_toggle else "MIN"

        query = f"SELECT {toggle}({column})from transactions"
        self.cursor.execute(query)
        output = self.cursor.fetchone()
        return output

    # transfer toggle = if true find the total income
    # at least one of the transfer_toggle and max_toggle should be included
    # grouping by the type of transaction is useful too
    def total_transfer_or_extreme_value(self, username, transfer_toggle=None, max_toggle=None, account_name=None, date_lower=None, date_upper=None):
        try:
            # string to datetime conversion, could get useful
            #date = datetime.fromisoformat(datetime_input)
            parameter = [username]

            toggle = "SUM"
            base_query = f"SELECT {toggle}(T.amount)" 

            body_query = """
                    FROM users U
                    JOIN accounts A ON A.userID = U.userID
                    JOIN transactions T ON T.accountID = A.accountID
                    WHERE U.username = %s
            """

            if (max_toggle is not None):
                toggle = "MAX" if max_toggle else "MIN"

            if (max_toggle is not None or transfer_toggle is not None):
                base_query =  f"SELECT ABS({toggle}(T.amount))" 

            query = base_query + body_query

            if (transfer_toggle is not None):
                toggle = ">" if transfer_toggle else "<"
                query+=f" and T.amount {toggle} 0"

            if (account_name is not None):
                query+= " and A.account_name = %s"
                parameter.append(account_name)

            if (date_lower):
                query += " and T.transaction_date >= %s"
                parameter.append(date_lower)

            if (date_upper):
                query += " and T.transaction_date <= %s"
                parameter.append(date_upper)

            self.cursor.execute(query, tuple(parameter))

            output = self.cursor.fetchone()
            print(output[0])
            return output[0]
        except:
            print("important arguments (max_toggle or transfer_toggle missing)")

    # Selects the last day of the given date range (month)
    def return_last_month(self, datetime_input):
        last_day_query = f"SELECT LAST_DAY('{datetime_input}')"
        self.cursor.execute(last_day_query)

        return self.cursor.fetchone()[0]

    # ["year", "year_month", "date"]
    # Produces the first and last date of the given data range
    def produce_dates(self, date, range):
        date = datetime.fromisoformat(date)
        if (range == "year"):
            return f"{date.year}-01-01", f"{date.year}-12-31"

        if (range == "year_month"):
            first_date = f"{date.year}-0{date.month}-01" if (date.month in range(1, 10)) else f"{date.year}-{date.month}-01"
            last_date = str(self.return_last_month(first_date))
            return first_date, last_date

    # Compares the given data ranges in terms of total transfer or extreme values (min or max)
    def compare_range(self, username, transfer_toggle, account_name,  date_first, date_second, range):

        first_dates = self.produce_dates(date_first, range)
        second_dates = self.produce_dates(date_second, range)
        return_values = []
        if (range == "year"):

            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, account_name=account_name, date_lower=first_dates[0], date_upper=first_dates[1]))
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, account_name=account_name, date_lower=second_dates[0], date_upper=second_dates[1]))

        elif (range == "year_month"):
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, account_name=account_name, date_lower=first_dates[0], date_upper=first_dates[1]))
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, account_name=account_name, date_lower=second_dates[0], date_upper=second_dates[1]))

        elif (range == "date"):

            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, account_name=account_name, date_lower=date_first, date_upper=date_first))
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, account_name=account_name, date_lower=date_second, date_upper=date_second))

        return return_values

    # Finds the total amount of the repeating transactions of data range of the account
    def common_transactions(self, username, limit, account_name=None, transfer_toggle=None, date_lower=None, date_upper=None, filter_amount=None):
        head_query = """
            SELECT T.description as statement, SUM(ABS(T.amount)) as total_sent
            FROM users U
            JOIN accounts A ON A.userID = U.userID
            JOIN transactions T ON T.accountID = A.accountID
        """

        where_query = f" WHERE U.username = '{username}'"

        if (account_name):
            where_query+=f" and A.account_name = '{account_name}'"

        if (transfer_toggle is not None):
            toggle = ">" if transfer_toggle else "<"
            where_query+=f" and T.amount {toggle} 0"

        if (date_lower):
            where_query += f" and T.transaction_date >= '{date_lower}'"

        if (date_upper):
            where_query += f" and T.transaction_date <= '{date_upper}'"

        tail_query = f" GROUP BY statement ORDER BY total_sent DESC LIMIT {limit}"

        if (filter_amount):
            tail_query = f" GROUP BY statement HAVING total_sent >= {filter_amount} ORDER BY total_sent DESC LIMIT {limit}"

        query = head_query + where_query + tail_query
        self.cursor.execute(query)

        output = self.cursor.fetchall()


        regex = re.compile(r'\b[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*\b')

        clean_ouput = []
        for key, value in output:
            clean_ouput.append(( ' '.join(regex.findall(key)), value))

        return clean_ouput

    # Finds subscriptions from the transactions 
    def find_subscriptions(self, username, account_name=None):
        head_query = """
            SELECT T.description, SUM(ABS(T.amount)) as total_sent, COUNT(*) count_transaction
            FROM transactions T
            JOIN accounts A ON T.accountID = A.accountID
            JOIN users U ON U.userID = A.userID
        """

        where_query = f" WHERE U.username = '{username}'"

        if (account_name):
            where_query+=f" and A.account_name = '{account_name}'"

        tail_query = f" GROUP BY T.description HAVING count_transaction > 3 ORDER BY total_sent DESC"

        query = head_query + where_query + tail_query
        self.cursor.execute(query)
        output = self.cursor.fetchall()
        print(output)
        return output

    # account queries
    # ============================
    # Creates new user, and inserts information into the database
    def insert_into_users(self, username, hashed_password, email):
        sql = f"INSERT INTO users (username, hashed_password, email_address) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (username, hashed_password, email))
        userID = self.cursor.lastrowid
        self.db.commit()
        return userID

    # Creates new account, and inserts information into the database
    def insert_into_accounts(self, userID, acc_name, acc_type, acc_currency):
        sql = f"INSERT INTO accounts (userID, account_name, account_type, account_currency) VALUES (%s, %s, %s, %s)"
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
    def insert_into_categories(self, userID, category_sentence, category_list, category_name):
        query = f"INSERT INTO categories (userID, category_sentence, category_list, category_name) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query, (userID, category_sentence, json.dumps(category_list), category_name))
        categoryID = self.cursor.lastrowid
        self.db.commit()
        return categoryID

    def insert_into_files(self, accountID,  filename, new_filename, str_size, file_type):
        new_query = "INSERT INTO files (accountID, file_name, hashed_name, file_size, file_type) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(new_query, (accountID,  filename, new_filename, str_size, file_type))
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
            try:
                accountID = self.insert_into_accounts(userID, acc_name, acc_type, acc_currency)
            except:
                print("could not execute insert_into_accounts ")
        return accountID

    # New category insertion/update with check of if the category already exists
    def insert_category(self, userID, category_sentence, category_list, category_name):
        result = self.get_category(userID, category_list)
        if result is not None:
            try:
                categoryID = result[0]
                query = f"""
                    UPDATE categories
                    SET category_name = %s
                    WHERE categoryID = %s
                """
                self.cursor.execute(query, (category_name, categoryID))
                self.db.commit()
            except:
                print(f"could not update the category:{categoryID}")
        else:
            categoryID = self.insert_into_categories(userID, category_sentence, category_list, category_name)
        return categoryID

    # Deleted the user, resulting in cascading effect
    def delete_user(self, username):
        """
        All data relating to the user is deleted
        """
        sql = f"DELETE FROM users WHERE username = %s"
        self.cursor.execute(sql, (username,))
        self.db.commit()

    # Returns the category based on the tokens of words in the list
    def get_category(self, userID, category_list):
        # https://stackoverflow.com/a/37662298
        # https://dev.mysql.com/doc/refman/8.4/en/json-search-functions.html

        sql_categories  = "SELECT categoryID, category_list, category_name FROM categories WHERE userID = %s ORDER BY categoryID"
        self.cursor.execute(sql_categories, (userID, ))
        result = self.cursor.fetchall()
        if not result:
            return None
        tuple_to_dictionary = {tuple(json.loads(category_list)): (categoryID, category_name) for categoryID, category_list, category_name in result}

        if not tuple_to_dictionary:
            return None
        
        priority_list = [(len([item for item in category_list if item in i]), len(i)) for i in tuple_to_dictionary]

        if not priority_list:
            return None
        max_category = max(priority_list, key=lambda x: (x[0], -x[1]))
        position = priority_list.index(max_category)

        key = list(tuple_to_dictionary)[position]

        output = tuple_to_dictionary[key]

        return output if output else None
    # Returns userID
    def get_userID(self, username):
        sql = f"SELECT userID FROM users WHERE username = %s"
        self.cursor.execute(sql, (username,))
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Returns accountID
    def get_accountID(self, account_name, userID):
        sql = f"SELECT accountID FROM accounts WHERE account_name = %s and userID = %s"
        self.cursor.execute(sql, (account_name, userID))
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Returns the hashed name of the encrypted file
    def get_hashed_name(self, accountID, filename):
        new_sql = f"SELECT hashed_name FROM files WHERE accountID = '{accountID}' and file_name = '{filename}'"
        self.cursor.execute(new_sql)
        output = self.cursor.fetchone()
        return output[0] if output else None

    # return total transactions made by the account
    def get_transactions(self, accountID):
        query = """SELECT * FROM transactions WHERE accountID = %s"""
        self.cursor.execute(query, (accountID,))
        output = self.cursor.fetchall()
        header_columns = [column[0] for column in self.cursor.description]
        df = pd.DataFrame(output, columns=header_columns)
        return df
        
    def get_hashed_password(self, username):
        sql = f"SELECT hashed_password FROM users WHERE username = %s"
        self.cursor.execute(sql, (username, ))
        result = self.cursor.fetchone()
        return result if result else None

    # Returns the original name of the file from the hashed
    def get_file_name_from_hashed(self, accountID, hashed_name):
        new_sql = f"SELECT file_name FROM files WHERE accountID = '{accountID}' and hashed_name = '{hashed_name}'"
        self.cursor.execute(new_sql)
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Returns accountID
    def get_file_ID(self, accountID, filename):
        sql = "SELECT file_ID FROM files WHERE accountID = %s AND file_name = %s"
        self.cursor.execute(sql, (accountID, filename))
        output = self.cursor.fetchone()
        return output[0] if output else None

    # Deleted the file, associating transactions
    def delete_file(self, username, account_name, filename):
        userID = self.get_userID(username)
        accountID = self.get_accountID(account_name, userID)
        file_ID = self.get_file_ID(accountID, filename)

        sql = f"DELETE FROM transactions WHERE file_ID = '{file_ID}'"
        self.cursor.execute(sql)
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
    def find_close_transactions(self, description):
        # https://stackoverflow.com/questions/6259647/mysql-match-against-order-by-relevance-and-column

        plus_list, word_list = self.return_word_list(description)
        parameters = [' '.join(plus_list)]

        query = "SELECT transactionID, description FROM transactions WHERE MATCH(description) AGAINST(%s IN NATURAL LANGUAGE MODE)"
        self.cursor.execute(query, parameters)

        output = self.cursor.fetchall()
        selective_ids = [value[0] for value in output]

        return selective_ids, word_list

    # Updates the category of the transaction
    def update_category(self, category, transactionID):
        parameter = [category]
        if not isinstance(transactionID, list):
            transactionID = [transactionID]

        s_list = []
        for i in range(len(transactionID)):
            s_list.append("%s")

        s_string = ', '.join(s_list)

        query = f"""
            UPDATE transactions
            SET category = %s
            WHERE transactionID IN ({s_string})
        """
        parameter += transactionID

        self.cursor.execute(query, parameter)
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
    def change_category(self, userID, category, transactionID):
        self.update_category(category, transactionID)
        description = self.return_description_given_transactionID(transactionID)

        close_transaction_ids = self.find_close_transactions(description)
        categoryID = self.insert_category(userID, description, close_transaction_ids[1], category)

        self.update_category(category, close_transaction_ids[0])

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

    # Returns the updated category
    def return_updated_category(self, description):
        word_list = self.return_word_list(description)[1]
        output = self.get_category(1, word_list)
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

    # Associate the description with the category name, and its close transactions
    def add_description_into_list_category(self, userID, description, category_name):
        close_transaction_ids = self.find_close_transactions(description)
        categoryID = self.insert_category(userID, description, close_transaction_ids[1], category_name)
        self.update_category(category_name, close_transaction_ids[0])
        return categoryID if categoryID else None

    # after the description list is shown, the user can remove category
    def remove_description_from_list_category(self, userID, categoryID, category_name):
        query_delete = """
            DELETE FROM categories
            WHERE userID = %s AND categoryID = %s"""

        self.cursor.execute(query_delete, (userID, categoryID))
        self.db.commit()
        # removed category name
        return category_name

    # use the category name of the removed description of the category
    def update_transaction_after_deletion_description(self, accountID, category_name):
        query = """
            SELECT transactionID, description
            FROM transactions
            WHERE accountID = %s AND category = %s
        """

        self.cursor.execute(query, (accountID, category_name))
        result = self.cursor.fetchall()
         #return result if result else None
        if result:
            for (i, j)in result:
                new_category = self.return_updated_category(j)
                self.update_category(new_category, i)

    # Changes the description of the transaction, needs to change the category after that
    def change_description_and_update(self, new_description, transactionID):
        query = """
            UPDATE transactions
            SET description = %s
            WHERE transactionID = %s
        """

        self.cursor.execute(query, (new_description, transactionID))
        self.db.commit()

        new_category = self.return_updated_category(new_description)
        self.update_category(new_category, transactionID)

    # Show list of accounts give user ID
    def return_accounts_given_userID(self, userID):
        query = """
            SELECT accountID, account_name
            FROM accounts
            WHERE userID = %s
        """
        self.cursor.execute(query, (userID,))
        result = self.cursor.fetchall()
        return result if result else None
    
    def compute_account_options(self, userID):
        accounts = self.return_accounts_given_userID(userID)
        options_list = [account[1] for account in accounts] if accounts else []
        return options_list if options_list else None