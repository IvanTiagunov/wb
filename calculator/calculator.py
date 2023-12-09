from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_orm.session import Session

my_database_connection = "postgresql://postgres:Olofmeister1337@localhost:5432/wildberries_commissions"
engine = create_engine(my_database_connection)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Commissions(Base):
    __tablename__ = "commissions"
    category = Column(String(256))
    product_name = Column(String(256), primary_key=True)
    wb_commission = Column(Integer)
    wb_commission_seller = Column(Integer)


Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def get_commission(cost: float, product_name: str, is_wb_commission: bool, is_seller_commission: bool, db: Session = Depends(get_db)):
    try:
        commission = db.query(Commissions).filter(Commissions.product_name == product_name).first()
        if is_wb_commission:
            final_cost = cost*(1-commission.wb_commission/100)
        if is_seller_commission:
            final_cost = cost * (1 - commission.wb_commission_seller / 100)
        return final_cost
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))
