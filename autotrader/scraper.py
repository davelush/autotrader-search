import math
import requests
from bs4 import BeautifulSoup
import re
from autotrader.vehicle import Vehicle


class Scraper:
    def __init__(self):
        self.base_url = "https://www.autotrader.co.uk"
        super(Scraper, self).__init__()

    @staticmethod
    def get_number_of_results(soup):
        result_count_h1 = soup.find("h1", "search-form__count js-results-count")
        result_count_str = result_count_h1.contents[0]
        result_count_str = result_count_str.replace(" motorhomes found", "")
        return math.ceil(int(result_count_str) / 10)

    def get_search_page(self, max_distance, postcode, berth, max_price, keywords, page):
        url = f"{self.base_url}/motorhome-search?" \
              f"sort=price-asc&" \
              f"radius={max_distance}&" \
              f"postcode={postcode}&" \
              f"berth={berth}&" \
              f"price-to={max_price}&" \
              f"keywords={keywords}&" \
              f"page={page}"
        result = requests.get(url)
        c = result.content
        soup = BeautifulSoup(c, features="html.parser")
        return soup

    def get_vehicle(self, uid, van_soup):
        vehicle = Vehicle(uid)

        # get a link for the thumbnail image
        image_fig = van_soup.find("figure", "listing-main-image")
        vehicle.thumbnail = image_fig.find("img").attrs.get("src")

        # get the link
        link_h2 = van_soup.find("h2", "listing-title title-wrap")
        link_a = link_h2.find("a")
        link_str = link_a.attrs['href']
        link_arr = link_str.split("?")
        vehicle.link = f"{self.base_url}{link_arr[0]}"

        # get a title for the vehicle
        info_container = van_soup.find("div", "information-container")
        title_h2 = info_container.find("h2", "listing-title title-wrap")
        vehicle.title = title_h2.find("a").contents[0]

        # get a price
        price_div = van_soup.find("div", "vehicle-price")
        price_str = price_div.contents[0]
        price_str = price_str.replace("£", "")
        price_str = price_str.replace(",", "")
        vehicle.price = int(price_str)

        # get the town & distance from the location
        seller_location = van_soup.find("div", "seller-location")
        seller_town = seller_location.find("span", "seller-town")
        if seller_town is not None and len(seller_town.contents) > 0:
            vehicle.town = seller_town.contents[0]
        else:
            vehicle.town = "unknown"
        for content in seller_location:
            if " miles away" in content:
                miles_str = content.replace("\n", "")
                miles_str = miles_str.replace(" - ", "")
                miles_str = miles_str.replace(" miles away", "")
                miles_str = miles_str.replace(" ", "")
                vehicle.distance = int(miles_str)

        # get a bunch of key specs where possible
        key_specs_li = van_soup.find("ul", "listing-key-specs")
        key_specs_list = key_specs_li.findAll("li")
        extras = ''
        for spec_li in key_specs_list:
            spec = spec_li.contents[0]
            if re.match(r'[1-3][0-9]{3}', spec):
                vehicle.year = spec
                # print("spec is a YEAR")
            elif " berth" in spec:
                vehicle.berth = int(spec.replace(" berth", ""))
                # print("spec is a BERTH")
            elif " miles" in spec:
                miles = int(spec.replace(" miles", "").replace(",", ""))
                vehicle.miles = miles
                # print("spec is a MILEAGE")
            elif "Manual" in spec or "Auto" in spec:
                vehicle.transmission = spec
                # print("spec is a TRANSMISSION")
            elif "belted" in spec:
                vehicle.seats = spec
                # print("spec is a SEATS")
            elif re.match(r'[0-9]\.[0-9][L]', spec):
                vehicle.engine = spec
                # print("spec is an ENGINE")
            else:
                extras = f"{extras}{spec} | "
        extras = extras.rstrip(" | ")
        vehicle.extras = extras

        return vehicle

    def get_vehicles(self, max_distance, postcode, berths, max_price, keywords):
        num_pages = 1000
        page = 1
        vans = []
        while page <= num_pages:
            soup = self.get_search_page(max_distance, postcode, berths, max_price, keywords, page)
            num_pages = self.get_number_of_results(soup)
            results_soup = soup.findAll("li", "search-page__result")
            for van_soup in results_soup:
                uid = van_soup.attrs.get('id')
                if uid is not None:
                    van = self.get_vehicle(uid, van_soup)
                    if van.price <= max_price:
                        vans.append(van)
                    else:
                        print(f"trimming out featured van costing {van.price} {van.thumbnail}")
            page += 1
        return vans
