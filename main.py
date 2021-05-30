from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
}

START_SEARCH_URL = 'https://garden.org/plants/group/'
BASE_URL = 'https://garden.org/'

PLANT_LINKS_FILE = 'plant_links.csv'

if __name__ == '__main__':
    with open(PLANT_LINKS_FILE, 'a') as links_file:
        soup = BeautifulSoup(requests.get(START_SEARCH_URL, headers=headers).content, "html.parser")
        should_start = False
        for td in soup.find_all("td", {"data-th": "Database name"}):
            if td.find('a'):
                db_link = td.find('a')['href']
            # if 'abelias' in db_link:
            if 'crepe-myrtles' in db_link:
                should_start = True
            if should_start:
                print(db_link)
                soup = BeautifulSoup(requests.get(urljoin(BASE_URL, db_link), headers=headers).content, "html.parser")
                all_db_opt = soup.select_one('.col-sm-7').find_all('a')
                all_db = [all_db['href'] for all_db in all_db_opt if 'Browse the full' in all_db.text][0]
                offset = 0
                while True:
                    group_plant_link = urljoin(BASE_URL, all_db) + f"?offset={str(offset)}"
                    table = BeautifulSoup(requests.get(group_plant_link, headers=headers).content, "html.parser")
                    if table.find('table'):
                        for plant_link in table.find('table').find_all('td', {"width":"110"}):
                            links_file.write(f"{urljoin(BASE_URL, plant_link.find('a')['href'])}\n")
                        offset += 20
                    else:
                        break
