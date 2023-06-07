import requests
from bs4 import BeautifulSoup, Comment
import csv
from tqdm import tqdm
from fake_useragent import UserAgent
import random
import logging
import warnings
import datetime
import json

last_fetch_time = datetime.datetime.now()

# Remove the NullHandler from the root logger
logging.getLogger().removeHandler(logging.NullHandler())

logging.basicConfig(filename='combine_scrape_debugging_error_log.txt', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s: %(message)s')
logging.captureWarnings(True)
warnings.filterwarnings("ignore", category=UserWarning, module='bs4.dammit', message='.*looks like a.*')


# Function to fetch and parse the list of proxies
def fetch_proxies():
    proxy_url = 'https://www.proxyscan.io/api/proxy?format=json&type=http&ping=800&level=elite&limit=20'
    proxy_response = requests.get(proxy_url)
    data = json.loads(proxy_response.text)
    return [{'http': f"http://{item['Ip']}:{item['Port']}", 'https': f"http://{item['Ip']}:{item['Port']}"} for item in data]


# Fetch the initial list of proxies
proxies = fetch_proxies()

# Create a list of link suffixes to append to the URL
link_suffixes = []
with open('linksuff.txt', 'r') as file:
    for line in file:
        link_suffix = line.strip()
        link_suffixes.append(link_suffix)

# Create progress bar
total_links = len(link_suffixes)
progress_bar = tqdm(total=total_links)

# Create requests session
session = requests.Session()

# Default values
name = 'N/A'
year = 'N/A'
pos = 'N/A'
ht = 'N/A'
wt = 'N/A'
forty = 'N/A'
bench = 'N/A'
broad_jump = 'N/A'
shuttle = 'N/A'
three_cone = 'N/A'
vertical = 'N/A'

# Scrape data from each link with each suffix and enter into a CSV file
for link_suffix in link_suffixes:
    success = False  # Flag to track if data scraping was successful for a link

    while not success and proxies:
        # Check if 2.5 minutes have passed to fetch new proxies
        current_time = datetime.datetime.now()
        time_diff = current_time - last_fetch_time
        if time_diff.total_seconds() > 150:
            proxies = fetch_proxies()
            last_fetch_time = current_time  # Update the time of the last fetch

        # Pick a random proxy
        proxy = random.choice(proxies)

        try:
            # Make a request to the webpage
            # Generate random user agent
            ua = UserAgent()
            session.headers = {'User-Agent': ua.random}

            # Establish connection to the proxy before making the request
            session.proxies = proxy

            url = f"https://pro-football-reference.com{link_suffix}"

            # Make a request to the webpage with a timeout of 30 seconds
            response = session.get(url, timeout=20)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            if soup:
                try:
                    name = soup.find("div", {"id": "meta"}).find_all("div")[1].find("h1").text.strip()
                except IndexError:
                    name = soup.find("div", {"id": "meta"}).find_all("div")[0].find("h1").text.strip()

                if name is not None:
                    content = soup.find('div', {"id": "all_combine"})
                    if content:
                        comments = content.findAll(string=lambda text: isinstance(text, Comment))

                        if comments:
                            # Process each comment
                            for comment in comments:
                                # Parse the comment text as HTML
                                comment_soup = BeautifulSoup(comment, 'html.parser')

                                # Find specific elements within the parsed comment
                                section = comment_soup.find('div', {"id": "div_combine"})

                                if section is not None:
                                    year = int(section.find("tbody").find_all("a")[0].text.strip())
                                    pos = section.find("tbody").find_all("td")[0].text.strip()
                                    ht = section.find("tbody").find_all("td")[1].text.strip()
                                    wt = section.find("tbody").find_all("td")[2].text.strip()
                                    forty = section.find("tbody").find_all("td")[3].text.strip()
                                    bench = section.find("tbody").find_all("td")[4].text.strip()
                                    broad_jump = section.find("tbody").find_all("td")[5].text.strip()
                                    shuttle = section.find("tbody").find_all("td")[6].text.strip()
                                    three_cone = section.find("tbody").find_all("td")[7].text.strip()
                                    vertical = section.find("tbody").find_all("td")[8].text.strip()
                        else:
                            year = 'N/A'
                            pos = 'N/A'
                            ht = 'N/A'
                            wt = 'N/A'
                            forty = 'N/A'
                            bench = 'N/A'
                            broad_jump = 'N/A'
                            shuttle = 'N/A'
                            three_cone = 'N/A'
                            vertical = 'N/A'

                    else:
                        year = 'N/A'
                        pos = 'N/A'
                        ht = 'N/A'
                        wt = 'N/A'
                        forty = 'N/A'
                        bench = 'N/A'
                        broad_jump = 'N/A'
                        shuttle = 'N/A'
                        three_cone = 'N/A'
                        vertical = 'N/A'

                else:
                    name = 'player name not found'
                    year = 'N/A'
                    pos = 'N/A'
                    ht = 'N/A'
                    wt = 'N/A'
                    forty = 'N/A'
                    bench = 'N/A'
                    broad_jump = 'N/A'
                    shuttle = 'N/A'
                    three_cone = 'N/A'
                    vertical = 'N/A'

            else:
                name = 'player page not found'
                year = 'N/A'
                pos = 'N/A'
                ht = 'N/A'
                wt = 'N/A'
                forty = 'N/A'
                bench = 'N/A'
                broad_jump = 'N/A'
                shuttle = 'N/A'
                three_cone = 'N/A'
                vertical = 'N/A'

            # Specify the file name
            filename = 'pfref_combine_a.csv'

            # Write the data to the CSV file
            with open(filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    name,
                    year,
                    pos,
                    ht,
                    wt,
                    forty,
                    bench,
                    broad_jump,
                    shuttle,
                    three_cone,
                    vertical
                ])

            success = True  # Data scraping was successful for the current link

            if success:
                progress_bar.update(1)  # Increment progress bar

        except requests.exceptions.RequestException as e:
            logging.error(e)