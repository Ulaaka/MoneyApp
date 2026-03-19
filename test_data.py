from FILE_handling import file_handling
from BASE_Classes import cryptography

exp_folder = '/Users/nyamdorjbat-erdene/Final_year/exp_folder'

crypto = cryptography()
key = crypto.generate_key("Ulaaka%1223")
file_execute = file_handling(1, key)
file_execute.process_files_in_folder()
print("finished executing")

