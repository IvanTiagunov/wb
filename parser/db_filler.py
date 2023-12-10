import requests
import json

from sqlmodel import Session

from app.models.db import engine
from parser.urls import ALL_CATEGORIES
from parser.constants import HEADERS
from app.models.models import Category

# парсим данные по существующим категориям
# 1) какие категории существуют


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


def fill_db():
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
