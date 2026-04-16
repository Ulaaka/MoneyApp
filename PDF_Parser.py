import camelot
import pandas as pd
import pdfplumber
from BASE_Classes import ParsingBase
import pandas as pd
import re

class ParsingPDF:

    """
    Parses the file with pdf format
    """

    def __init__(self, pdf_name):

        flavor_choice = self.flavor_decision(pdf_name, 0)
        tables = self.run_camelot(pdf_name, flavor_choice)
        self.parser = ParsingBase()
        self.df = []
        for idx, table in enumerate(tables):
            df = table.df
            dataframes = self.clean_up(df, idx)
            for dataframe in dataframes:

                columns = self.parser.choose_ratio(dataframe.columns.tolist())

                dataframe = dataframe[columns[0]]
                new_dataframe = self.parser.order_dataframe(dataframe, columns[1])
                # needs to check the format
                new_dataframe = self.parser.unify_amount_columns(new_dataframe)

                money_columns = [new_dataframe.columns[-1], new_dataframe.columns[-2]]
                for i in money_columns:
                    # turn the values into a str, and replace comma to convert into numeric
                    #https://stackoverflow.com/questions/56947333/how-to-remove-commas-from-all-the-column-in-pandas-at-once
                    dataframe[i] = pd.to_numeric(new_dataframe[i].astype(str).str.replace(',', ''), errors='coerce')

                self.df.append(new_dataframe)

    # Selects the valid headers of the csv file dataframe
    def select_header(self, index, header_Values, size_columns):
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
            if (length_count != size_columns):
                length = False

            if (string == True and unique == True and length == True):
                return index
            else:
                return 0

    # Selects the header of the dataframe
    def find_header(self, df):
        for i in range(min(15, len(df))):
            row = df.iloc[i]

            header_Values = row.tolist()
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

    # Cleans the returned dataframe after extraction of pdf file
    def pre_clean_up(self, value):
        if value is None or not value or not isinstance(value, str):
            return value

        if (value[-1] == "."):
            value = value[:-1]

        if ("\n" in value):
            value = value.split("\n")[-1]

        value = re.sub(r'[^A-Za-z0-9 -./]+', '', value)
        try:
            value = float(value.replace(",", "").replace('"', ""))
        except:
            pass

        return value

    # Cleans dataframe/s extracted from pdf pages, by checking the validity and requirements
    def clean_up(self, df, idx):

        df = df.drop_duplicates()

        # https://stackoverflow.com/questions/39475978/apply-function-to-each-cell-in-dataframe
        df = df.map(self.pre_clean_up)

        header = self.find_header(df)
        df.columns = df.iloc[header]
        df = df.reset_index(drop=True)

        dataframe_list = []
        rows_to_drop = []

        for j in range(len(df)):
            has_numbers = False
            row = df.iloc[j].tolist()
            for item in row:
                try:
                    float(item)
                    has_numbers = True
                    break
                except:
                    continue

            if (has_numbers == False):
                rows_to_drop.append(j)

        df = df.drop(rows_to_drop)
        df = df.reset_index(drop=True)

        if not df.empty:
            test_value = df.loc[0, df.columns[0]]
            self.parser.change_type(test_value, df[df.columns[0]], df)
            dataframe_list.append(df)
            # return dataframe_list

        return dataframe_list

    # Read pdf based on the given flavor
    def run_camelot(self, name, flavor_camelot):
        if (flavor_camelot == "stream"):
            tables = camelot.read_pdf(name, flavor=flavor_camelot ,pages='all', row_tol = 20)
        else:
            tables = camelot.read_pdf(name, flavor=flavor_camelot, pages='all', line_scale=40)
        return tables

    # Chooses the right method for extracting dataframe from pages of pdf after detecting number of rectangles
    def flavor_decision(self, name, idx):
        with pdfplumber.open(name) as pdf:
            page = pdf.pages[idx]
            header_rects = [
            r for r in page.rects
            if r['height'] > 5
            and r['height'] < 100
            and r['width'] < 200
        ]
        if len(header_rects) > 15:
            return "lattice"
        return "stream"
