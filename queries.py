from database_connection import database
from datetime import datetime
import re
from nltk.corpus import stopwords
from geotext import GeoText
import json
class query_processor:
    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.stop_words = set(stopwords.words('english'))
        # https://stackoverflow.com/a/51534662
        new_stopwords = {'ltd', 'limited', 'inc', 'stores', 'gb', 'uk'}
        self.stop_words.update(new_stopwords)

    def find_min_max(self, column, max_toggle=True):
        toggle = "MAX" if max_toggle else "MIN"

        query = f"SELECT {toggle}({column})from transactions"
        self.cursor.execute(query)
        output = self.cursor.fetchone()

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


    def return_last_month(self, datetime_input):
        last_day_query = f"SELECT LAST_DAY('{datetime_input}')"
        self.cursor.execute(last_day_query)

        return self.cursor.fetchone()[0]
    
    # ["year", "year_month", "date"]
    def produce_dates(self, date, range):
        date = datetime.fromisoformat(date)
        if (range == "year"):
            return f"{date.year}-01-01", f"{date.year}-12-31"
        
        if (range == "year_month"):
            first_date = f"{date.year}-0{date.month}-01" if (date.month in range(1, 10)) else f"{date.year}-{date.month}-01"
            last_date = str(self.return_last_month(first_date))
            return first_date, last_date


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

    def insert_into_users(self, username, hashed_password, email):
        sql = f"INSERT INTO users (username, hashed_password, email_address) VALUES (%s, %s, %s)"
        self.cursor.execute(sql, (username, hashed_password, email))
        userID = self.cursor.lastrowid
        self.db.commit()
        return userID
    
    def insert_into_accounts(self, userID, acc_name, acc_type, acc_currency):
        sql = f"INSERT INTO accounts (userID, account_name, account_type, account_currency) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(sql, ( userID, acc_name, acc_type, acc_currency))
        accountID = self.cursor.lastrowid
        self.db.commit()
        return accountID
    
    def insert_into_transactions(self, accountID, file_ID, date, type, description, category, amount, balance):
        sql = f"INSERT INTO transactions (accountID, file_ID, transaction_date, transaction_type, description, category, amount, balance) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        self.cursor.execute(sql, (accountID, file_ID, date, type, description, category, amount, balance))
        self.db.commit()

    def insert_into_categories(self, userID, category_list, category_name):
        query = f"INSERT INTO categories (userID, category_list, category_name) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (userID, json.dumps(category_list), category_name))
        categoryID = self.cursor.lastrowid
        self.db.commit()
        return categoryID
    
    def insert_user(self, username, hashed_password, email):
        userID = self.get_userID(username)
        if userID is None:
            try:
                userID = self.insert_into_users(username, hashed_password, email)
            except:
                print("User registration error")
        return userID

    def insert_account(self, userID, acc_name, acc_type, acc_currency):
        accountID = self.get_accountID(acc_name, userID)
        if accountID is None:
            try:
                accountID = self.insert_into_accounts(userID, acc_name, acc_type, acc_currency)
            except:
                print("could not execute insert_into_accounts ")
        return accountID
    
    def insert_category(self, userID, category_list, category_name):
        categoryID = self.get_category(userID, category_list)[0]
        if categoryID is not None:
            try:
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
            categoryID = self.insert_into_categories(query, category_list, category_name)
        return categoryID

    def get_category(self, userID, category_list):
        # https://stackoverflow.com/a/37662298
        # https://dev.mysql.com/doc/refman/8.4/en/json-search-functions.html
        sql = f"SELECT categoryID, category_name FROM categories WHERE userID = %s AND JSON_CONTAINS(category_list, %s)"
        self.cursor.execute(sql, (userID, json.dumps(category_list)))
        output = self.cursor.fetchone()
        return output if output else None

    def get_userID(self, username):
        sql = f"SELECT userID FROM users WHERE username = %s"
        self.cursor.execute(sql, (username,))
        output = self.cursor.fetchone()
        return output[0] if output else None

    def get_accountID(self, account_name, userID):
        sql = f"SELECT accountID FROM accounts WHERE account_name = %s and userID = %s"
        self.cursor.execute(sql, (account_name, userID))
        output = self.cursor.fetchone()
        return output[0] if output else None
    
    def get_hashed_name(self, accountID, filename):
        new_sql = f"SELECT hashed_name FROM files WHERE accountID = '{accountID}' and file_name = '{filename}'"
        self.cursor.execute(new_sql)
        output = self.cursor.fetchone()
        return output[0] if output else None
    
    def get_file_ID(self, accountID, filename):
        sql = "SELECT file_ID FROM files WHERE accountID = %s AND file_name = %s"
        self.cursor.execute(sql, (accountID, filename))
        output = self.cursor.fetchone()
        return output[0] if output else None
    
    # needs to polish, would be a trouble if the file names are the same
    def delete_file(self, username, account_name, filename):
        userID = self.get_userID(username)
        accountID = self.get_accountID(account_name, userID)
        file_ID = self.get_file_ID(accountID, filename)

        sql = f"DELETE FROM transactions WHERE file_ID = '{file_ID}'"
        self.cursor.execute(sql)
        self.db.commit()

    def return_word_list(self, description):
        places = (GeoText(description.title()).cities + GeoText(description.title()).countries)
        places_set = {place.lower() for place in places}

        regex = re.compile(r'\b[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})*\b')
        str_list = regex.findall(description)
        plus_list = []
        word_list = []
        for  word in str_list:
            if (word.lower() not in (places_set | self.stop_words)):
                # since the case does not matter
                plus_list.append(f'+{word}')
                word_list.append(word)
        return plus_list, word_list

    def find_close_transactions(self, description):
        # https://stackoverflow.com/questions/6259647/mysql-match-against-order-by-relevance-and-column

        plus_list, word_list = self.return_word_list(description)
        parameters = [' '.join(plus_list)]

        query = "SELECT transactionID, description FROM transactions WHERE MATCH(description) AGAINST(%s IN NATURAL LANGUAGE MODE)"
        self.cursor.execute(query, parameters)

        output = self.cursor.fetchall()
        selective_ids = [value[0] for value in output]

        return selective_ids, word_list

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

    # needs to search for similar description to apply the same category in the database
    def change_category(self, userID, category, transactionID):
        self.update_category(category, transactionID)

        description_query =  """
            SELECT description
            FROM transactions
            WHERE transactionID = %s
        """

        self.cursor.execute(description_query, (transactionID, ))
        description = self.cursor.fetchone()[0]

        close_transaction_ids = self.find_close_transactions(description)
        categoryID = self.insert_category(userID, close_transaction_ids[1], category)

        self.update_category(category, close_transaction_ids[0])
    

    



