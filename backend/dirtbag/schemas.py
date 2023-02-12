from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional, AnyStr


class Todo(BaseModel):
    id: str
    user_id: str
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
