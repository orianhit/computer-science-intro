from bs4 import BeautifulSoup
import json
import asyncio
from itertools import islice
import aiohttp

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
}


async def process_line(session, link):
    try:
        resp = await session.get(link, headers=headers)
        content = await resp.text()
        soup = BeautifulSoup(content, "html.parser")
        plant_data = {"name": link.strip().rstrip('/').split('/')[-1]}
        if soup.select_one('.col-sm-6 center img'):
            plant_data['img'] = soup.select_one('.col-sm-6 center img')['src']
        for line in soup.select_one('table.simple-table tbody').find_all('tr'):
            col, val = line.find_all('td')
            plant_data[col.text.rstrip(':').strip().lower()] = val.text.strip().lower()
        return plant_data
    except Exception as ex:
        print(link + ' ---- ' + str(ex))

all_data = []


async def main():
    counter = 0
    with open('plant_data.json', 'a') as writer:
        with open('plant_links.csv', 'r') as reader:
            async with aiohttp.ClientSession() as session:
                for n_lines in iter(lambda: tuple(islice(reader, 1)), ()):
                    counter +=1
                    if counter % 1000 == 0:
                        print(counter)
                    tasks = []
                    for line in n_lines:
                        tasks.append(asyncio.create_task(process_line(session, line)))
                    records = await asyncio.gather(*tasks, return_exceptions=True)
                    for record in records:
                        if record:
                            writer.write(json.dumps(record) + '\n')


if __name__ == '__main__':
    asyncio.run(main())
