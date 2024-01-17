import datetime

import requests
import json

from sqlmodel import Session, select

from app.models.db import engine
from parser.urls import ALL_CATEGORIES, NOMS, QNT
from parser.constants import HEADERS
from app.models.models import Category, Nomenclature, Amount


# парсим данные по существующим категориям
# 1) какие категории существуют

def get_category(skip=0, limit=1):
    with Session(engine) as session:
        category = session.query(Category).offset(skip).limit(limit).first()
        return category
def get_child_info(sub_cat):
    cat_obj = Category(wb_id=sub_cat.get("id"),
                       parent=sub_cat.get("parent"),
                       seo=sub_cat.get("seo"),
                       name=sub_cat.get("name"),
                       url=sub_cat.get("url"),
                       shard=sub_cat.get("shard"),
                       query=sub_cat.get("query"))

    with Session(engine) as session:

        session.add(cat_obj)
        session.commit()

    children = sub_cat.get("childs")

    if children is not None:
        for sub_child in children:
            get_child_info(sub_child)
    else:
        return


def fill_categories():
    response = requests.get(ALL_CATEGORIES,
                            headers=HEADERS,
                            verify=False)
    categories = json.loads(response.text)

    # пройти по всем категориям и возможным подкатегориям
    for category in categories:
        get_child_info(category)

    # Parent
    # id, name, url, shard, query, childs
    # Child
    # id, parent, name, seo, url, shard, query

def fill_first_ten_categories_nomenclature():
    skip = 1
    bad_categories_count = 0
    while skip != 10:
        category = get_category(skip=skip+bad_categories_count, limit=1)
        try:
            # не можем выполнить запрос для самых верхних категорий
            # например первая категория shard=blackhole, cat=306
            fill_nomenclature(shard=category.shard, cat=category.query)
            skip += 1
        except Exception:
            bad_categories_count +=1

def fill_db():
    #fill_categories()
    #fill_first_ten_categories_nomenclature()
    # заполняем товары по первым 10 категориям
    date = datetime.datetime.now()
    skip = 0
    limit = 10
    while skip < 1000:
        with Session(engine) as session:
            query = select(Nomenclature).offset(skip).limit(limit)
            nomenclatures = session.exec(query).all()
            nms_list = [str(nm.id) for nm in nomenclatures]
            nms = ";".join(nms_list)
            fill_amount(nm_ids=nms, date=date)
        skip+=10


def fill_nomenclature(pages=1, shard="sweatshirts_hoodies", cat="cat=8141"):
    page_number = 10
    while page_number <= pages:
        noms_url = NOMS.substitute(shard=shard, cat=cat, page_number=page_number)
        response = requests.get(noms_url,
                                headers=HEADERS,
                                verify=False)
        data = json.loads(response.text).get("data").get("products")

        if not data:
            return

        noms_list = []

        for nom in data:
            nom_obj = Nomenclature(
                id=nom.get("id"),
                category_id=cat[4:],
                root=nom.get("root"),
                brand=nom.get("brand"),
                brandId=nom.get("brandId"),
                siteBrandId=nom.get("siteBrandId"),
                name=nom.get("name"),
                supplier=nom.get("supplier"),
                supplierId=nom.get("supplierId"),
                supplierRating=nom.get("supplierRating"),
                priceU=nom.get("priceU"),
                salePriceU=nom.get("salePriceU"),
                sale=nom.get("sale"),
                logistricsCost=nom.get("logistricsCost"),
                returnCost=nom.get("returnCost"),
                diffPrice=nom.get("diffPrice"),
                pics=nom.get("pics"),
                rating=nom.get("rating"),
                reviewRating=nom.get("reviewRating"),
                feedbacks=nom.get("feedbacks"),
                volume=nom.get("volume")
            )
            noms_list.append(nom_obj)

        with Session(engine) as session:
            session.add_all(noms_list)
            session.commit()

        page_number += 1

def fill_amount(nm_ids, date):
    qnt_url = QNT.substitute(NM=nm_ids)
    response = requests.get(qnt_url,
                            headers=HEADERS,
                            verify=False)
    products = json.loads(response.text).get("data").get("products")
    if not products:
        return

    for product in products:
        nm_id = product.get("id")
        price = product.get("salePriceU")
        sizes = product.get("sizes")
        wh_list = []
        for size in sizes:
            stocks = size.get("stocks")
            name = size.get("name")
            for stock in stocks:
                amount = Amount(nm_id=nm_id,
                                name=name,
                                wh=stock.get("wh"),
                                qty=stock.get("qty"),
                                price=price,
                                date=date)
                wh_list.append(amount)

        with Session(engine) as session:
            session.add_all(wh_list)
            session.commit()

if __name__ == "__main__":
    fill_db()
