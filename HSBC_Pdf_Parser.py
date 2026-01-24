import pandas as pd
import pdfplumber
import re 
from datetime import datetime
import dateutil.parser
from BASE_Classes import ParsingBase
# https://github.com/Anlanther/bank-statement-converter/blob/main/src/classes/BOCStatement.py#L28
class HSBC_PDF_CONVERSION:
    def __init__(self, pdf_name):
        text = self.return_text(pdf_name)
        detected_transactions = self.detect_transactions(text)
        self.corrected_transaction = self.correct_transactions(detected_transactions)
        self.classified_transactions = self.classify_transactions(self.corrected_transaction)
        parser = ParsingBase()

        df = pd.DataFrame(self.classified_transactions)
        date_list = df[df.columns[0]].tolist()
        date_column = df[df.columns[0]]
        parser.change_type(date_list, date_column, df)
        parser.unify_amount_columns(df)
        self.df = df

        print(self.df.to_string(index=False))
        print("\n" + "="*100)

    def return_text(self, pdf_file):
        with pdfplumber.open(pdf_file) as pdf:
            text_list = []
            for page in pdf.pages:
                text_list.append(page.extract_text(x_tolerance=1))
            return " ".join(text_list)


    def detect_transactions(self, text):
        lines = text.split("\n")

        first = None
        for index, line in enumerate(lines):
            if ("BALANCE BROUGHT FORWARD" in line):
                first = index
                break

        end_lines = []
        for index, line in enumerate(lines):
            if ("BALANCE CARRIED FORWARD" in line):
                end_lines.append(index)
        end = end_lines[-1]

        transaction_lines = []
        for i in lines[first + 1 :end]:
            if "BALANCE BROUGHT FORWARD" in i:
                continue
            if "BALANCE CARRIED FORWARD" in i:
                continue
            transaction_lines.append(i.replace(",", ""))

        return transaction_lines
    

    def new_transaction_func(self, i):
        regex_date = r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2}\b"
        return re.search(regex_date, i)


    def has_balance_func(self, i):
        regex_float = r'\d+\.\d+'
        return re.findall(regex_float, i) 


    def correct_transactions(self, detect):
        carry_balance = "None"
        carry_date = None
        entire_lines = []
        string_carry = ""
        for idx, i in enumerate(detect):
            new_transaction_mark = self.new_transaction_func(i)
            has_balance = self.has_balance_func(i)

            if has_balance and new_transaction_mark:
                if len(has_balance) == 2:
                    entire_lines.append(i)
                else:
                    string_carry = i + " " + carry_balance
                    entire_lines.append(string_carry)
                    carry_date = new_transaction_mark.group()

            elif has_balance:
                if len(has_balance) == 2:
                    string_carry = string_carry + " " + i
                    entire_lines.append(string_carry)
                else:
                    string_carry = string_carry + " " + i + " " + carry_balance
                    entire_lines.append(string_carry)

            elif new_transaction_mark:
                carry_date = new_transaction_mark.group()
                string_carry = i

            else:
                if idx > 0:
                    condition_1 = self.new_transaction_func(detect[idx - 1])
                    condition_2 = self.has_balance_func(detect[idx - 1])
                    
                    if not condition_1 and not condition_2:
                        string_carry = string_carry + " " + i
                    else:
                        string_carry = carry_date + " " + i
                else:
                    string_carry = i
                    
        return entire_lines

    def transaction_type(self, transaction):
        if transaction[10:].split():
            return transaction[10:].split()[0]
        return ''

    def parse_transaction(self, line):

        parts = line.rsplit(maxsplit=2)
        if len(parts) < 3:
            return None
            
        trans_type = self.transaction_type(line)
        
        after_date = parts[0][10:]
   
        return {
            'date' : parts[0][:9],
            'type' : trans_type,
            'description' : after_date[len(trans_type) + 1:] if trans_type else after_date,
            'amount' : float(parts[1]),
            'balance': None if parts[2] == "None" else float(parts[2])
        }

    def classify_transactions(self, transactions, initial_balance=89.78):
        """Classify transactions and create DataFrame with Credit/Debit columns"""
        parsed = []
        for i in transactions:
            result = self.parse_transaction(i)
            if result:
                parsed.append(result)
        
        balance = initial_balance
        values = []
        for dict in parsed:

            credit = None
            debit = None
            
            if dict['type'] == 'CR' or dict['type'] == 'PIM':
                credit = dict['amount']
                if dict['balance'] is not None:
                    balance = dict['balance']
                else:
                    balance = balance + dict['amount']
            else:
                debit = dict['amount']
                if dict['balance'] is not None:
                    balance = dict['balance']
                else:
                    balance = balance - dict['amount']
            
            values.append({
                'Date': dict['date'],
                'Type': dict['type'],
                'Description': dict['description'],
                'Credit': credit,
                'Debit': debit,
                'Balance': balance
            })
        
        return values


