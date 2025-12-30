from parsingCSV import csv_parsing
from dataProcessor import csvProcessor
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
# parsing = csv_parsing("Transaction_data_original.csv")

parsing = HSBC_PDF_CONVERSION("2025-06-20_Statement.pdf")
# processor = csvProcessor(parsing.df, "test2", "knongoroo1223", "gurgaldai", "Bank", "GBP")

