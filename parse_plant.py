from bs4 import BeautifulSoup
import json
import asyncio
from itertools import islice
import aiohttp

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
}


async def process_line(session, link):
    resp = await session.get(link, headers=headers)
    content = await resp.text()
    soup = BeautifulSoup(content, "html.parser")
    plant_data = {"name": link.rstrip('/').split('/')[-1]}
    for line in soup.find('tbody').find_all('tr'):
        col, val = line.find_all('td')
        plant_data[col.text.rstrip(':').strip().lower()] = val.text.strip().lower()
    return plant_data


all_data = []


async def main():
    with open('plant_data.json', 'a') as writer:
        with open('plant_links.csv', 'r') as reader:
            async with aiohttp.ClientSession() as session:
                for n_lines in iter(lambda: tuple(islice(reader, 10)), ()):
                    tasks = []
                    for line in n_lines:
                        tasks.append(asyncio.create_task(process_line(session, line)))
                    records = await asyncio.gather(*tasks, return_exceptions=True)
                    for record in records:
                        writer.write(json.dumps(record) + '\n')


if __name__ == '__main__':
    asyncio.run(main())
