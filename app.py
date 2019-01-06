import requests
from bs4 import BeautifulSoup
import math
import re


def get_number_of_results(soup):
    result_count_h1 = soup.find("h1", "search-form__count js-results-count")
    result_count_str = result_count_h1.contents[0]
    result_count_str = result_count_str.replace(" motorhomes found", "")
    return math.ceil(int(result_count_str) / 10)


def get_search_page(radius, postcode, berth, max_price, keywords, page):
    url = f"https://www.autotrader.co.uk/motorhome-search?" \
          f"sort=price-asc&" \
          f"radius={radius}&" \
          f"postcode={postcode}&" \
          f"berth={berth}&" \
          f"price-to={max_price}&" \
          f"keywords={keywords}&" \
          f"page={page}"
    result = requests.get(url)
    c = result.content
    soup = BeautifulSoup(c, features="html.parser")
    return soup


def get_van_dict(uid, van_soup):
    response = {"uid": uid}

    image_fig = van_soup.find("figure", "listing-main-image")
    response['thumbnail'] = image_fig.find("img").attrs.get("src")

    info_container = van_soup.find("div", "information-container")
    title_h2 = info_container.find("h2", "listing-title title-wrap")
    response['title'] = title_h2.find("a").contents[0]

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

    if len(extras) > 0:
        print(f"{extras}")

    return response
    pass


vans = []
page = 1
num_pages = 1000

while page <= num_pages:
    soup = get_search_page(1500, "rg315nr", 6, 25000, "bunk", page)
    num_pages = get_number_of_results(soup)
    results_soup = soup.findAll("li", "search-page__result")
    for van_soup in results_soup:
        uid = van_soup.attrs.get('id')
        if uid is not None:
            van = get_van_dict(uid, van_soup)
            vans.append(van)
            # print(f"{van['uid']} {van['title']}")

    page += 1
