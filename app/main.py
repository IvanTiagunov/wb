from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from sqlmodel import Session
from parser.db_filler import fill_db

from app.models.db import init_db, get_session
from app.models.models import Category, Commissions

def start_up():
    init_db()
    #fill_db()

app = FastAPI(on_startup=start_up())


@app.get("/categories", response_model=list[Category])
def get_categories(session: Session = Depends(get_session)):
    result = session.execute(select(Category))
    categories = result.scalars().all()
    return [Category(name=cat.name, url=cat.url, id=cat.id) for cat in categories]


@app.get("/commissions")
def get_commission(cost: float, product_name: str, is_wb_commission: bool, is_seller_commission: bool,
                   session: Session = Depends(get_session)):
    try:
        commission = session.query(Commissions).filter(Commissions.product_name == product_name).first()
        if is_wb_commission:
            final_cost = cost*(1-commission.wb_commission/100)
        if is_seller_commission:
            final_cost = cost * (1 - commission.wb_commission_seller / 100)
        return final_cost
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))