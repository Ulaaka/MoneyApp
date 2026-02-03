from CSV_Parser import ParsingCSV
from DF_Processor import ProcessingDF
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
from PDF_Parser import ParsingPDF
from queries import query_processor
from pathlib import Path
import os
from BASE_Classes import cryptography


#parsing = ParsingCSV("Monzo_csv.csv")
# Monzo_pdf
# TXN_pdf
# 2025_October_Statement
# 2025_September_Statement
#parsing = ParsingPDF(file_path)

#parsing = HSBC_PDF_CONVERSION("2025-06-20_Statement.pdf")
#processor = ProcessingDF(parsing.df, "test5", "Ulaaka_1223", "urnaa@gmail.com", "savings", "Bank", "GBP")
#converted = ParsingPDF("Statement_12_2025.pdf")

#query = query_processor()
#date_upper="2025-06-03"
#query.total_transfer_or_extreme_value("test5", "2025-06-03")


#last_day = query.return_last_month("2025-11-13")
# exp = query.compare_range("test5", False, "savings", "2025-11-07", "2025-12-23", "date")
#query.common_transactions("test5",  5, account_name="savings",transfer_toggle=False, date_lower="2025-12-23", filter_amount=5)

# https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory
query = query_processor()
password = 'Ulaaka_1223'
username = "test5"
account_name =  "savings"
query = query_processor()

folder_path = '/Users/nyamdorjbat-erdene/Final_year/file_storage'
save_folder = '/Users/nyamdorjbat-erdene/Final_year/encrypted_storage'

password = 'Ulaaka_1223'
username = "test5"
account_name =  "savings"
query = query_processor()

for filename in os.listdir(folder_path):
    if (filename.endswith(".csv") or filename.endswith(".pdf")): 
        crypto = cryptography()

        file_ID = crypto.encrypt(save_folder, folder_path, filename, password, username, account_name)

        file_path = os.path.join(folder_path, filename)
        if (filename.endswith(".csv")):
            parsing = ParsingCSV(file_path)
        else:
            try:
                parsing = ParsingPDF(file_path)
            except:
                parsing = HSBC_PDF_CONVERSION(file_path)

        processor = ProcessingDF(parsing.df, username, password, "urnaa@gmail.com", account_name, "Bank", file_ID,  "GBP")
    else:
        raise Exception("Incompatible file/s has been submitted.")
