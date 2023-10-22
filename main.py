import sys
import time
from datetime import datetime
import csv

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.labirint.ru"
START_TIME = time.time()

books_data = []


def loading_bar(count, total, text, size, symbol=1):
    percent = float(count) / float(total) * 100
    symbols = {1: '█', 2: '#', 3: '='}

    sys.stdout.write(
        '\r' + text + str(int(count)).rjust(3, '0') + "/" + str(int(total)).rjust(3, '0') + ' |' +
        symbols[symbol] * int(percent / 10) * size + ' ' * (10 - int(percent / 10)) * size + '|'
    )


def get_data():
    cur_time = datetime.now().strftime('%d-%m-%Y-%H-%M')
    file_name = "prices_%s.csv" % cur_time

    with open(file_name, 'w', encoding='cp1251', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            (
                'Название книги',
                'Автор',
                'Издательство',
                'Старая цена',
                'Процент скидки',
                'Новая цена',
            )
        )

    headers = {
        "Accept": "text / html, application / xhtml + xml, application / "
                  "xml;q = 0.9, image / avif, image / webp, image / apng, "
                  "* / *;q = 0.8, application / signed - exchange;v = b3;q = "
                  "0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/118.0.0.0 Safari/537.36"
    }

    url = "/".join([BASE_URL, "genres/2308/?available=1&paperbooks=1"])

    response = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')

    pages_count = \
        soup.find('div', class_='pagination-numbers').find_all('a')[-1].text

    for page in range(1, int(pages_count) + 1):
        url += "&page=%i" % page
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

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

                with open(file_name, 'a', encoding='cp1251', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        (
                            title,
                            author,
                            publishing,
                            old_price,
                            discount,
                            new_price,
                        )
                    )

            except IndexError as iex:
                print('[Error] Index out of range', iex)

        loading_bar(page, pages_count, 'Progress: ', 1)
        time.sleep(1)


def main():
    get_data()
    finish_time = time.time() - START_TIME
    print('\nThe program was running for %.2f sec.' % finish_time)


if __name__ == '__main__':
    main()
