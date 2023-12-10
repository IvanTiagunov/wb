from fastapi import FastAPI, Depends
from sqlmodel import select
from sqlmodel import Session
from parser.db_filler import fill_db

from app.models.db import init_db, get_session
from app.models.models import Category

def start_up():
    init_db()
    fill_db()

app = FastAPI(on_startup=start_up())


@app.get("/categories", response_model=list[Category])
def get_categories(session: Session = Depends(get_session)):
    result = session.execute(select(Category))
    categories = result.scalars().all()
    return [Category(name=cat.name, url=cat.url, id=cat.id) for cat in categories]