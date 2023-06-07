import csv
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tqdm import tqdm
import json
import datetime
import warnings
import logging

last_fetch_time = datetime.datetime.now()

# Remove the NullHandler from the root logger
logging.getLogger().removeHandler(logging.NullHandler())

logging.basicConfig(filename='header_scrape_error_log2.txt', level=logging.ERROR,
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
with open('linksuff_b_fantasy.txt', 'r') as file:
    for line in file:
        link_suffix = line.strip()
        link_suffixes.append(link_suffix)

# Create progress bar
total_links = len(link_suffixes)
progress_bar = tqdm(total=total_links)

# Create requests session
session = requests.Session()

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

            # Make a request to the webpage with a timeout of 10 seconds
            response = session.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for non-200 status codes

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            try:
                head = soup.find("div", {"id": "meta"}).find_all("div")[1]
                name = head.find("h1").text.strip()
                pos = head.find_all("p")[1].text.strip().replace("Position: ", "")

            except IndexError:
                head = soup.find("div", {"id": "meta"}).find_all("div")[0]
                name = head.find("h1").text.strip()
                pos = head.find_all("p")[1].text.strip()

            section = soup.find("div", {"id": "content"})
            table_head = section.find("div", {"id": "all_player_fantasy"}).find("thead")
            head_row_len = len(table_head.find_all("tr")[2].find_all("th"))
            table_body = section.find("div", {"id": "all_player_fantasy"}).find("tbody")
            rows = table_body.find_all("tr")

            for row in rows:
                if head_row_len == 13:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    sc_num_off = row.find_all("td")[3].text.strip()
                    sc_pct_off = row.find_all("td")[4].text.strip()
                    sc_num_def = row.find_all("td")[5].text.strip()
                    sc_pct_def = row.find_all("td")[6].text.strip()
                    sc_num_st = row.find_all("td")[7].text.strip()
                    sc_pct_st = row.find_all("td")[8].text.strip()
                    fantpt = row.find_all("td")[9].text.strip()
                    dkpt = row.find_all("td")[10].text.strip()
                    fdpt = row.find_all("td")[11].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group1.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 17:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_rec_tgt = row.find_all("td")[3].text.strip()
                    in_20_rec_rec = row.find_all("td")[4].text.strip()
                    in_20_rec_yds = row.find_all("td")[5].text.strip()
                    in_20_rec_td = row.find_all("td")[6].text.strip()
                    sc_num_off = row.find_all("td")[7].text.strip()
                    sc_pct_off = row.find_all("td")[8].text.strip()
                    sc_num_def = row.find_all("td")[9].text.strip()
                    sc_pct_def = row.find_all("td")[10].text.strip()
                    sc_num_st = row.find_all("td")[11].text.strip()
                    sc_pct_st = row.find_all("td")[12].text.strip()
                    fantpt = row.find_all("td")[13].text.strip()
                    dkpt = row.find_all("td")[14].text.strip()
                    fdpt = row.find_all("td")[15].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group2.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_rec_tgt,
                            in_20_rec_rec,
                            in_20_rec_yds,
                            in_20_rec_td,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 19:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_rush_att = row.find_all("td")[3].text.strip()
                    in_20_rush_yds = row.find_all("td")[4].text.strip()
                    in_20_rush_td = row.find_all("td")[5].text.strip()
                    in_10_rush_att = row.find_all("td")[6].text.strip()
                    in_10_rush_yds = row.find_all("td")[7].text.strip()
                    in_10_rush_td = row.find_all("td")[8].text.strip()
                    sc_num_off = row.find_all("td")[9].text.strip()
                    sc_pct_off = row.find_all("td")[10].text.strip()
                    sc_num_def = row.find_all("td")[11].text.strip()
                    sc_pct_def = row.find_all("td")[12].text.strip()
                    sc_num_st = row.find_all("td")[13].text.strip()
                    sc_pct_st = row.find_all("td")[14].text.strip()
                    fantpt = row.find_all("td")[15].text.strip()
                    dkpt = row.find_all("td")[16].text.strip()
                    fdpt = row.find_all("td")[17].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group3.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_rush_att,
                            in_20_rush_yds,
                            in_20_rush_td,
                            in_10_rush_att,
                            in_10_rush_yds,
                            in_10_rush_td,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 21:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_passcomp_or_rectgt = row.find_all("td")[3].text.strip()
                    in_20_passatt_or_recrec = row.find_all("td")[4].text.strip()
                    in_20_passyds_or_recyds = row.find_all("td")[5].text.strip()
                    in_20_passtd_or_rectd = row.find_all("td")[6].text.strip()
                    in_10_passcomp_or_rectgt = row.find_all("td")[7].text.strip()
                    in_10_passatt_or_recrec = row.find_all("td")[8].text.strip()
                    in_10_passyds_or_recyds = row.find_all("td")[9].text.strip()
                    in_10_passtd_or_rectd = row.find_all("td")[10].text.strip()
                    sc_num_off = row.find_all("td")[11].text.strip()
                    sc_pct_off = row.find_all("td")[12].text.strip()
                    sc_num_def = row.find_all("td")[13].text.strip()
                    sc_pct_def = row.find_all("td")[14].text.strip()
                    sc_num_st = row.find_all("td")[15].text.strip()
                    sc_pct_st = row.find_all("td")[16].text.strip()
                    fantpt = row.find_all("td")[17].text.strip()
                    dkpt = row.find_all("td")[18].text.strip()
                    fdpt = row.find_all("td")[19].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group4.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_passcomp_or_rectgt,
                            in_20_passatt_or_recrec,
                            in_20_passyds_or_recyds,
                            in_20_passtd_or_rectd,
                            in_10_passcomp_or_rectgt,
                            in_10_passatt_or_recrec,
                            in_10_passyds_or_recyds,
                            in_10_passtd_or_rectd,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 23:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_rush_att = row.find_all("td")[3].text.strip()
                    in_20_rush_yds = row.find_all("td")[4].text.strip()
                    in_20_rush_td = row.find_all("td")[5].text.strip()
                    in_20_rec_tgt = row.find_all("td")[6].text.strip()
                    in_20_rec_rec = row.find_all("td")[7].text.strip()
                    in_20_rec_yds = row.find_all("td")[8].text.strip()
                    in_20_rec_td = row.find_all("td")[9].text.strip()
                    in_10_rush_att = row.find_all("td")[10].text.strip()
                    in_10_rush_yds = row.find_all("td")[11].text.strip()
                    in_10_rush_td = row.find_all("td")[12].text.strip()
                    sc_num_off = row.find_all("td")[13].text.strip()
                    sc_pct_off = row.find_all("td")[14].text.strip()
                    sc_num_def = row.find_all("td")[15].text.strip()
                    sc_pct_def = row.find_all("td")[16].text.strip()
                    sc_num_st = row.find_all("td")[17].text.strip()
                    sc_pct_st = row.find_all("td")[18].text.strip()
                    fantpt = row.find_all("td")[19].text.strip()
                    dkpt = row.find_all("td")[20].text.strip()
                    fdpt = row.find_all("td")[21].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group5.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_rush_att,
                            in_20_rush_yds,
                            in_20_rush_td,
                            in_20_rec_tgt,
                            in_20_rec_rec,
                            in_20_rec_yds,
                            in_20_rec_td,
                            in_10_rush_att,
                            in_10_rush_yds,
                            in_10_rush_td,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 27:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_passcmp_or_rushatt = row.find_all("td")[3].text.strip()
                    in_20_passatt_or_rushyds = row.find_all("td")[4].text.strip()
                    in_20_passyds_or_rushtd = row.find_all("td")[5].text.strip()
                    in_20_passtd_or_rectgt = row.find_all("td")[6].text.strip()
                    in_20_rushatt_or_recrec = row.find_all("td")[7].text.strip()
                    in_20_rushyds_or_recyds = row.find_all("td")[8].text.strip()
                    in_20_rushtd_or_rectd = row.find_all("td")[9].text.strip()
                    in_10_passcmp_or_rushatt = row.find_all("td")[10].text.strip()
                    in_10_passatt_or_rushyds = row.find_all("td")[11].text.strip()
                    in_10_passyds_or_rushtd = row.find_all("td")[12].text.strip()
                    in_10_passtd_or_rectgt = row.find_all("td")[13].text.strip()
                    in_10_rushatt_or_recrec = row.find_all("td")[14].text.strip()
                    in_10_rushyds_or_recyds = row.find_all("td")[15].text.strip()
                    in_10_rushtd_or_rectd = row.find_all("td")[16].text.strip()
                    sc_num_off = row.find_all("td")[17].text.strip()
                    sc_pct_off = row.find_all("td")[18].text.strip()
                    sc_num_def = row.find_all("td")[19].text.strip()
                    sc_pct_def = row.find_all("td")[20].text.strip()
                    sc_num_st = row.find_all("td")[21].text.strip()
                    sc_pct_st = row.find_all("td")[22].text.strip()
                    fantpt = row.find_all("td")[23].text.strip()
                    dkpt = row.find_all("td")[24].text.strip()
                    fdpt = row.find_all("td")[25].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group6.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_passcmp_or_rushatt,
                            in_20_passatt_or_rushyds,
                            in_20_passyds_or_rushtd,
                            in_20_passtd_or_rectgt,
                            in_20_rushatt_or_recrec,
                            in_20_rushyds_or_recyds,
                            in_20_rushtd_or_rectd,
                            in_10_passcmp_or_rushatt,
                            in_10_passatt_or_rushyds,
                            in_10_passyds_or_rushtd,
                            in_10_passtd_or_rectgt,
                            in_10_rushatt_or_recrec,
                            in_10_rushyds_or_recyds,
                            in_10_rushtd_or_rectd,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 29:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_pass_cmp = row.find_all("td")[3].text.strip()
                    in_20_pass_att = row.find_all("td")[4].text.strip()
                    in_20_pass_yds = row.find_all("td")[5].text.strip()
                    in_20_pass_td = row.find_all("td")[6].text.strip()
                    in_20_rec_tgt = row.find_all("td")[7].text.strip()
                    in_20_rec_rec = row.find_all("td")[8].text.strip()
                    in_20_rec_yds = row.find_all("td")[9].text.strip()
                    in_20_rec_td = row.find_all("td")[10].text.strip()
                    in_10_pass_cmp = row.find_all("td")[11].text.strip()
                    in_10_pass_att = row.find_all("td")[12].text.strip()
                    in_10_pass_yds = row.find_all("td")[13].text.strip()
                    in_10_pass_td = row.find_all("td")[14].text.strip()
                    in_10_rec_tgt = row.find_all("td")[15].text.strip()
                    in_10_rec_rec = row.find_all("td")[16].text.strip()
                    in_10_rec_yds = row.find_all("td")[17].text.strip()
                    in_10_rec_td = row.find_all("td")[18].text.strip()
                    sc_num_off = row.find_all("td")[19].text.strip()
                    sc_pct_off = row.find_all("td")[20].text.strip()
                    sc_num_def = row.find_all("td")[21].text.strip()
                    sc_pct_def = row.find_all("td")[22].text.strip()
                    sc_num_st = row.find_all("td")[23].text.strip()
                    sc_pct_st = row.find_all("td")[24].text.strip()
                    fantpt = row.find_all("td")[25].text.strip()
                    dkpt = row.find_all("td")[26].text.strip()
                    fdpt = row.find_all("td")[27].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group7.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_pass_cmp,
                            in_20_pass_att,
                            in_20_pass_yds,
                            in_20_pass_td,
                            in_20_rec_tgt,
                            in_20_rec_rec,
                            in_20_rec_yds,
                            in_20_rec_td,
                            in_10_pass_cmp,
                            in_10_pass_att,
                            in_10_pass_yds,
                            in_10_pass_td,
                            in_10_rec_tgt,
                            in_10_rec_rec,
                            in_10_rec_yds,
                            in_10_rec_td,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 31:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_pass_cmp = row.find_all("td")[3].text.strip()
                    in_20_pass_att = row.find_all("td")[4].text.strip()
                    in_20_pass_yds = row.find_all("td")[5].text.strip()
                    in_20_pass_td = row.find_all("td")[6].text.strip()
                    in_20_rush_att = row.find_all("td")[7].text.strip()
                    in_20_rush_yds = row.find_all("td")[8].text.strip()
                    in_20_rush_td = row.find_all("td")[9].text.strip()
                    in_20_rec_tgt = row.find_all("td")[10].text.strip()
                    in_20_rec_rec = row.find_all("td")[11].text.strip()
                    in_20_rec_yds = row.find_all("td")[12].text.strip()
                    in_20_rec_td = row.find_all("td")[13].text.strip()
                    in_10_pass_cmp = row.find_all("td")[14].text.strip()
                    in_10_pass_att = row.find_all("td")[15].text.strip()
                    in_10_pass_yds = row.find_all("td")[16].text.strip()
                    in_10_pass_td = row.find_all("td")[17].text.strip()
                    in_10_rush_att = row.find_all("td")[18].text.strip()
                    in_10_rush_yds = row.find_all("td")[19].text.strip()
                    in_10_rush_td = row.find_all("td")[20].text.strip()
                    sc_num_off = row.find_all("td")[21].text.strip()
                    sc_pct_off = row.find_all("td")[22].text.strip()
                    sc_num_def = row.find_all("td")[23].text.strip()
                    sc_pct_def = row.find_all("td")[24].text.strip()
                    sc_num_st = row.find_all("td")[25].text.strip()
                    sc_pct_st = row.find_all("td")[26].text.strip()
                    fantpt = row.find_all("td")[27].text.strip()
                    dkpt = row.find_all("td")[28].text.strip()
                    fdpt = row.find_all("td")[29].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group8.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_pass_cmp,
                            in_20_pass_att,
                            in_20_pass_yds,
                            in_20_pass_td,
                            in_20_rush_att,
                            in_20_rush_yds,
                            in_20_rush_td,
                            in_20_rec_tgt,
                            in_20_rec_rec,
                            in_20_rec_yds,
                            in_20_rec_td,
                            in_10_pass_cmp,
                            in_10_pass_att,
                            in_10_pass_yds,
                            in_10_pass_td,
                            in_10_rush_att,
                            in_10_rush_yds,
                            in_10_rush_td,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                elif head_row_len == 35:
                    year = row.find_all("td")[0].text.strip()
                    team = row.find_all("td")[1].text.strip()
                    games = row.find_all("td")[2].text.strip()
                    in_20_pass_cmp = row.find_all("td")[3].text.strip()
                    in_20_pass_att = row.find_all("td")[4].text.strip()
                    in_20_pass_yds = row.find_all("td")[5].text.strip()
                    in_20_pass_td = row.find_all("td")[6].text.strip()
                    in_20_rush_att = row.find_all("td")[7].text.strip()
                    in_20_rush_yds = row.find_all("td")[8].text.strip()
                    in_20_rush_td = row.find_all("td")[9].text.strip()
                    in_20_rec_tgt = row.find_all("td")[10].text.strip()
                    in_20_rec_rec = row.find_all("td")[11].text.strip()
                    in_20_rec_yds = row.find_all("td")[12].text.strip()
                    in_20_rec_td = row.find_all("td")[13].text.strip()
                    in_10_pass_cmp = row.find_all("td")[14].text.strip()
                    in_10_pass_att = row.find_all("td")[15].text.strip()
                    in_10_pass_yds = row.find_all("td")[16].text.strip()
                    in_10_pass_td = row.find_all("td")[17].text.strip()
                    in_10_rush_att = row.find_all("td")[18].text.strip()
                    in_10_rush_yds = row.find_all("td")[19].text.strip()
                    in_10_rush_td = row.find_all("td")[20].text.strip()
                    in_10_rec_tgt = row.find_all("td")[21].text.strip()
                    in_10_rec_rec = row.find_all("td")[22].text.strip()
                    in_10_rec_yds = row.find_all("td")[23].text.strip()
                    in_10_rec_td = row.find_all("td")[24].text.strip()
                    sc_num_off = row.find_all("td")[25].text.strip()
                    sc_pct_off = row.find_all("td")[26].text.strip()
                    sc_num_def = row.find_all("td")[27].text.strip()
                    sc_pct_def = row.find_all("td")[28].text.strip()
                    sc_num_st = row.find_all("td")[29].text.strip()
                    sc_pct_st = row.find_all("td")[30].text.strip()
                    fantpt = row.find_all("td")[31].text.strip()
                    dkpt = row.find_all("td")[32].text.strip()
                    fdpt = row.find_all("td")[33].text.strip()

                    # Specify the file name
                    filename = 'fantasy_group9.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name,
                            year,
                            team,
                            games,
                            in_20_pass_cmp,
                            in_20_pass_att,
                            in_20_pass_yds,
                            in_20_pass_td,
                            in_20_rush_att,
                            in_20_rush_yds,
                            in_20_rush_td,
                            in_20_rec_tgt,
                            in_20_rec_rec,
                            in_20_rec_yds,
                            in_20_rec_td,
                            in_10_pass_cmp,
                            in_10_pass_att,
                            in_10_pass_yds,
                            in_10_pass_td,
                            in_10_rush_att,
                            in_10_rush_yds,
                            in_10_rush_td,
                            in_10_rec_tgt,
                            in_10_rec_rec,
                            in_10_rec_yds,
                            in_10_rec_td,
                            sc_num_off,
                            sc_pct_off,
                            sc_num_def,
                            sc_pct_def,
                            sc_num_st,
                            sc_pct_st,
                            fantpt,
                            dkpt,
                            fdpt
                        ])

                else:
                    # Specify the file name
                    filename = 'fantasy_group10.csv'

                    # Write the data to the CSV file
                    with open(filename, 'a', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([
                            name
                        ])

            success = True  # Data scraping was successful for the current link

            if success:
                progress_bar.update(1)  # Increment progress bar

        except requests.exceptions.RequestException as e:
            logging.error(e)
