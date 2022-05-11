"""Beautiful Soup fun
https://www.youtube.com/watch?v=F1kZ39SvuGE
"""

import requests
from bs4 import BeautifulSoup

# get the data
data = requests.get('https://umggaming.com/leaderboards')

# load data into bs4
soup = BeautifulSoup(data.text, "html.parser")
# print(soup)

leaderboard = soup.find("table", {"id": "leaderboard-table"})
# print(leaderboard)
tbody = leaderboard.find("tbody")
# print(tbody)

for tr in tbody.find_all("tr"):
    # print(tr)
    place = tr.find_all("td")[0].text.strip()
    # print(place)
    username = tr.find_all("td")[1].text.strip()
    # or: username = tr.find_all("td")[1].find_all("a")[1].text.strip()
    # print(place, username)
    xp = tr.find_all("td")[4].text.strip()
    print(place, username, xp)
