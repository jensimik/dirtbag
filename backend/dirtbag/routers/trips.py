import asyncio
from fastapi import APIRouter, Request, HTTPException, status
from datetime import datetime, date
from tinydb import where
from dirtbag import schemas
from dirtbag.helpers import DB_trips, DB_todos
from dirtbag.config import settings

router = APIRouter(tags=["trips"])


@router.get("/")
async def trips():
    return [
        {
            "destination": "Albarracin",
            "participants": [
                {"id": 1, "name": "Jens Dav", "27_id": "jensda"},
                {"id": 2, "name": "Jacob Thing", "27_id": "jacobthi"},
                {"id": 3, "name": "Nicklas Jefe", "27_id": "nicklasn"},
                {"id": 4, "name": "Jeppe Böf", "27_id": "jeppe_rosenkrands"},
            ],
            "date_from": date(2023, 3, 18).isoformat(),
            "date_to": date(2023, 3, 25).isoformat(),
        },
    ]


@router.get("/trip/{trip_id}/todo_list")
async def trip_todo_list(trip_id: int) -> list[schemas.Todo]:
    async with DB_todos as db:
        return [schemas.Todo(**d) for d in db.search(where("trip_id") == trip_id)]
