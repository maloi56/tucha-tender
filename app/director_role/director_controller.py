import mimetypes
import re
from functools import wraps
from app.util import dbase
import tempfile
import os
import io
import zipfile
import magic
import requests
from bs4 import BeautifulSoup
from flask import render_template, url_for, redirect, request, flash, abort, send_file
from flask_login import current_user
from app.director_role.forms import DirectorDocsForm, DirectorStatusForm

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


def role_required(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        if request.endpoint.split('.')[0] != current_user.get_role():
            abort(403)
        return route_func(*args, **kwargs)

    return wrapper


def check_role():
    return True if current_user.get_role() == 'director' else False


def get_reasonability(rate):
    if rate >= 100:
        return "участие необходимо"
    elif rate >= 80:
        return "участие целесообразно"
    elif rate >= 70:
        return "участие рискованно"
    else:
        return "участие нецелесообразно"


def get_self_price(hr, instruments, materials):
    try:
        return hr.Rating.costprice + instruments.Rating.costprice + materials.Rating.costprice
    except Exception as err:
        raise err


def get_sppr_info(self_price, hr, instruments, materials, tender):
    try:
        if (self_price != 0 and hr.Rating.rate != 0 and instruments.Rating.rate != 0 and materials.Rating.rate != 0):
            average_rate = (hr.Rating.rate + instruments.Rating.rate + materials.Rating.rate) / 3
            reasonability = int((average_rate / 10) * (tender.price / (self_price + 1)) * 100)
            support_decision = get_reasonability(reasonability)
            return average_rate, str(reasonability) + '%', support_decision
        else:
            return 'Не все отделы выставили оценки!', 'Не все отделы выставили оценки!', 'Не все отделы выставили оценки!'
    except:
        return 0, 0, 0


def set_status():
    form = DirectorStatusForm()
    if form.validate_on_submit():
        dbase.set_status(request.form['tender_id'], form.status.data)
    return redirect(url_for('.selected'))


def selected():
    if check_role():
        selected_items = dbase.get_selected('отбор')
        return render_template('director/selected.html', selected_items=selected_items, title="Выбранные заявки",
                               menu=current_user.get_menu() if current_user.is_authenticated else [])
    else:
        flash('Нет доступа')
        redirect(url_for(".index"))


def index():
    # dbase.init_db()
    return render_template('director/index.html', title="Интеллектуальная поддержка отбора заявок на сайте закупок",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])


def download_docs():
    # Передавать список доступных документов и мб загрузку по одному отдельному
    form = DirectorDocsForm()
    id = form.doc_href.data
    if id[0] == "0" and len(id) > 11:
        url = f"https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber={id}"
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        blocks = soup.find("div", class_="blockFilesTabDocs").find_all("span", {"class": "section__value"})
        type = "44"
    else:
        url = f"https://zakupki.gov.ru/epz/order/notice/notice223/documents.html?noticeInfoId={id}"
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")
        pre_blocks = soup.find_all("div", class_="attachment__value")
        blocks = pre_blocks[3].find_all("span", class_="count")
        type = "223"
        # print(blocks[1].find_all("span", {"class": "count "}))

    # создаем временную папку для сохранения файлов
    tempdir = tempfile.mkdtemp()

    # скачиваем файлы и сохраняем их в временной папке
    for block in blocks:
        href = block.find_all("a")
        url = href[0].get("href") if type == "44" else "https://zakupki.gov.ru" + href[1].get("href")
        text = href[0].text if type == "44" else href[1].text
        clean_text = re.sub(r'[^\w\s]', '', text).strip()

        mime = magic.Magic(mime=True)

        r = requests.get(url, headers=headers)
        content_type = mime.from_buffer(r.content)
        ext = mimetypes.guess_extension(content_type)
        f_name = clean_text + ext if ext else clean_text + ".pdf"
        filename = os.path.join(tempdir, f_name)
        with open(filename, 'wb') as f:
            f.write(r.content)

    # создаем zip-архив с содержимым временной папки
    zip_filename = f'Заявка - {id}.zip'
    temp_buffer = io.BytesIO()
    with zipfile.ZipFile(temp_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, _, filenames in os.walk(tempdir):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                zipf.write(filepath, arcname=os.path.relpath(filepath, tempdir))

    temp_buffer.seek(0)  # Перемещаем указатель буфера в начало

    return send_file(
        temp_buffer,
        as_attachment=True,
        download_name=zip_filename,
        mimetype='application/zip',
    )


def tender(id):
    tender = dbase.get_tender(id)
    if not tender or not check_role():
        abort(404)
    doc_form = DirectorDocsForm()
    doc_form.doc_href.data = tender.id

    status_form = DirectorStatusForm()
    status_form.doc_href.data = tender.id

    hr_info = dbase.get_tender_rate(id, 'hr')
    instruments_info = dbase.get_tender_rate(id, 'instruments')
    materials_info = dbase.get_tender_rate(id, 'materials')

    self_price = get_self_price(hr_info, instruments_info, materials_info)
    average_rate, reasonability, support_decision = get_sppr_info(self_price, hr_info, instruments_info,
                                                                  materials_info, tender)

    return render_template('director/tender.html', tender=tender,
                           self_price=self_price,
                           doc_form=doc_form,
                           status_form=status_form,
                           support_decision=support_decision,
                           reasonability=reasonability,
                           average_rate=average_rate,
                           hr_info=hr_info,
                           instruments_info=instruments_info,
                           materials_info=materials_info,
                           title=f"Тендерная заявка номер: {id}",
                           menu=current_user.get_menu() if current_user.is_authenticated else [])
