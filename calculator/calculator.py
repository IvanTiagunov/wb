import os
from sqlmodel import Field, SQLModel, SQLModel, Session, create_engine
from fastapi import FastAPI, Depends, HTTPException

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)


class Commissions(SQLModel, table=True):
    category: [str]
    product_name: [str] = Field(default=None, primary_key=True)
    wb_commission: [int]
    wb_commission_seller: [int]


app = FastAPI()


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def get_commission(cost: float, product_name: str, is_wb_commission: bool, is_seller_commission: bool, db: Session = Depends(get_session)):
    try:
        commission = db.query(Commissions).filter(Commissions.product_name == product_name).first()
        if is_wb_commission:
            final_cost = cost*(1-commission.wb_commission/100)
        if is_seller_commission:
            final_cost = cost * (1 - commission.wb_commission_seller / 100)
        return final_cost
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))
