from CSV_Parser import ParsingCSV
from DF_Processor import ProcessingDF
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
from PDF_Parser import ParsingPDF
#parsing = ParsingCSV("Transaction_data_original.csv")

parsing = HSBC_PDF_CONVERSION("2025-06-20_Statement.pdf")
processor = ProcessingDF(parsing.df, "test4", "Ulaaka_1223", "huhu", "Bank", "GBP")

#converted = ParsingPDF("Statement_12_2025.pdf")

