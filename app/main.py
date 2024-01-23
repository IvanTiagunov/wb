import os
import sys
import threading
from datetime import datetime
from typing import List, Optional

import psycopg2
from fastapi import FastAPI, Depends, HTTPException
from fastapi.logger import logger
from pydantic import BaseModel, BaseSettings
from sqlmodel import select
from sqlmodel import Session
from parser.db_filler import fill_db, get_sales_from_db, start_fill, get_categories_calc_list, \
    get_subcategories_calc_list, get_db_sales_by_category, get_analitics_by_articul, get_noms_list
from seller_calc.calc import start_calc
from app.models.db import init_db, get_session
from app.models.models import Category, Commissions
from fastapi.middleware.cors import CORSMiddleware


# from seller_calc.calc import calculations
# from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
# from sqlalchemy.sql import text
# from fastapi.responses import Response


class Settings(BaseSettings):
    # ... The rest of our FastAPI settings

    BASE_URL = "http://localhost:8000"
    USE_NGROK = True


settings = Settings()


def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass


def start_up():
    # init_db()
    # fill_db()
    pass
    fill_thread = threading.Thread(target=start_fill)
    fill_thread.start()
    calc_thread = threading.Thread(target=start_calc)
    calc_thread.start()


app = FastAPI(on_startup=start_up())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.USE_NGROK:
    # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
    from pyngrok import ngrok

    # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
    # when starting the server
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "8000"

    # Open a ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url
    logger.info("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

    # Update any base URLs or webhooks to use the public ngrok URL
    settings.BASE_URL = public_url
    init_webhooks(public_url)


class CategoryResponse(BaseModel):
    name: str
    url: str
    wb_id: int


@app.get("/all_categories", response_model=list[CategoryResponse])
def get_categories_table(session: Session = Depends(get_session)):
    result = session.execute(select(Category))
    categories = result.scalars().all()
    return [CategoryResponse(name=cat.name, url=cat.url, wb_id=cat.wb_id) for cat in categories]


# @app.get("/commissions")
# def get_commission(product_name: str, session: Session = Depends(get_session)):
#     try:
#         return session.query(Commissions).filter(Commissions.product_name == product_name).first()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

class Categories(BaseModel):
    categories: list[str]


@app.get("/calc/cat_list")
def get_calc_categories_list() -> Categories:
    result = get_categories_calc_list()
    res_list = []
    for res in result:
        res_list.append(res[0])
    return Categories(categories=res_list)


class SubCategories(BaseModel):
    category: str
    sub_category: str
    wb_commission: int
    wb_seller_commission: int


@app.get("/calc/sub_cat_list")
def get_calc_sub_categories_list(category: str) -> list[SubCategories]:
    result = get_subcategories_calc_list(category)
    res_list = []
    for sub_cat in result:
        res_list.append(SubCategories(category=sub_cat[0],
                                      sub_category=sub_cat[1],
                                      wb_commission=sub_cat[2],
                                      wb_seller_commission=sub_cat[3],
                                      ))
    return res_list


class SalesByCategory(BaseModel):
    articul: int
    sells: int
    cost: int
    name: str
    category_id: int


@app.get("/sales_with_category")
def get_sales_with_category():
    result = get_db_sales_by_category()
    res_list = []
    for cat in result:
        res_list.append(SalesByCategory(articul=cat[0],
                                        sells=cat[1],
                                        cost=cat[2],
                                        name=cat[3],
                                        category_id=cat[4]))
    return res_list


class Sales(BaseModel):
    id: int
    articul: int
    sells: int
    cost: int
    date: datetime
    name: str


@app.get("/sales")
def get_sales() -> list[Sales]:
    result = get_sales_from_db()
    res_list = []
    for r in result:
        res_list.append(Sales(id=r[0],
                              articul=r[1],
                              sells=r[2],
                              cost=r[3] / 100,
                              date=r[4],
                              name=r[5]))
    return res_list


class Analitics(BaseModel):
    wb_id: Optional[int]
    name: Optional[str]
    category_id: Optional[int]
    supplier: Optional[str]
    supplier_rating: Optional[float]
    sale_price_u: Optional[int]
    rating: Optional[int]
    review_rating: Optional[int]
    feedbacks: Optional[int]
    url: Optional[str]


@app.get('/analitics')
def get_analitics(articul: int) -> Optional[Analitics]:
    result = get_analitics_by_articul(articul)[0]
    if len(result) == 0:
        raise HTTPException(status_code=502, detail=f"Отсутствуют данные по артикулу {articul} в базе Nomenclature")
    try:
        return Analitics(wb_id=result[0],
                         name=result[1],
                         category_id=result[2],
                         supplier=result[3],
                         supplier_rating=result[4],
                         sale_price_u=result[5],
                         rating=result[6],
                         review_rating=result[7],
                         feedbacks=result[8],
                         url=f'https://www.wildberries.ru/catalog/{result[0]}/detail.aspx'
                         )
    except Exception as e:
        raise HTTPException(status_code=501, detail=f"Сервер вернул ошибку: {e}")


class NomenclatureResponce(BaseModel):
    id: int
    name: str


@app.get('/articul_for_analitics')
def get_analitics(limit=100, offset=0) -> list[NomenclatureResponce]:
    result = get_noms_list(limit, offset)
    res_list = []
    for nom in result:
        res_list.append(NomenclatureResponce(id=nom[0], name=nom[1]))
    return res_list
