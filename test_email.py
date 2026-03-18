import os
import certifi
import sys
from system_functions import system_functions

system = system_functions()
# Add the project root to Python path
sys.path.insert(0, '/Users/nyamdorjbat-erdene/Final_year')

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings' 
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

import django
django.setup()

from system_functions import system_functions

system = system_functions()
number = system.send_reset_digits(6, 'test5')
print(number)