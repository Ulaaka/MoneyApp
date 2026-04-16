
from decouple import config
import os, tempfile, shutil
from BASE_Classes import cryptography
from CSV_Parser import ParsingCSV
from DF_Processor import ProcessingDF
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
from PDF_Parser import ParsingPDF
from queries import query_processor

class file_handling():

    """
    Contains functions for handling files
    """

    def __init__(self, userID, accountID, key):
        self.accountID = accountID
        self.key = key
        self.userID = userID
        self.query = query_processor()
        self.temp_files = []

    # Returns temporary decrypted text file of the file in a pdf format
    def show_decrypted_pdf(self, decrypted_text, pdf_flag=None):
        suffix_str = ".csv"
        if (pdf_flag):
            suffix_str = ".pdf"
        # https://stackoverflow.com/a/75398222
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix_str) as tmp:
            tmp.write(decrypted_text)
            tmp.flush()
        return tmp.name

    def view_file(self, original_filename=None, fileID=None):
        crypto = cryptography()

        flag = False
        query = query_processor()
        sub_save_folder = os.path.join(config('SAVE_FOLDER'),f"account_{self.accountID}")

        if fileID:
            current_filename = query.get_file_name(self.accountID, fileID=fileID)
        elif original_filename:
            current_filename = original_filename

        decrypted_text = crypto.decrypt(sub_save_folder, self.key, self.accountID,filename=current_filename)
        if (current_filename.split(".")[1] == "pdf"):
            flag = True
        temp_name = self.show_decrypted_pdf(decrypted_text, pdf_flag=flag)
        self.temp_files.append(temp_name)
        self.open_temp_file(temp_name)

    def delete_encrypted_file(self, accountID, hashed_name):
        sub_save_folder = os.path.join(config('SAVE_FOLDER'),f"account_{accountID}")
        for encrypted_file in os.listdir(sub_save_folder):
            if (hashed_name == encrypted_file):
                file_path = os.path.join(sub_save_folder, encrypted_file)
                os.remove(file_path)

    # Deletes the temporary pdf file
    def delete_temp_file(self, temp_name):
        os.unlink(temp_name)

    # Opens the temporary pdf file
    def open_temp_file(self, temp_name):
        os.system(f"open {temp_name}")

    # Checks if the file with the same content exists by checking the save folder for encrypted files
    def check_file_exists(self, sub_save_folder, file_path, filename):
        crypto = cryptography()


        found = False
        output = ""

        for encrypted_file in os.listdir(sub_save_folder):
            decrypted = crypto.decrypt(sub_save_folder, self.key, self.accountID, hashed_filename=encrypted_file)
            if os.path.getsize(file_path) == len(decrypted):
                with open(file_path, 'rb') as file:
                    if file.read() == decrypted:
                        # find the submitted existing file_name in the folder
                        existing_name = self.query.get_file_name(self.accountID, hashed_name=encrypted_file)
                        found = True
                        # print(f"The file {filename} already exists as: {existing_name}")
                        output = f'\tThe file {filename} already exists as <a href="file:{existing_name}">{existing_name}</a>'
                        break
        return found, output

    # The functions for handling the parsing of the user input files
    def process_files_in_folder(self):
        crypto = cryptography()
    
        dir = os.listdir(config('FOLDER_PATH'))
        parsed_count = 0
        existing_file_output = []
        for filename in dir:
            if (filename.endswith(".csv") or filename.endswith(".pdf")): 
                file_type = 'PDF Document'
                if filename.endswith(".csv"):
                    file_type = 'CSV Document'

                file_path = os.path.join(config('FOLDER_PATH'), filename)

                # create the folder for the user's account
                sub_save_folder = os.path.join(config('SAVE_FOLDER'),f"account_{self.accountID}")
                if not os.path.exists(sub_save_folder):
                    os.makedirs(sub_save_folder)

                result = self.check_file_exists(sub_save_folder, file_path, filename)
                flag = result[0]

                if flag is False:
                    if (filename.endswith(".csv")):
                        parsing = ParsingCSV(file_path)
                    else:
                        try:
                            parsing = ParsingPDF(file_path)
                        except:
                            parsing = HSBC_PDF_CONVERSION(file_path)
                    parsed_count+=1
                    size_file = os.path.getsize(file_path)
                    file_ID = crypto.encrypt(sub_save_folder, config('FOLDER_PATH'), filename, self.key, self.accountID, size_file, file_type)
                    ProcessingDF(parsing.df, file_ID, self.userID, self.accountID)
                else:
                    existing_file_output.append(result[1])
            else:
                print("Incompatible file/s has been submitted")
                return
        print(f"{parsed_count}/{len(dir)} files loaded successfully")

        # Deletest the file folder/files inside and recreate it
        file_folder = config("FOLDER_PATH")
        shutil.rmtree(file_folder)
        os.mkdir(file_folder)

        if (len(existing_file_output) > 0):
            print(f"Skipped duplicates:\n")
            for i in existing_file_output:
                print(i)

    def convert_file_size(self, size):
        converted_size = ""
        if (size < 1024):
            converted_size = f"{size} Bytes"
        elif (size < 1024**2):
            converted_size = f"{size/1024:.1f} KB"
        elif (size < 1024**3):
            converted_size = f"{size/1024**2:.1f} MB"
        else:
            converted_size =  f"{size/1024**3:.1f} GB"
        return converted_size
