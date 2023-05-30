import re
import asyncio
import aiohttp
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup
import pymorphy3
from fuzzywuzzy import fuzz
from flask import g
from FDataBase import FDataBase
from apscheduler.schedulers.background import BackgroundScheduler
from util.mail_sender import Mail

morph = pymorphy3.MorphAnalyzer()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

DATABASE = 'database.db'
dbase = None
baseStopWords = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т",
                 "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я", "ст"]
res = {}


def get_db():
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db


def get_database():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = get_db()
    return g.link_db


def create_temp_bd():  # Delete soon
    return FDataBase(get_db())


def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_database()
    dbase = FDataBase(db)


def close_db(request):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()


def get_filter_words(dbase):
    rules = dbase.get_filter_words()
    words = []
    for rule in rules:
        words += rule['word'].split()
    return set(words)


def get_ban_words(dbase):
    rules = dbase.get_ban_words()
    words = []
    for rule in rules:
        words += rule['word'].split()
    return set(words)


async def get_page_data(session, page, stopWords, filter, priceFrom, priceTo, formatted_date):
    url = f"https://zakupki.gov.ru/epz/order/extendedsearch/results.html?morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber={page}&sortDirection=false&recordsPerPage=_50&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&fz223=on&ppRf615=on&af=on&priceFromGeneral={priceFrom}&priceToGeneral={priceTo}&currencyIdGeneral=-1&applSubmissionCloseDateTo={formatted_date}&customerPlace=5277327%2C5277335&customerPlaceCodes=50000000000%2C77000000000&OrderPlacementSmallBusinessSubject=on&OrderPlacementRnpData=on&OrderPlacementExecutionRequirement=on&orderPlacement94_0=0&orderPlacement94_1=0&orderPlacement94_2=0"
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, "lxml")
        container = soup.find("div", class_="col-9")
        if container is not None:
            card_items = container.find_all("div", {"class": "registry-entry__form"})
        else:
            card_items = []
        for ci in card_items:
            flag = False
            card_data = ci.find_all("div", {"class": "registry-entry__body-value"})
            right_block = ci.find_all("div", {"class": "registry-entry__right-block"})
            if len(right_block) != 0:
                price = right_block[0].find("div", {"class": "price-block__value"})
                block = ci.find("div", {"class": "data-block__title"}, text="Окончание подачи заявок")
                if block:
                    date_value = block.find_next_sibling("div", {"class": "data-block__value"}).text
                else:
                    print("No date found")
                price_value = 0 if price is None else int(re.sub(r'\D', '', price.text.strip())) / 100
            href = ci.find_all("a")
            if len(card_data) != 0:
                text = card_data[0].text.lower()
                t = re.sub(r"[^\w\s]", "", text)
                words = t.split()
                normalized_text = " ".join([morph.parse(word)[0].normal_form for word in words]).split()
                for word in stopWords:
                    if word in normalized_text:
                        flag = True
                        break
                if flag == False:
                    id = str(re.sub(r'\D', '', href[2].text))
                    flag_1 = False
                    text_1 = re.sub(r"[^\w\s]", "", card_data[0].text)
                    baseFiltered = [word for word in text_1.split() if word not in baseStopWords]
                    for word in baseFiltered:
                        for fil_word in filter:
                            a = fuzz.partial_ratio(fil_word, word)
                            if a == 100:
                                if datetime.strptime(date_value, '%d.%m.%Y') >= datetime.today():
                                    res[str(id)] = {
                                        "id": id,
                                        "title": card_data[0].text,
                                        "price": price_value,
                                        "date": date_value,
                                        "href": href[2].get("href")
                                    }
                                    print(fil_word + " " + word)
                                    print(res[id])
                                    flag_1 = True
                                    break
                        if flag_1:
                            break
                else:
                    print("В бан - " + card_data[0].text)
    print(f"[INFO] Обработал страницу {page}")


async def gather_data(db):
    async with aiohttp.ClientSession() as session:
        tasks = []
        optRules = db.get_optional_rules()
        if len(optRules) != 0:
            date = optRules[0]['date']
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d.%m.%Y')
            priceFrom = optRules[0]['priceFrom']
            priceTo = optRules[0]['priceTo']
        else:
            formatted_date = str(datetime.today().strftime("%d-%m-%Y"))
            priceFrom = 0
            priceTo = 100000
        filter = get_filter_words(db)
        stopWords = get_ban_words(db)
        for page in range(1, 10):
            task = asyncio.create_task(
                get_page_data(session, page, stopWords, filter, priceFrom, priceTo, formatted_date))
            tasks.append(task)

        await asyncio.gather(*tasks)


def find_new_tenders(dbase):
    try:
        mail = Mail('tendertestingg@gmail.com', 'uhtvsfqnhylrmclc')
        current_tenders_count = int(dbase.get_considered_count('отбор'))
        asyncio.run(gather_data(dbase))
        dbase.insert_tenders(res)
        tenders_count = len(res) - current_tenders_count
        if tenders_count != 0 and scheduler.running:
            msg = f'Найдено {tenders_count} новых заявок'
            mail.send_email("Поиск тендеров", 'beztfake@yandex.ru', msg)
        return True
    except Exception as e:
        print(e)
        return False


temp_db = create_temp_bd()
scheduler = BackgroundScheduler()
scheduler.add_job(find_new_tenders, 'interval', hours=24, args=[temp_db])  # Запуск каждые 24 часа


def start_scheduler():
    scheduler.start()
