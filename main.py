"""An Automated Rental Finder

This script researches house prices that fit a particular criteria
for a client using the 'Zillow' website. The data will be transferred into
a form, which will create a spreadhseet in 'Google Sheets'. This script
requires that the user create a 'Google Sheet' that has 3 fields:
'Address of the property', 'Price per month', and 'Link to the property'.

This script requires that 'selenium', 'requests', 'bs4',
 're', and 'python_dotenv' be installed within the Python
environment you are running this script in. The user
must also have a WebDriver.

"""

from rental_finder import RentalFinder
CHROME_EXECUTABLE_PATH = 'C:\\Development\\chromedriver.exe'

rental_finder_bot = RentalFinder(CHROME_EXECUTABLE_PATH)
rental_finder_bot.parse_html()
rental_finder_bot.fill_forms()