import camelot
import pandas as pd
import csv 
import pdfplumber

def find_header(df):
    for i in range(min(8, len(df))):
        row = df.iloc[i]
        header_Values = row.tolist()

        empty = False
        string = True
        unique = True
        length = True

        for j in header_Values:
            if pd.isna(j) or j == '':
                empty = True
                break
            if type(j) != str:
                string = False

        if len(header_Values) > len(set(header_Values)):
            unique = False
        if (len(header_Values) != len(df.columns)):
            length = False
        if (empty == False and string == True and unique == True and length == True):
            return i
    return 0
        
def clean_up(table, idx):
    df = table.df.drop_duplicates()

    for j in range(len(df)):

        for i in range(len(df.columns)):
            value = str(df.iat[j, i]).strip()

            if (len(value) > 0 ):
                if (value[-1] == "."):
                    try:
                        df.iat[j, i] = float(value[:-1].replace(",", "").replace('"', ""))
                    except:
                        df.iat[j, i] = value[:-1]
                else:
                    try:
                        df.iat[j, i] = float(value.replace(",", "").replace('"', ""))
                    except:
                        pass

    header = find_header(df)
    df.columns = df.iloc[header]
    df = df.reset_index(drop=True) 
    rows_to_drop = []

    for j in range(len(df)):
        has_numbers = False
        row = df.iloc[j].tolist()
        for item in row:
            if isinstance(item, (int, float)):
                has_numbers = True
                break

        if (has_numbers == False):
            rows_to_drop.append(j)

    df = df.drop(rows_to_drop)
    df = df.reset_index(drop=True)
    if not df.empty:
        df = df.replace(r'\n', ' ', regex=True) 
        df.to_csv(f'output{idx}.csv', index=False)

def run_camelot(name, flavor_camelot):
    tables = camelot.read_pdf(name, flavor=flavor_camelot, pages='all')
    return tables

def flavor_decision(name, idx):
    with pdfplumber.open(name) as pdf:
        page = pdf.pages[idx]

        count = len(page.rects)
    if count > 10:
        return "lattice"

    return "stream"

flavor_choice = flavor_decision('Statement_12_2025.pdf', 0)
tables = run_camelot('Statement_12_2025.pdf', flavor_choice)

for idx, table in enumerate(tables):
    clean_up(table, idx)