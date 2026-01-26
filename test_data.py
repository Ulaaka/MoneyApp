from CSV_Parser import ParsingCSV
from DF_Processor import ProcessingDF
from HSBC_Pdf_Parser import HSBC_PDF_CONVERSION
from PDF_Parser import ParsingPDF
from queries import query_processor


#parsing = ParsingCSV("Transaction_data_original.csv")

#parsing = HSBC_PDF_CONVERSION("2025-06-20_Statement.pdf")
#processor = ProcessingDF(parsing.df, "test5", "Ulaaka_1223", "batzayabtrdn@gmail.com", "savings", "Bank", "GBP")
#converted = ParsingPDF("Statement_12_2025.pdf")

query = query_processor()
query.total_transfer_or_extreme_value("test5", date_upper="2025-06-03 00:00:00", max_toggle=False)

