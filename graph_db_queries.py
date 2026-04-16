
from nltk.corpus import stopwords
from db_connection import Database

class GraphQueries:
    """
    Contains queries for fetching data for creating various graphs in the app (used in graphs_page.py)
    """

    def __init__(self):

        """
        Constructor for app graph queries
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


    def total_transfer_or_extreme_value(self, userID, accountID, transfer_toggle=None, max_toggle=None, date_lower=None, date_upper=None):
        """
        Versatile function for finding transactions data given constrains/filters as parameters
        :param userID, accountID: unique identifiers for transactions
        :param transfer_toggle: if True finds total income, else total expense
        :param max_toggle: If true, changes the total income/expense to max/min income/expense
        :param date_lower: Lower date boundary as a string in format (YYYY-MM-DD)
        :param date_lower: Upper date boundary as a string in format (YYYY-MM-DD)

        :return: total/min/max amount
        """
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

    def common_transactions(self, userID, limit, accountID=None, transfer_toggle=None, date_lower=None, date_upper=None):
        """
        Finds the total amount of the repeating transactions in the account given data range

        :param accountID: If True, scope narrows down to given account, else as a whole (user)
        :param transfer_toggle: If True, finds income, else expense
        :param date_lower: Lower date boundary in string format (YYYY-MM-DD)
        :param date_upper: Upper date boundary in string format (YYYY-MM-DD)

        :return: trimmed description and total amount
        """
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

    def find_subscriptions(self, userID, account_name=None):
        """
        Finds possible subscriptions
        Checks if the same expense from the sender were repeated at least 4 times

        :param account_name: If True, scope narrows to the given account, Else as a whole (user)
        :return: description, total amount of transaction/s
        """
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


    def show_by_type(self, userID, date_lower, date_upper, account_name=None):
        """
        Used for finding composition of transactions given their type
        :param date_lower: Lower date boundary as string (YYYY-MM-DD)
        :param date_upperR: upper date boundary as string (YYYY-MM-DD)
        :param account_name: If True, scope narrows down to account, Else as a whole (user)

        :return: transaction type, total count, total amount
        """
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
        """
        Used for finding composition of transactions given their category
        :param date_lower: Lower date boundary as string (YYYY-MM-DD)
        :param date_upperR: upper date boundary as string (YYYY-MM-DD)
        :param account_name: If True, scope narrows down to account, Else as a whole (user)

        :return: transaction category, total count, total amount
        """

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

