from pydantic import BaseModel
from datetime import datetime, date
from typing import Literal, Optional, Union, AnyStr


class BaseTodo(BaseModel):
    name: str
    grade: str
    thumb_url: str
    url: str
    app_url: str
    sector_name: str
    sector_url: str
    sector_app_url: str
    area_name: str
    area_url: str


class TripTodo(BaseTodo):
    user_ids: list[str]


class DBTodo(BaseTodo):
    id: str
    user_id: str


class Sector(BaseModel):
    name: str
    url: str
    app_url: str
    thumb_url: str
    location: tuple[float, float]
    todos: list[Union[TripTodo, BaseTodo]]


class User(BaseModel):
    id: int
    user_id: str
    name: str
    thumb_url: str


class Trip(BaseModel):
    id: int
    area_name: str
    date_from: date
    date_to: date
    participants: list[User]
    sectors: list[Sector]


class TripList(BaseModel):
    id: int
    area_name: str
    date_from: date
    date_to: date
    duration: int
    participants: list[User]
