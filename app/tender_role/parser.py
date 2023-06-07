import re
import asyncio
import aiohttp
from app.util import dbase
from datetime import datetime
from bs4 import BeautifulSoup
import pymorphy3
from fuzzywuzzy import fuzz
# from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
from app.util.mail_sender import Mail
from app.model import Selected

morph = pymorphy3.MorphAnalyzer()

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

baseStopWords = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т",
                 "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я", "ст"]
res = {}


def get_filter_words():
    rules = dbase.get_filter_words()
    words = []
    for rule in rules:
        words += rule.word.split()
    return set(words)


def get_ban_words():
    rules = dbase.get_ban_words()
    words = []
    for rule in rules:
        words += rule.word.split()
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
                                        "date": datetime.strptime(date_value, '%d.%m.%Y'),
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


async def gather_data():
    async with aiohttp.ClientSession() as session:
        tasks = []
        optRules = dbase.get_optional_rules()
        if len(optRules) != 0:
            date = optRules[0].date
            formatted_date = date.strftime('%d.%m.%Y')
            priceFrom = optRules[0].priceFrom
            priceTo = optRules[0].priceTo
        else:
            formatted_date = str(datetime.today().strftime("%d-%m-%Y"))
            priceFrom = 0
            priceTo = 100000
        filter = get_filter_words()
        stopWords = get_ban_words()
        for page in range(1, 10):
            task = asyncio.create_task(
                get_page_data(session, page, stopWords, filter, priceFrom, priceTo, formatted_date))
            tasks.append(task)

        await asyncio.gather(*tasks)


def find_new_tenders():  # надо будет подумать над логикой подсчета новых заявок. можно, чтобы функция инсерта возвращала кол-во переделать с использованием множеств
    try:
        mail = Mail('Kolesnikovaksenia2001@gmail.com', 'kusvcxkhioiffbgi')
        tenders_count = 0
        asyncio.run(gather_data())
        for key, value in res.items():
            if Selected.query.get(key) is None:
                tenders_count += 1
        dbase.insert_tenders(res)
        if tenders_count > 0 and scheduler.running:
            msg = f'Найдено {tenders_count} новых заявок'
            mail.send_email("Поиск тендеров", 'Kolesnikovaksenia2001@gmail.com', msg)
        return True
    except Exception as e:
        raise e
        return False


scheduler = APScheduler()


# scheduler.add_job(find_new_tenders, 'interval', minutes=1)  # Запуск каждые 24 часа


def start_scheduler():
    @scheduler.task('interval', id='do_job_1', hours=24, misfire_grace_time=900)
    def job1():
        with scheduler.app.app_context():
            find_new_tenders()

    scheduler.start()
