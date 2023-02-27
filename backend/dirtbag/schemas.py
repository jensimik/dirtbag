from pydantic import BaseModel
from datetime import datetime, date
from typing import Literal, Optional, Union, AnyStr


class Comment(BaseModel):
    type: str
    text: str
    url: Optional[str]


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
    comment: Optional[list[Comment]]


class TripTodo(BaseTodo):
    user_ids: list[str]
    comments: list[Comment]


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
    user_id: str
    name: Optional[str]


class BaseTrip(BaseModel):
    area_name: str
    date_from: date
    date_to: date
    markdown: str


2


class TripDB(BaseTrip):
    participants: str
    pin: str = "1337"


class Trip(BaseTrip):
    id: int
    participants: list[User]
    sectors: list[Sector]


class TripList(BaseModel):
    id: int
    area_name: str
    date_from: date
    date_from_display: str
    date_to: date
    date_to_display: str
    duration: int
    participants: list[User]


class TripUpdate(BaseModel):
    date_from: date
    date_to: date
    participants: str
    markdown: str
