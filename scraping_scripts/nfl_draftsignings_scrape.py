import requests
from bs4 import BeautifulSoup
import csv

# Define the headers list
column_headers = ["Pick_Number", "Team", "Player", "Position", "College"]

# Create a new CSV file
filename = "../data_files/new_player_info.csv"
with open(filename, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(column_headers)

# Use a session object for HTTP requests
session = requests.Session()
session.headers = {
    #header omitted
}

# Scrape player names for the target year
url = "https://www.footballdb.com/transactions/draft-signings.html"

response = session.get(url)

soup = BeautifulSoup(response.content, "html.parser")

while True:
    # Find the next table on the page
    table = soup.find("table").find("tbody")

    if not table:
        # No more tables found, break the loop
        break

    rows = table.find_all("tr")

    # Process each row
    for row in rows:
        cells = row.find_all("td")

        # Extract data
        Pick_Number = cells[0].text.strip()
        Team = cells[1].find("span", {"class": "hidden-xs"}).text.strip()
        Player = cells[2].text.strip()
        Position = cells[3].text.strip()
        College = cells[4].text.strip()

        # Append each row to the CSV file
        with open(filename, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([Pick_Number, Team, Player, Position, College])

    # Remove the current table from the soup
    table.decompose()


# This would only ever scrape the first round, so I just copy-pasted the table from the webpage into an excel csv file, which (luckily) worked.
