import camelot
import pandas as pd
import csv 
import pdfplumber

def find_header(df):
    print("----------------------------------------")
    for i in range(min(15, len(df))):
        row = df.iloc[i]

        header_Values = row.tolist()

        print(header_Values)
        string = True
        unique = True
        length = True

        length_count = 0
        for item in header_Values:
            if(item != ''):
                length_count+=1

        for j in header_Values:
            if type(j) != str:
                string = False

        if len(header_Values) > len(set(header_Values)):
            unique = False
        if (length_count != len(df.columns)):
            length = False

        if (string == True and unique == True and length == True):
            return i
    return 0
        
def clean_up(table, idx):
    df = table.df
    df = df.drop_duplicates()

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
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    if not df.empty:
        df = df.replace(r'\n', ' ', regex=True) 
        df.to_csv(f'output{idx}.csv', index=False)

def run_camelot(name, flavor_camelot):
    if (flavor_camelot == "stream"):

        # tables = camelot.read_pdf(name, flavor=flavor_camelot, row_tol=18, column_tol=7, edge_tol=25, strip_text='\n \t', split_text=False ,pages='all')
        tables = camelot.read_pdf(name, flavor=flavor_camelot ,pages='all')

    else: 
        tables = camelot.read_pdf(name, flavor=flavor_camelot, pages='all')
    return tables

def flavor_decision(name, idx):
    with pdfplumber.open(name) as pdf:
        page = pdf.pages[idx]

        header_rects = [
        r for r in page.rects 
        if r['height'] > 5 
        and r['height'] < 100 
        and r['width'] < 200
        ]
        im = page.to_image(resolution=150)
        im.draw_rects(header_rects, stroke="red", stroke_width=2)
        im.save('debug_rectangles.png')
        
    if len(header_rects) > 10:
        return "lattice"

    return "stream"
# Statement_12_2025
# fake_pdf
# sample-tables
# KH_P_statement
flavor_choice = flavor_decision('Statement_12_2025.pdf', 0)
tables = run_camelot('Statement_12_2025.pdf', flavor_choice)

for idx, table in enumerate(tables):
    clean_up(table, idx)