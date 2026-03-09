
import pandas as pd
from datetime import datetime
from BASE_Classes import ParsingBase
import numpy as np

class ParsingCSV:

    def __init__(self, pdf_name):

        # df = pd.read_csv("TransactionData.csv")
        # https://www.geeksforgeeks.org/python/how-to-do-fuzzy-matching-on-pandas-dataframe-column-using-python/

        parser = ParsingBase()
        columns_list = list(pd.read_csv(pdf_name, nrows=0).columns.tolist())

        mat2, selected_columns = parser.choose_ratio(columns_list)

        if mat2:
            df = pd.read_csv(pdf_name, usecols=mat2)
            df = df[mat2]

            date_column = df[df.columns[0]]
            parser.change_type(df.loc[0, df.columns[0]], date_column, df)

            new_df = parser.order_dataframe(df, selected_columns)

            new_df = parser.unify_amount_columns(new_df)

            self.df = new_df
            # print(self.df)