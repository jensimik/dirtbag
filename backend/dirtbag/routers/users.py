import itertools
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from datetime import datetime, date
from tinydb import where
from dirtbag import schemas
from dirtbag.c27_fetcher import refresh_27crags
from dirtbag.helpers import DB_todos, DB_27cache, reversor
from dirtbag.config import settings

router = APIRouter(tags=["users"])


@router.post("/user/{user_id}")
async def sync_user(user_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(refresh_27crags, usernames=[user_id])


@router.get("/user/{user_id}/sync_done")
async def sync_done(user_id: str):
    async with DB_27cache as db:
        user_lock = db.get(where("user_id_lock") == user_id)
    if user_lock:
        return {"processing": user_lock["locked"]}
    return {"processing": True}


@router.get("/user/{user_id}/areas")
async def user_areas(user_id: str) -> list[dict]:
    async with DB_todos as db:
        # get all todos for this user and sort by sector_name
        data = sorted(
            db.search(where("user_id") == user_id),
            key=lambda d: d["area_name"],
        )
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        # group by area_name
        areas_dict = {
            k: len(list(g))
            for k, g in itertools.groupby(data, key=lambda d: d["area_name"])
        }
        return [{"name": k, "todos_count": v} for k, v in areas_dict.items()]


@router.get("/user/{user_id}/{area_name}/todos")
async def user_areas(user_id: str, area_name: str):
    async with (DB_todos as db_todos):
        # get all todos for the trip area
        data = sorted(
            db_todos.search(
                (where("area_name") == area_name) & (where("user_id") == user_id)
            ),
            key=lambda d: d["sector_name"],
        )

        # group by sector_name
        sectors_dict = {
            k: list(g)
            for k, g in itertools.groupby(data, key=lambda d: d["sector_name"])
        }

        # return the data
        return dict(
            sectors=[
                schemas.Sector(
                    name=k,
                    url=v[0]["sector_url"],
                    app_url=v[0]["sector_app_url"],
                    thumb_url=v[0]["sector_thumb_url"],
                    todos=[
                        schemas.BaseTodo(**todo)
                        for todo in sorted(
                            v, key=lambda d: (reversor(d["grade"]), d["name"])
                        )
                    ],
                )
                for k, v in sectors_dict.items()
            ]
        )
