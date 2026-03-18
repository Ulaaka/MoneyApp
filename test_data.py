from CSV_Parser import ParsingCSV
from DF_Processor import ProcessingDF
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
from PDF_Parser import ParsingPDF
from queries import query_processor
from pathlib import Path
from BASE_Classes import cryptography, password_class
from system_functions import system_functions
import os, tempfile

def show_decrypted_pdf(decrypted_text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(decrypted_text)
        tmp.flush()
    return tmp.name

def delete_temp_file(temp_name):
    os.unlink(temp_name)

def open_temp_file(temp_name):
    os.system(f"open {temp_name}")

# needs to be fixed
def check_file_exists(sub_save_folder):
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
                    print(f"The file {filename} already exists as: {existing_name}")
                    break
    return found


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
for filename in os.listdir(folder_path):
    if (filename.endswith(".csv") or filename.endswith(".pdf")): 

        crypto = cryptography()
        password_manager = password_class()
        hashed_password = password_manager.hash_password(password)
        userID = query.insert_user(username, password, email)
        accountID = query.insert_account(userID, account_name, account_type, account_currency)

        file_path = os.path.join(folder_path, filename)

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
                        print(f"The file {filename} already exists as: {existing_name}")
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
            file_ID = crypto.encrypt(sub_save_folder, folder_path, filename, password, accountID)
            processor = ProcessingDF(parsing.df, username, password, email, account_name, account_type, file_ID,  account_currency)
    else:
        raise Exception("Incompatible file/s has been submitted.")

