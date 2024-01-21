import threading
from datetime import datetime
from typing import List

import psycopg2
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel import Session
from parser.db_filler import fill_db, get_sales_from_db, start_fill
from seller_calc.calc import start_calc
from app.models.db import init_db, get_session
from app.models.models import Category, Commissions
from seller_calc.calc import calculations
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
from sqlalchemy.sql import text
from fastapi.responses import Response

def start_up():
    #init_db()
    #fill_db()
    fill_thread = threading.Thread(target=start_fill)
    fill_thread.start()
    calc_thread = threading.Thread(target=start_calc)
    calc_thread.start()


app = FastAPI(on_startup=start_up())


@app.get("/categories", response_model=list[Category])
def get_categories(session: Session = Depends(get_session)):
    result = session.execute(select(Category))
    categories = result.scalars().all()
    return [Category(name=cat.name, url=cat.url, id=cat.id) for cat in categories]


@app.get("/commissions")
def get_commission(product_name: str, session: Session = Depends(get_session)):
    try:
        return session.query(Commissions).filter(Commissions.product_name == product_name).first()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class Sales(BaseModel):
    id: int
    articul:int
    sells:int
    cost:int
    date:datetime
    name:str

@app.get("/sales")
def get_sales() -> list[Sales]:
    result = get_sales_from_db()
    res_list = []
    for r in result:
        res_list.append(Sales(id=r[0],
                              articul=r[1],
                              sells=r[2],
                              cost=r[3]/100,
                              date=r[4],
                              name=r[5]))
    return res_list
