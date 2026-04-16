from FILE_handling import file_handling
from BASE_Classes import cryptography
from queries import query_processor
from system_functions import system_functions
query = query_processor()
system = system_functions()
result = query.find_min_max(17, 'amount')

#result1 = query.total_transfer_or_extreme_value(1, 1, transfer_toggle=True, max_toggle=True, date_lower="2025-12-20", date_upper="2026-01-16")
result = query.common_transactions(1, 5, 1, True, "2025-08-20", "2026-01-16")
print(result)