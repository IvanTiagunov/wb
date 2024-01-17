from typing import Optional, List

import sqlmodel
from datetime import datetime
from sqlalchemy import Column, Integer
from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wb_id: int = Field(sa_column=Column("wb_id", Integer, unique=True))
    parent: Optional[int]
    seo: Optional[str]
    name: str
    url: str
    shard: Optional[str]
    query: Optional[str]

# class Card(SQLModel, table=True):
#     some_fields: int = Field(default=None, primary_key=True)


# "id" - артикул на wb, "root" - похоже внутренний id wb, "brand" - название магазина, name - наименование товара,
# supplier, supplierId, supplierRating, priceU - цена, умноженная на 100 (зачеркнутая), logistricsCost, returnCost,
# sizes пока не используем
# diffPrice (bool) хз, pics - int, rating - float, reviewRating - float, feedbacks - int, volume - int,
# salePriceU - цена умнож на 100 реальная, sale - размер скидки
class Nomenclature(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(default=None, foreign_key="category.wb_id")
    root: int
    brand: str
    brandId: int
    siteBrandId: int
    name: str
    supplier: str
    supplierId: int
    supplierRating: float
    priceU: int
    salePriceU: int
    sale: int
    logistricsCost: Optional[int]
    returnCost: Optional[int]
    diffPrice: bool
    pics: int
    rating: float
    reviewRating: float
    feedbacks: int
    volume: int


class Amount(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nm_id: int = Field(default=None, foreign_key="nomenclature.id")
    name: str
    wh: int
    qty: int
    price: int
    date: datetime
