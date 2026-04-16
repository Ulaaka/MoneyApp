
import pandas as pd
from base_classes import ParsingHelper

class ParsingCSV:

    """
    Parses CSV formatted file
    """

    def __init__(self, pdf_name):
        """
        Constructor for parsing csv

        Calls helper functions and saves the resulting dataframe in self.df
        """

        parser = ParsingHelper()
        columns_list = list(pd.read_csv(pdf_name, nrows=0).columns.tolist())

        mat2, selected_columns = parser.choose_ratio(columns_list)

        if mat2:
            df = pd.read_csv(pdf_name, usecols=mat2)
            df = df[mat2]

            date_column = df[df.columns[0]]
            parser.change_date_type(df.loc[0, df.columns[0]], date_column, df)

            new_df = parser.order_dataframe(df, selected_columns)

            new_df = parser.unify_amount_columns(new_df)

            self.df = new_df
