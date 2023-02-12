import asyncio
import itertools
from fastapi import APIRouter, Request, HTTPException, status
from datetime import datetime, date
from tinydb import where
from dirtbag import schemas
from dirtbag.helpers import DB_trips, DB_todos
from dirtbag.config import settings

router = APIRouter(tags=["test"])


@router.get("/todos/{area_name}")
async def todos(area_name):
    async with DB_todos as db:
        data = sorted(
            db.search(where("area_name") == area_name), key=lambda d: d["app_url"]
        )

    # first group by app_url to make todos unique
    def grouper(d):
        for k, g in itertools.groupby(data, key=lambda d: d["app_url"]):
            lg = list(g)
            user_ids = [i["user_id"] for i in lg]
            yield {**lg[0], "user_ids": user_ids}

    grouped_data = sorted([d for d in grouper(data)], key=lambda d: d["sector_name"])

    # then return grouped by sector name
    return {
        k: list(g)
        for k, g in itertools.groupby(grouped_data, key=lambda d: d["sector_name"])
    }

    return data
    # TODO: merge from trip-participants? dedupe on app-url
    return [schemas.Todo(**d) for d in data]


@router.get("/areas")
async def areas():
    async with DB_todos as db:
        return {d["area_name"] for d in db}
