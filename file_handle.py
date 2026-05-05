
import os, tempfile, shutil
from decouple import config

from base_classes import CryptoHelper
from csv_parser import ParsingCSV
from df_processor import ProcessingDF
from hsbc_pdf_parser import ParsingPdfHSBC
from pdf_parser import ParsingPDF
from db_queries import QueryProcessor

class FileHandling():

    """
    Contains functions for managing files
    """

    def __init__(self, userID, accountID, key):
        """
        Constructor for file handling class
        """

        self.accountID = accountID
        self.key = key
        self.userID = userID
        self.query = QueryProcessor()
        # holds temporarily created files to delete when the app closes
        self.temp_files = []

    def show_decrypted_pdf(self, decrypted_text, pdf_flag=None):
        """
        Returns temporary decrypted text in PDF or CSV format

        :param decrypted_text: the text to be displayed
        :param pdf_flag: If true, set the suffix as PDF, else CSV
        :return: temporary file to be displayed
        """
        suffix_str = ".csv"
        if (pdf_flag):
            suffix_str = ".pdf"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix_str) as tmp:
            tmp.write(decrypted_text)
            tmp.flush()
        return tmp.name

    def view_file(self, original_filename=None, fileID=None):
        """
        Opens encrypted file in different formats by decrypting
        :param original_filename: name of the file
        :param fileID: ID of the file
        """
        crypto = CryptoHelper()
        query = QueryProcessor()

        flag = False
        # Folder where the file exists (under the account account sub folder)
        sub_save_folder = os.path.join(config('SAVE_FOLDER'),f"account_{self.accountID}")

        if fileID:
            current_filename = query.get_file_name(self.accountID, fileID=fileID)
        elif original_filename:
            current_filename = original_filename

        decrypted_text = crypto.decrypt(sub_save_folder, self.key, self.accountID,filename=current_filename)
        if (current_filename.split(".")[1] == "pdf"):
            flag = True

        temp_name = self.show_decrypted_pdf(decrypted_text, pdf_flag=flag)

        # Append to the list  to later delete when the application closes
        self.temp_files.append(temp_name)
        self.open_temp_file(temp_name)


    def delete_encrypted_file(self, accountID, hashed_name):
        """
        Deleted the encrypted file from the encryption folder
        """
        sub_save_folder = os.path.join(config('SAVE_FOLDER'),f"account_{accountID}")
        for encrypted_file in os.listdir(sub_save_folder):
            if (hashed_name == encrypted_file):
                file_path = os.path.join(sub_save_folder, encrypted_file)
                os.remove(file_path)

    def delete_temp_file(self, temp_name):
        """
        Deletes the temporary pdf file
        """
        os.unlink(temp_name)

    def open_temp_file(self, temp_name):
        """
        Opens the temporary pdf file
        """
        os.system(f"open {temp_name}")

    def check_file_exists(self, sub_save_folder, file_path, filename):
        """
        Checks if the file with the same content exists by checking the save folder for encrypted files
        :return found: is true when duplicate file exists
        :return output: if exist, return the existing file's name
        """
        crypto = CryptoHelper()
        found = False
        output = ""

        for encrypted_file in os.listdir(sub_save_folder):
            decrypted = crypto.decrypt(sub_save_folder, self.key, self.accountID, hashed_filename=encrypted_file)
            # Compare the size first to prevent from fully decrypting
            if os.path.getsize(file_path) == len(decrypted):
                with open(file_path, 'rb') as file:
                    if file.read() == decrypted:
                        # find the submitted existing file_name in the folder
                        existing_name = self.query.get_file_name(self.accountID, hashed_name=encrypted_file)
                        found = True
                        output = f'\tThe file {filename} already exists as <a href="file:{existing_name}">{existing_name}</a>'
                        break
        return found, output

    def process_files_in_folder(self):
        """
        Parses the files in the submission ("FOLDER_PATH") folder using the corresponding parsing techniques
        print statements are captured in a window for the user to see the loading of the files
        Deletes and recreates the submission folder once the files processed
        """
        crypto = CryptoHelper()
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

                found, output = self.check_file_exists(sub_save_folder, file_path, filename)
                flag = found

                # if the file does not exist
                if flag is False:
                    if (filename.endswith(".csv")):
                        parsing = ParsingCSV(file_path)
                    else:
                        try:
                            parsing = ParsingPDF(file_path)
                        except:
                            parsing = ParsingPdfHSBC(file_path)
                    parsed_count+=1
                    size_file = os.path.getsize(file_path)
                    file_ID = crypto.encrypt(sub_save_folder, config('FOLDER_PATH'), filename, self.key, self.accountID, size_file, file_type)
                    ProcessingDF(parsing.df, file_ID, self.userID, self.accountID)
                else:
                    existing_file_output.append(output)
            else:
                print("Incompatible file/s has been submitted")
                return
        print(f"{parsed_count}/{len(dir)} files loaded successfully")

        # Deletes the file folder/files inside and recreate it
        file_folder = config("FOLDER_PATH")
        shutil.rmtree(file_folder)
        os.mkdir(file_folder)

        if (len(existing_file_output) > 0):
            print(f"Skipped duplicates:\n")
            for i in existing_file_output:
                print(i)

    def convert_file_size(self, size):
        """
        Converts the size of the file into a string format
        :return converted_size: converted file size
        """
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
