import requests
from bs4 import BeautifulSoup
from itertools import cycle
import re
import csv
import random
from collections import OrderedDict

# Create a list of http headers
headers_list = [
    #headers list omitted
]

# Create ordered dict from Headers above
ordered_headers_list = []
for headers in headers_list:
    h = OrderedDict()
    for header, value in headers.items():
        h[header] = value
    ordered_headers_list.append(h)

# Create requests session
session = requests.Session()

# Create list of proxies to cycle
list_proxy = [
    #proxies list omitted
]

proxy_cycle = cycle(list_proxy)

# Create a list to track proxies that encounter errors
error_proxies = []


def clean(html_block):
    # Convert 'Tag' object to a string representation
    html_string = str(html_block)
    # Remove line breaks
    html_string = re.sub('\n', '', html_string)
    # Remove multiple whitespace characters
    html_string = re.sub('\s+', ' ', html_string)
    # Remove leading and trailing whitespace
    html_string = html_string.strip()

    pattern = r'data-birth="([^"]*)"'
    matches = re.search(pattern, html_string)
    if matches:
        date_of_birth = matches.group(1)
        return date_of_birth


# Create a list of link suffixes to append to the URL
link_suffixes = []
with open('linksuff_extra.txt', 'r') as file:
    for line in file:
        link_suffix = line.strip()
        link_suffixes.append(link_suffix)

# Scrape data from each link with each suffix and enter into a CSV file
for link_suffix in link_suffixes:
    success = False  # Flag to track if data scraping was successful for a link

    while not success and len(list_proxy) > 0:
        # Pick the next proxy from the cycle
        proxy = next(proxy_cycle)
        proxies = {
            "http": proxy,
            "https": proxy
        }

        try:
            # Make a request to the webpage
            # Establish connection to the proxy before making the request
            session.proxies = proxies

            # Pick a random browser header for each request
            headers = random.choice(headers_list)

            url = f"https://pro-football-reference.com{link_suffix}"

            # Make a request to the webpage with a timeout of 30 seconds
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find the data
            full_info = soup.find("div", {"id": "info"})

            # Scrape the variables of interest
            name = full_info.find_all("p")[0].text.strip()
            position = full_info.find_all("p")[1].text.strip()
            ht_wt = full_info.find_all("p")[2].text.strip()
            try:
                team = full_info.find_all("p")[3].find("span").text.strip()
            except AttributeError:
                team = None
            dob = clean(full_info.find_all("p")[4])
            college = full_info.find_all("p")[5].find("a").text.strip()

            # Write row of variables to csv file
            with open('pfref_data.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([name, position, ht_wt, team, dob, college])

            success = True  # Data scraping was successful for the current link

        except requests.RequestException as e:
            print(f"Error occurred for proxy {proxy}: {str(e)}")
            error_proxies.append(proxy)
            list_proxy.remove(proxy)

    if not success:
        print(f"Skipping link {link_suffix} due to proxy errors.")

    # Rotate to the next proxy after attempting to scrape data for a link
    proxy = next(proxy_cycle)