
from decouple import config
import os, tempfile
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

    def __init__(self, accountID, key):
        self.accountID = accountID
        self.key = key
        self.crypto = cryptography()
        self.query = query_processor()

    # Returns temporary decrypted text file of the file in a pdf format
    def show_decrypted_pdf(self, decrypted_text):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(decrypted_text)
            tmp.flush()
        return tmp.name

    # Deletes the temporary pdf file
    def delete_temp_file(self, temp_name):
        os.unlink(temp_name)

    # Opens the temporary pdf file
    def open_temp_file(self, temp_name):
        os.system(f"open {temp_name}")

    # Checks if the file with the same content exists by checking the save folder for encrypted files
    def check_file_exists(self, sub_save_folder, file_path, filename):

        found = False
        output = ""
        for encrypted_file in os.listdir(sub_save_folder):
            decrypted = self.crypto.decrypt(sub_save_folder, self.key, self.accountID, hashed_filename=encrypted_file)
            # check the size of the file, avoiding reading the whole files

            if os.path.getsize(file_path) == len(decrypted):
                # if the same size, then read them
                with open(file_path, 'rb') as file:
                    if file.read() == decrypted:
                        # find the submitted existing file_name in the folder
                        existing_name = self.query.get_file_name_from_hashed(self.accountID, encrypted_file)
                        found = True
                        # print(f"The file {filename} already exists as: {existing_name}")
                        output = f'\tThe file {filename} already exists as <a href="file:{existing_name}">{existing_name}</a>'
                        break
        return found, output

    # The functions for handling the parsing of the user input files
    def process_files_in_folder(self):
        dir = os.listdir(config('FOLDER_PATH'))
        parsed_count = 0
        existing_file_output = []
        for filename in dir:
            if (filename.endswith(".csv") or filename.endswith(".pdf")): 

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
                    # print("parsed: ", filename)
                    parsed_count+=1
                    file_ID = self.crypto.encrypt(sub_save_folder, config('FOLDER_PATH'), filename, self.key, self.accountID)
                    ProcessingDF(parsing.df, file_ID, self.accountID)
                else:
                    existing_file_output.append(result[1])
            else:
                raise Exception("Incompatible file/s has been submitted.")
        print(f"{parsed_count}/{len(dir)} files loaded successfully")
        if (len(existing_file_output) > 0):
            print(f"Skipped duplicates:\n")
            for i in existing_file_output:
                print(i)

    # Shows existing files IDs and filename submitted in the account
    def show_files(self, accountID):
        query = """
        SELECT file_ID, file_name
        FROM files
        WHERE accountID = %s
        ORDER BY added_at DESC
        """
        self.cursor.execute(query, (accountID,))
        result = self.cursor.fetchall()
        return result if result else None
