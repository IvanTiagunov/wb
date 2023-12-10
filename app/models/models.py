from typing import Optional, List
from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wb_id: int
    parent: Optional[int]
    seo: Optional[str]
    name: str
    url: str
    shard: Optional[str]
    query: Optional[str]

# class Card(SQLModel, table=True):
#     some_fields: int = Field(default=None, primary_key=True)
