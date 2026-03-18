from CSV_Parser import ParsingCSV
from DF_Processor import ProcessingDF
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
from PDF_Parser import ParsingPDF
from queries import query_processor
from pathlib import Path
import os
from BASE_Classes import cryptography, password_class
from system_functions import system_functions


#parsing = ParsingCSV("Monzo_csv.csv")
# Monzo_pdf
# TXN_pdf
# 2025_October_Statement
# 2025_September_Statement
#parsing = ParsingPDF(file_path)

#parsing = HSBC_PDF_CONVERSION("2025-06-20_Statement.pdf")
#processor = ProcessingDF(parsing.df, "test5", "Ulaaka_1223", "urnaa@gmail.com", "savings", "Bank", "GBP")
#converted = ParsingPDF("Statement_12_2025.pdf")

#date_upper="2025-06-03"
#query.total_transfer_or_extreme_value("test5", "2025-06-03")


#last_day = query.return_last_month("2025-11-13")
# exp = query.compare_range("test5", False, "savings", "2025-11-07", "2025-12-23", "date")
#query.common_transactions("test5",  5, account_name="savings",transfer_toggle=False, date_lower="2025-12-23", filter_amount=5)

# https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory
folder_path = '/Users/nyamdorjbat-erdene/Final_year/file_storage'
save_folder = '/Users/nyamdorjbat-erdene/Final_year/encrypted_storage'
exp_folder = '/Users/nyamdorjbat-erdene/Final_year/exp_folder'
# /Users/nyamdorjbat-erdene/Final_year/2025_October_Statement.pdf
password = 'Ulaaka_1223'
username = "test5"
account_name =  "savings"
email = "urnaa@gmail.com"
account_type = "Bank"
account_currency = "GBP"
query = query_processor()
for filename in os.listdir(exp_folder):
    if (filename.endswith(".csv") or filename.endswith(".pdf")): 

        crypto = cryptography()
        password_manager = password_class()
        hashed_password = password_manager.hash_password(password)
        userID = query.insert_user(username, password, email)
        accountID = query.insert_account(userID, account_name, account_type, account_currency)

        file_path = os.path.join(exp_folder, filename)

        # create the folder for the user's account
        sub_save_folder = os.path.join(save_folder,f"account_{accountID}")
        if not os.path.exists(sub_save_folder):
            os.makedirs(sub_save_folder)

        found = False
        for encrypted_file in os.listdir(sub_save_folder):
            decrypted = crypto.decrypt(sub_save_folder, password, username, account_name, hashed_filename=encrypted_file)
            # check the size of the file, avoiding reading the whole files
            if os.path.getsize(file_path) == len(decrypted):
                # if the same size, then read them
                with open(file_path, 'rb') as file:
                    if file.read() == decrypted:
                        # find the submitted existing file_name in the folder
                        existing_name = query.get_file_name_from_hashed(accountID, encrypted_file)
                        found = True
                        print(f"The same file already exists: {existing_name}")
                        break

        if found is False:
            if (filename.endswith(".csv")):
                parsing = ParsingCSV(file_path)
            else:
                try:
                    parsing = ParsingPDF(file_path)
                except:
                    parsing = HSBC_PDF_CONVERSION(file_path)

            print("parsed: ", filename)
            file_ID = crypto.encrypt(sub_save_folder, exp_folder, filename, password, accountID)
            processor = ProcessingDF(parsing.df, username, password, email, account_name, account_type, file_ID,  account_currency)
    else:
        raise Exception("Incompatible file/s has been submitted.")


query = query_processor()
# "TESCO STORES 5243"
#query.change_category(1, "shopping", 228)
#result = query.get_categories(1)
# result = query.show_description_list_by_category_name(1, "grocery")
"""description  = "Lidl Liverpool GB"
category = query.return_updated_category(description)
transaction = [(1, 7, "2026-03-11", "Deposit", description, category, "50", "1000")]
query.insert_into_transactions(transaction)
"""
# result = query.add_description_into_list_category(1, "lidl Cosmetic Surgery Mongolia", "cosmetic")

#result = query.remove_description_from_list_category(1, 7, "cosmetic")
#query.update_transaction_after_deletion_description(1, "cosmetic")

"""system = system_functions()
random = system.generate_random_digits(6)
print(random)"""

"""password = password_class()
new_password = password.change_password(1, "Bi20031223torson")"""