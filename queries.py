from database_connection import database
from datetime import datetime

class query_processor:
    def __init__(self):
        connection = database()
        self.db = connection.db
        self.cursor = connection.cursor

    def find_min_max(self, column, max_toggle=True):
        toggle = "MAX" if max_toggle else "MIN"

        query = f"SELECT {toggle}({column})from transactions"
        self.cursor.execute(query)
        output = self.cursor.fetchone()
        return output[0]
        

    # transfer toggle = if true find the total income
    # at least one of the transfer_toggle and max_toggle should be included
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


    def compare_range(self, username, transfer_toggle, date_first, date_second, range):

        first_dates = self.produce_dates(date_first, range)
        second_dates = self.produce_dates(date_second, range)
        return_values = []
        if (range == "year"):

            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, date_lower=first_dates[0], date_upper=first_dates[1]))
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, date_lower=second_dates[0], date_upper=second_dates[1]))

        elif (range == "year_month"):
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, date_lower=first_dates[0], date_upper=first_dates[1]))
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, date_lower=second_dates[0], date_upper=second_dates[1]))
        
        elif (range == "date"):

            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, date_lower=date_first, date_upper=date_first))
            return_values.append(self.total_transfer_or_extreme_value(username, transfer_toggle=transfer_toggle, date_lower=date_second, date_upper=date_second))

        return return_values



