from autotrader.scraper import Scraper
from autotrader.repository import Repository

#set up search parameters
max_distance = 1500
postcode = "rg315nr"
berths = 6
max_price = 25000
keywords = "bunk"

scraper = Scraper()
repo = Repository()

vans = scraper.get_vehicles(max_distance, postcode, berths, max_price, keywords)
repo.store(vans)
