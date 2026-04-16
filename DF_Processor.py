from datetime import datetime
from decimal import Decimal

from db_queries import QueryProcessor
from db_connection import Database
from base_classes import ParsingHelper

class ProcessingDF:

    """
    Processed the dataframe returned from parsing
    """

    def __init__(self, df, file_ID, userID, accountID):

        connection = Database()
        self.db = connection.db
        self.cursor = connection.cursor
        self.accountID = accountID
        self.query = QueryProcessor()
        self.file_ID = file_ID
        self.userID = userID

        if isinstance(df, list):
            for i in df:
                self.insert_transaction(self.accountID, i)
        else:
            self.insert_transaction(self.accountID, df)

    # Inserts type classified transaction into the database
    def insert_transaction(self, accountID, dtb):
        parser = ParsingHelper()
        query = QueryProcessor()

        # https://stackoverflow.com/questions/16476924/how-can-i-iterate-over-rows-in-a-pandas-dataframe

        transaction_list = []
        for _, row in dtb.iterrows():
            row = list(map(str, row.tolist()))
            category = query.return_updated_category(self.userID, self.accountID, row[2])
            row[1] = parser.classify_transaction_type(row[1])
            transaction_list.append((accountID, self.file_ID, self.change_to_date(row[0]), row[1], row[2], category, Decimal(row[3]),  Decimal(row[4])))

        self.query.insert_into_transactions(transaction_list)

    # Converts string formatted date into a valid date
    def change_to_date(self, date_string):
        date = datetime.strptime(date_string, "%d/%m/%Y")
        return date


