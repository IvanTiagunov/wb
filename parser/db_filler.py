import datetime
import time

import requests
import json

import schedule
from sqlalchemy import text
from sqlmodel import Session, select

from app.models.db import engine
from config import PATH_TO_XLSX
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

def fill_first_hundrer_categories_nomenclature():
    skip = 0
    bad_categories_count = 0
    while skip != 100:
        category = get_category(skip=skip+bad_categories_count, limit=1)
        try:
            # не можем выполнить запрос для самых верхних категорий
            # например первая категория shard=blackhole, cat=306
            fill_nomenclature(pages=5, shard=category.shard, cat=category.query)
            skip += 1
        except Exception:
            bad_categories_count +=1


def fill_amount_6000():
    date = datetime.datetime.now()
    skip = 0
    limit = 10
    while skip < 6000:
        with Session(engine) as session:
            query = select(Nomenclature).offset(skip).limit(limit)
            nomenclatures = session.exec(query).all()
            nms_list = [str(nm.id) for nm in nomenclatures]
            nms = ";".join(nms_list)
            fill_amount(nm_ids=nms, date=date)
        skip += 10

def fill_db():
    #fill_categories()
    # заполняем товары по первым 100 категориям
    #fill_first_hundrer_categories_nomenclature()
    fill_amount_6000()


def fill_nomenclature(pages=1, shard="sweatshirts_hoodies", cat="cat=8141"):
    page_number = 1
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
                brand_id=nom.get("brandId"),
                site_brand_id=nom.get("siteBrandId"),
                name=nom.get("name"),
                supplier=nom.get("supplier"),
                supplier_id=nom.get("supplierId"),
                supplier_rating=nom.get("supplierRating"),
                price_u=nom.get("priceU"),
                sale_price_u=nom.get("salePriceU"),
                sale=nom.get("sale"),
                logistrics_cost=nom.get("logistricsCost"),
                return_cost=nom.get("returnCost"),
                diff_price=nom.get("diffPrice"),
                pics=nom.get("pics"),
                rating=nom.get("rating"),
                review_rating=nom.get("reviewRating"),
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


def fill_comissions():
    import pandas as pd
    excel_file_path = PATH_TO_XLSX
    df = pd.read_excel(excel_file_path)
    df.to_sql('commissions', engine, index=False, if_exists='replace')

def get_sales_from_db():
    with Session(engine) as session:
        sql_query = "SELECT SellerCalculations.id, SellerCalculations.articul, SellerCalculations.sells," \
                    " SellerCalculations.cost, SellerCalculations.date, " \
                    "Nomenclature.name FROM SellerCalculations" \
                    " JOIN Nomenclature ON SellerCalculations.articul=Nomenclature.id"
        result = session.execute(text(sql_query)).all()
        return result

def get_db_sales_by_category():
    with Session(engine) as session:
        sql_query = "SELECT sc.articul, sc.sells, sc.cost, nm.name, nm.category_id " \
                    "FROM SellerCalculations as sc " \
                    f"JOIN Nomenclature as nm ON nm.id=sc.articul " \
                    f"WHERE sc.sells > 0 " \
                    f"ORDER BY sc.sells DESC"
        result = session.execute(text(sql_query)).all()
        return result

def get_analitics_by_articul(articul):
    with Session(engine) as session:
        sql_query = "SELECT nm.id, nm.name, nm.category_id, nm.supplier, nm.supplier_rating, nm.sale_price_u," \
                    " nm.rating, nm.review_rating, nm.feedbacks " \
                    "FROM Nomenclature as nm " \
                    f"WHERE nm.id={articul}"
        result = session.execute(text(sql_query)).all()
        return result

def get_noms_list(limit, offset):
    with Session(engine) as session:
        sql_query = f"SELECT id, name FROM Nomenclature LIMIT {limit} OFFSET {offset}"
        result = session.execute(text(sql_query)).all()
        return result
def get_categories_calc_list():
    with Session(engine) as session:
        sql_query = "SELECT DISTINCT category FROM Commissions"
        result = session.execute(text(sql_query)).all()
        return result

def get_subcategories_calc_list(category:str):
    with Session(engine) as session:
        sql_query = "SELECT category, product_name, wb_commission, wb_commission_seller FROM Commissions" \
                    f" WHERE category='{category}'"
        result = session.execute(text(sql_query)).all()
        return result

def start_fill():
    schedule.every().day.at("04:00").do(fill_db)

    # Запуск планировщика
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    fill_db()
    # skip = 0
    # limit = 700000
    # with Session(engine) as session:
    #     query = select(Amount).offset(skip).limit(limit)
    #     result = session.exec(query).all()
    #     print(len(result))
    #fill_comissions()

