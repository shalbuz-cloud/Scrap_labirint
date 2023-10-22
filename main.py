import time
from datetime import datetime
import csv
import platform
import asyncio

from bs4 import BeautifulSoup
import aiohttp

from utils.interface import loading_bar
from config import headers

BASE_URL = "https://www.labirint.ru"
START_TIME = time.time()

books_data = []


async def get_page_data(session: aiohttp.ClientSession, url: str, page: int):
    url += "&page=%i" % page

    async with session.get(url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

        books_items = soup.find(
            'div', class_='genres-carousel__container'
        ).find_all('div', class_='genres-carousel__item')

        for item in books_items:
            item_data: BeautifulSoup = item.find('div', class_='product')

            if item_data is None:
                continue

            try:
                book = item_data.find('div', class_='product-cover')
                title = book.select_one('a.product-title-link > span').text.strip()
                link = book.find('a').get('href')
                author = item_data.select_one('div.product-author > a > span').text.strip()
                publishing = "".join(
                    [
                        t.text for t in
                        item_data.select(
                            'div.product-pubhouse > span,'
                            'div.product-pubhouse > a > span')
                    ]
                ).strip()
                old_price = book.find('span', class_='price-old')
                if old_price is not None:
                    old_price = int(old_price.find('span').text.replace(' ', ''))

                new_price = int(
                    book.find('span', class_='price-val').find('span').text.replace(' ', '')
                )
                discount = 0 if old_price is None else round(
                    (old_price - new_price) / old_price * 100
                )

                books_data.append(
                    {
                        "title": title,
                        "author": author,
                        "publishing": publishing,
                        "old_price": old_price,
                        "discount": discount,
                        "new_price": new_price,
                    }
                )

            except IndexError as iex:
                print('[Error] Index out of range', iex)

        # loading_bar(page, pages_count, 'Progress: ', 1)
        # time.sleep(1)


async def gather_data(url):
    """The function makes a list of tasks."""

    url = "/".join([BASE_URL, "genres/2308/?available=1&paperbooks=1"])

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, headers=headers)
        soup = BeautifulSoup(await response.text(), 'lxml')
        pages_count = int(soup.find('div', class_='pagination-numbers').find_all('a')[-1].text)

        tasks = []

        for page in range(1, pages_count):
            task = asyncio.create_task(get_page_data(session, url, page))
            tasks.append(task)
            loading_bar(page, pages_count, 'Progress: ', 1)

        await asyncio.gather(*tasks)


def main():
    # get_data()

    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')
    file_name = "prices_%s.csv" % cur_time

    url = "/".join([BASE_URL, "genres/2308/?available=1&paperbooks=1"])

    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(gather_data(url))

    loop = asyncio.get_runnig_loop()

    with open(file_name, 'w', encoding='cp1251', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                "Название книги",
                "Автор",
                "Издательство",
                "Старая цена",
                "Процент скидки",
                "Новая цена",
            )
        )
        for book in books_data:
            writer.writerow(
                (
                    book['title'],
                    book['author'],
                    book['publishing'],
                    book["old_price"],
                    book['discount'],
                    book['new_price'],
                )
            )

    finish_time = time.time() - START_TIME
    print('\nThe program was running for %.2f sec.' % finish_time)


if __name__ == '__main__':
    main()
