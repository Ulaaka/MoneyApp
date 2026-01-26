from database_connection import database
from datetime import datetime

class query_processor:
    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

    # find extreme value of the column [amount, transaction_date, balance]
    def find_min_max(self, column, max_toggle=True):
        toggle = "MAX" if max_toggle else "MIN"

        query = f"SELECT {toggle}({column}) from transactions"
        self.cursor.execute(query)
        output = self.cursor.fetchone()
        return output[0]
        

    # transfer toggle = if true find the total income
    # at least one of the transfer_toggle and max_toggle should be included
    def total_transfer_or_extreme_value(self, username, transfer_toggle=None, account_name=None, date_lower=None, date_upper=None, max_toggle=None):
        try:
            parameter = [username]

            query = """
                SELECT ABS(SUM(T.amount)) as total_expense
                FROM users U
                JOIN accounts A ON A.userID = U.userID
                JOIN transactions T ON T.accountID = A.accountID
                WHERE U.username = %s
            """
            
            if (max_toggle is not None):
                toggle = "MAX" if max_toggle else "MIN"
                base_query = f"SELECT ABS({toggle}(T.amount))" 
                body_query = """
                    FROM users U
                    JOIN accounts A ON A.userID = U.userID
                    JOIN transactions T ON T.accountID = A.accountID
                    WHERE U.username = %s
                """
                query = base_query + body_query

            if (transfer_toggle is not None):
                toggle = ">" if transfer_toggle else "<"
                transfer_additional = f" and T.amount {toggle} 0"
                query+=transfer_additional
            
            if (account_name is not None):
                query+= " and A.account_name = %s"
                parameter.append(account_name)

            if (date_upper and not date_lower):
                date_lower = self.find_min_max("transaction_date", False)

            elif (date_lower and not date_upper):
                date_upper = self.find_min_max("transaction_date", True)

            if (date_lower and date_upper):
                query+="and T.transaction_date BETWEEN %s and %s"
                parameter.extend([date_lower, date_upper])

            self.cursor.execute(query, tuple(parameter))

            output = self.cursor.fetchone()
            print(output[0])
            return output[0]
        except:
            print("important arguments (max_toggle or transfer_toggle missing)")