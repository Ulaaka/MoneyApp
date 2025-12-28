from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import dateutil.parser
from datetime import datetime


class csv_parsing():

    def __init__(self, pdf_name):

        # df = pd.read_csv("TransactionData.csv")
        # https://www.geeksforgeeks.org/python/how-to-do-fuzzy-matching-on-pandas-dataframe-column-using-python/

        self.expecting = ["Date", ["Type" , "Category"], [ "Details", "Description", "Reference", "Narrative"], ["Credit Amount", "Withdrawal", "Out"], ["In", "Debit Amount", "Received", "Deposit"], "Balance"]

        mat2, selected_columns = self.choose_ratio(self.expecting, pdf_name)

        if mat2:
            df = pd.read_csv(pdf_name, usecols=mat2)
            df = df[mat2]
            date_list = df[df.columns[0]].tolist()
            date_column = df[df.columns[0]]
            self.change_type(date_list, date_column, df)
            new_df = self.order_dataframe(df, selected_columns)
            new_df = new_df.loc[:,~df.columns.duplicated()].copy()
            self.df = new_df
            print(self.df)

    def order_dataframe(self, df, columns):
        extra = list(set(range(6)) - set(columns))

        if (extra == 0):
            return df
        print(extra)

        for i in extra:
            if (i == 1):
                df.insert(i, "Type", "")
            elif (i == 2):
                df.insert(i, "Description", "")
            else:
                raise Exception("Important column is not selected")
        return df

    def check_date_type(self, dateList):
        try:
            datetime.strptime(dateList[0], "%d/%m/%Y")
            return True
        except ValueError:
            return False
        
    # https://stackoverflow.com/questions/52206973/convert-different-date-formats-to-a-given-unique-date-format-in-python
    def change_type(self, dateList, column, dataframe):
        if not self.check_date_type(dateList):
            for i in column:
                column = column.replace([i], dateutil.parser.parse(i).strftime("%Y/%m/%d"))
        dataframe[dataframe.columns[0]] = column


    def choose_ratio(self, expect, name_pdf):
        mat1 = []
        mat2 = []
        columns = list(pd.read_csv(name_pdf, nrows=0).columns.tolist())
        
        for i in expect:
            if not isinstance(i, list):
                mat1.append(process.extractOne(i, columns, scorer=fuzz.partial_ratio))
            else:
                group_results = []
                for j in i:
                    matches = process.extractOne(j, columns, scorer=fuzz.partial_ratio)
                    group_results.append(matches)
                mat1.append(group_results)

        above = 70
        chosen_columns = []
        for idx, i in enumerate(mat1):
            if not isinstance(i, list):
                if (i[1] > above):
                    mat2.append(i[0])
                    chosen_columns.append(idx)
            else:
                highest = 0
                highIdx = None
                for sub_idx, j in enumerate(i):
                    if (j[1] > highest and j[1] >above):
                        highest = j[1]
                        highIdx = sub_idx

                if highIdx is not None:
                    element = i[highIdx][0]
                    mat2.append(element)
                    chosen_columns.append(idx)

        try:
            if (mat2[-1] == mat2[-2]):
                mat2.pop()
        except:
            print("The table is not related to transaction")

        return mat2, chosen_columns
