import itertools
from fastapi import APIRouter, Request, HTTPException, status
from datetime import datetime, date
from tinydb import where
from dirtbag import schemas
from dirtbag.helpers import DB_trips, DB_todos, DB_users, get_crag_location
from dirtbag.config import settings

router = APIRouter(tags=["users"])


@router.get("/users")
def users() -> list[schemas.User]:
    pass


@router.get("/users/{user_id}")
async def user_get(user_id) -> schemas.User:
    async with DB_users as db:
        user = db.get(doc_id=user_id)
    return schemas.User(id=user.doc_id, **user)


@router.get("/users/{user_id}/areas")
async def user_areas(user_id: int) -> list[dict]:
    async with (DB_todos as db_todos, DB_users as db_users):
        user = db_users.get(doc_id=user_id)
        # get all todos for this user and sort by sector_name
        data = sorted(
            db_todos.search(where("user_id") == user["user_id"]),
            key=lambda d: d["area_name"],
        )
        # group by area_name
        areas_dict = {
            k: len(list(g))
            for k, g in itertools.groupby(data, key=lambda d: d["area_name"])
        }
        return [{"name": k, "todos_count": v} for k, v in areas_dict.items()]


@router.get("/users/{user_id}/area/{area_name}/todos")
async def user_todos(user_id: int, area_name: str) -> list[schemas.Sector]:
    async with (DB_todos as db_todos, DB_users as db_users):
        user = db_users.get(doc_id=user_id)
        # get all todos for this user and sort by sector_name
        data = sorted(
            db_todos.search(
                (where("user_id") == user["user_id"])
                & (where("area_name") == area_name)
            ),
            key=lambda d: d["sector_name"],
        )
        # group by sector_name
        sectors_dict = {
            k: list(g)
            for k, g in itertools.groupby(data, key=lambda d: d["sector_name"])
        }
        # return the data packed in a schemas.Sector
        return [
            schemas.Sector(
                name=k,
                url=v[0]["sector_url"],
                app_url=v[0]["sector_app_url"],
                thumb_url=v[0]["sector_thumb_url"],
                location=get_crag_location(v[0]["sector_name"]),
                todos=[schemas.BaseTodo(**todo) for todo in v],
            )
            for k, v in sectors_dict.items()
        ]
