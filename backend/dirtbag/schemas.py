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
    thumb_url: Optional[str] = ""
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
    ticks: list[str]
    comments: list[Comment]


class DBTodo(BaseTodo):
    id: str
    user_id: str


class Sector(BaseModel):
    name: str
    url: str
    app_url: str
    thumb_url: str
    todos: list[Union[TripTodo, BaseTodo]]


class User(BaseModel):
    user_id: str
    name: Optional[str]


class BaseTrip(BaseModel):
    area_name: str
    date_from: date
    date_to: date
    markdown: Optional[str]
    markdown_html: Optional[str]


class TripDB(BaseTrip):
    participants: str
    pin: str


class Trip(BaseTrip):
    id: int
    yr_link: Optional[str] = None
    yr_svg: Optional[str] = None
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
