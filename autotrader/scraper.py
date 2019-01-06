import math
import requests
from bs4 import BeautifulSoup
import re


class Scraper:
    def __init__(self):
        super(Scraper, self).__init__()

    @staticmethod
    def get_number_of_results(soup):
        result_count_h1 = soup.find("h1", "search-form__count js-results-count")
        result_count_str = result_count_h1.contents[0]
        result_count_str = result_count_str.replace(" motorhomes found", "")
        return math.ceil(int(result_count_str) / 10)

    @staticmethod
    def get_search_page(max_distance, postcode, berth, max_price, keywords, page):
        url = f"https://www.autotrader.co.uk/motorhome-search?" \
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

    @staticmethod
    def get_van_dict(uid, van_soup):
        response = {"uid": uid}

        # get a link for the thumbnail image
        image_fig = van_soup.find("figure", "listing-main-image")
        response['thumbnail'] = image_fig.find("img").attrs.get("src")

        # get a title for the vehicle
        info_container = van_soup.find("div", "information-container")
        title_h2 = info_container.find("h2", "listing-title title-wrap")
        response['title'] = title_h2.find("a").contents[0]

        # get a price
        price_div = van_soup.find("div", "vehicle-price")
        price_str = price_div.contents[0]
        price_str = price_str.replace("£", "")
        price_str = price_str.replace(",", "")
        response['price'] = int(price_str)

        # get the town & distance from the location
        seller_location = van_soup.find("div", "seller-location")
        seller_town = seller_location.find("span", "seller-town")
        if seller_town is not None and len(seller_town.contents) > 0:
            response['town'] = seller_town.contents[0]
        else:
            response['town'] = "unknown"
        for content in seller_location:
            if " miles away" in content:
                miles_str = content.replace("\n", "")
                miles_str = miles_str.replace(" - ", "")
                miles_str = miles_str.replace(" miles away", "")
                miles_str = miles_str.replace(" ", "")
                response['distance'] = int(miles_str)

        # get a bunch of key specs where possible
        key_specs_li = van_soup.find("ul", "listing-key-specs")
        key_specs_list = key_specs_li.findAll("li")
        extras = ''
        for spec_li in key_specs_list:
            spec = spec_li.contents[0]
            if re.match(r'[1-3][0-9]{3}', spec):
                response['year'] = spec
                # print("spec is a YEAR")
            elif " berth" in spec:
                response['berth'] = spec.replace(" berth", "")
                # print("spec is a BERTH")
            elif " miles" in spec:
                miles = int(spec.replace(" miles", "").replace(",", ""))
                response['miles'] = miles
                # print("spec is a MILEAGE")
            elif "Manual" in spec or "Auto" in spec:
                response['transmission'] = spec
                # print("spec is a TRANSMISSION")
            elif "belted" in spec:
                response['seats'] = spec
                # print("spec is a SEATS")
            elif re.match(r'[0-9]\.[0-9][L]', spec):
                response['engine'] = spec
                # print("spec is an ENGINE")
            else:
                extras += spec + " | "
        extras = extras.rstrip(" | ")
        response['extras'] = extras

        return response

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
                    van = self.get_van_dict(uid, van_soup)
                    if van['price'] <= max_price:
                        vans.append(van)
                        print(van)
                    else:
                        print(f"trimming out featured van costing {van['price']} {van['thumbnail']}")
            page += 1
        return vans
