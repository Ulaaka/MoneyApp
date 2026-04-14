from FILE_handling import file_handling
from BASE_Classes import cryptography
from queries import query_processor
from system_functions import system_functions
query = query_processor()
system = system_functions()
result = query.find_min_max(17, 'amount')

result1 = query.total_transfer_or_extreme_value()
