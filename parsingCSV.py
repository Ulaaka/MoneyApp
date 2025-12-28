from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import pandas as pd
import dateutil.parser
from datetime import datetime
# df = pd.read_csv("TransactionData.csv")
# https://www.geeksforgeeks.org/python/how-to-do-fuzzy-matching-on-pandas-dataframe-column-using-python/

expecting = ["Date", ["Type" , "Category"], ["Number", "Acc", "IBAN"],
             [ "Details", "Description", "Reference", "Narrative"], ["Credit Amount", "Withdrawal", "Out"], ["In", "Debit Amount", "Received", "Deposit"], "Balance"
             ]

# https://stackoverflow.com/questions/52206973/convert-different-date-formats-to-a-given-unique-date-format-in-python
def change_type(dateList, column, dataframe):
    if not check_date_type(dateList):
        for i in column:
            column = column.replace([i], dateutil.parser.parse(i).strftime("%Y/%m/%d"))
    dataframe[dataframe.columns[0]] = column

def check_date_type(dateList):
    try:
        datetime.strptime(dateList[0], "%d/%m/%Y")
        return True
    except ValueError:
        return False

def choose_ratio(expect, name_pdf):
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

    print(mat1)

    above = 70
    for i in mat1:
        if not isinstance(i, list):
            if (i[1] > above):
                mat2.append(i[0])
        else:
            highest = 0
            highIdx = None
            for idx, j in enumerate(i):
                if (j[1] > highest and j[1] >above):
                    highest = j[1]
                    highIdx = idx

            if highIdx is not None:
                element = i[highIdx][0]
                mat2.append(element)

    try:
        if (mat2[-1] == mat2[-2]):
            mat2.pop()
    except:
        print("The table is not related to transaction")

    return mat2

mat2 = choose_ratio(expecting, "output0.csv")
if mat2:
    new_df = pd.read_csv("output0.csv", usecols=mat2)
    new_df = new_df[mat2]
    date_list = new_df[new_df.columns[0]].tolist()
    date_column = new_df[new_df.columns[0]]
    change_type(date_list, date_column, new_df)
    print(new_df.columns.values)
    print(new_df)
