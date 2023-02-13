import itertools
from fastapi import APIRouter, Request, HTTPException, status
from datetime import datetime, date
from tinydb import where
from dirtbag import schemas
from dirtbag.helpers import (
    DB_trips,
    DB_todos,
    DB_users,
    get_crag_location,
    parse_comments,
)
from dirtbag.config import settings

router = APIRouter(tags=["trips"])


@router.get("/create_data")
async def create_data():
    async with (DB_trips as db_trips, DB_users as db_users):
        # users
        db_users.drop_tables()
        db_users.insert(
            {
                "name": "Jens Dav",
                "user_id": "jensda",
                "thumb_url": "https://27crags.s3.amazonaws.com/photos/000/298/298634/size_s-958682743ba1343d50bd2bd0ede8d6c8.jpg",
            }
        )
        db_users.insert(
            {
                "name": "Jacob Thing",
                "user_id": "jacobthi",
                "thumb_url": "https://www.gravatar.com/avatar/287713e4f80168a1ae1a64222da1d67b?s=80&d=retro",
            }
        )
        db_users.insert(
            {
                "name": "Nicklas Jefe",
                "user_id": "nicklasn",
                "thumb_url": "https://27crags.s3.amazonaws.com/photos/000/190/190723/size_s-8cec9165fea9.jpg",
            }
        )
        db_users.insert(
            {
                "name": "Jeppe Böf",
                "user_id": "jeppe_rosenkrands",
                "thumb_url": "https://www.gravatar.com/avatar/9d554d599fecbcc27aef48e9627e47c8?s=80&d=retro",
            }
        )
        db_users.insert(
            {
                "name": "Kristian Aagaard",
                "user_id": "kristiana",
                "thumb_url": "https://www.gravatar.com/avatar/20ba1e2c7606f4e2d3a05de57260fdb0?s=80&d=retro",
            }
        )
        db_users.insert(
            {
                "name": "Ivan Ischenko",
                "user_id": "ivanis",
                "thumb_url": "https://www.gravatar.com/avatar/5caaa8a1b45e98a8cae778b2aefdc8b1?s=80&d=retro",
            }
        )
        db_users.insert(
            {
                "name": "Jonas Holm",
                "user_id": "jonaspet",
                "thumb_url": "https://www.gravatar.com/avatar/f56ae650e54d03afb378267355d4701b?s=80&d=retro",
            }
        )
        # trip
        db_trips.drop_tables()
        db_trips.insert(
            {
                "area_name": "Bohuslän",
                "date_from": date(2023, 5, 15).isoformat(),
                "date_to": date(2023, 5, 22).isoformat(),
                "participants": ["jensda"],
            }
        )
        db_trips.insert(
            {
                "area_name": "Albarracin",
                "date_from": date(2023, 3, 18).isoformat(),
                "date_to": date(2023, 3, 25).isoformat(),
                "participants": ["jensda", "jacobthi", "nicklasn", "jeppe_rosenkrands"],
            }
        )
        db_trips.insert(
            {
                "area_name": "Albarracin",
                "date_from": date(2023, 3, 6).isoformat(),
                "date_to": date(2023, 3, 30).isoformat(),
                "participants": ["jensda"],
            }
        )
        db_trips.insert(
            {
                "area_name": "Fontainebleau",
                "date_from": date(2023, 4, 6).isoformat(),
                "date_to": date(2023, 4, 13).isoformat(),
                "participants": [
                    "kristiana",
                    "nicklasn",
                    "jeppe_rosenkrands",
                    "jacobthi",
                    "jensda",
                    "jonaspet",
                    "ivanis",
                ],
            }
        )
        db_trips.insert(
            {
                "area_name": "Kjugekull",
                "date_from": date(2023, 2, 17).isoformat(),
                "date_to": date(2023, 2, 17).isoformat(),
                "participants": [
                    "kristiana",
                    "ivanis",
                ],
            }
        )
        db_trips.insert(
            {
                "area_name": "Magic Wood",
                "date_from": date(2023, 6, 19).isoformat(),
                "date_to": date(2023, 6, 26).isoformat(),
                "participants": ["jensda", "jonaspet"],
            }
        )


@router.get("/trips")
async def trips() -> list[schemas.TripList]:
    async with DB_trips as db_trips:
        data = sorted(db_trips, key=lambda d: d["date_from"])
    res = []
    for trip in data:
        async with DB_users as db_users:
            users = db_users.search(where("user_id").one_of(trip.pop("participants")))
        participants = [schemas.User(id=u.doc_id, **u) for u in users]
        duration = (
            date.fromisoformat(trip["date_to"]) - date.fromisoformat(trip["date_from"])
        ).days
        res.append(
            schemas.TripList(
                id=trip.doc_id, participants=participants, duration=duration, **trip
            )
        )
    return res


@router.get("/trips/{trip_id}")
async def trip(trip_id: int) -> schemas.Trip:
    async with (DB_trips as db_trips, DB_todos as db_todos, DB_users as db_users):
        trip = db_trips.get(doc_id=trip_id)

        users = db_users.search(where("user_id").one_of(trip["participants"]))

        # get all todos for the trip area
        data = sorted(
            db_todos.search(
                (where("area_name") == trip["area_name"])
                & where("user_id").one_of(trip["participants"])
            ),
            key=lambda d: d["app_url"],
        )

        # first group by app_url to make todos unique
        def grouper(d):
            for k, g in itertools.groupby(data, key=lambda d: d["app_url"]):
                lg = list(g)
                user_ids = [i["user_id"] for i in lg]
                yield {
                    **lg[0],
                    "user_ids": user_ids,
                    "comments": list(parse_comments(lg)),
                }

        grouped_data = sorted(
            [d for d in grouper(data)], key=lambda d: d["sector_name"]
        )
        # group by sector_name
        sectors_dict = {
            k: list(g)
            for k, g in itertools.groupby(grouped_data, key=lambda d: d["sector_name"])
        }
        # return the data packed in a schemas.Trip
        return schemas.Trip(
            id=trip.doc_id,
            area_name=trip["area_name"],
            date_from=trip["date_from"],
            date_to=trip["date_to"],
            participants=[schemas.User(id=u.doc_id, **u) for u in users],
            sectors=[
                schemas.Sector(
                    name=k,
                    url=v[0]["sector_url"],
                    app_url=v[0]["sector_app_url"],
                    thumb_url=v[0]["sector_thumb_url"],
                    location=get_crag_location(v[0]["sector_name"]),
                    todos=[schemas.TripTodo(**todo) for todo in v],
                )
                for k, v in sectors_dict.items()
            ],
        )
