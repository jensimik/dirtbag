import itertools
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from datetime import datetime, date
from tinydb import where
from libgravatar import Gravatar
from dirtbag import schemas
from dirtbag.helpers import DB_trips, DB_todos, DB_users, reversor, get_crag_location
from dirtbag.c27_fetcher import refresh_27crags
from dirtbag.config import settings

router = APIRouter(tags=["trips"])


@router.get("/create_data")
async def create_data():
    async with (DB_trips as db_trips, DB_users as db_users):
        db_trips.drop_tables()
        db_trips.insert(
            {
                "area_name": "Bohuslän",
                "date_from": date(2023, 5, 15).isoformat(),
                "date_to": date(2023, 5, 22).isoformat(),
                "pin": "1337",
                "participants": [{"user_id": "jensda", "name": "JD"}],
            }
        )
        db_trips.insert(
            {
                "area_name": "Albarracin",
                "date_from": date(2023, 3, 18).isoformat(),
                "date_to": date(2023, 3, 25).isoformat(),
                "pin": "1337",
                "participants": [
                    {"user_id": "jensda", "name": "JD"},
                    {
                        "user_id": "jacobthi",
                        "name": "JT",
                    },
                    {
                        "user_id": "nicklasn",
                        "name": "NN",
                    },
                    {
                        "user_id": "jeppe_rosenkrands",
                        "name": "JR",
                    },
                ],
            }
        )
        db_trips.insert(
            {
                "area_name": "Albarracin",
                "date_from": date(2023, 3, 6).isoformat(),
                "date_to": date(2023, 3, 30).isoformat(),
                "pin": "1337",
                "participants": [{"user_id": "jensda", "name": "JD"}],
            }
        )
        db_trips.insert(
            {
                "area_name": "Fontainebleau",
                "date_from": date(2023, 4, 6).isoformat(),
                "date_to": date(2023, 4, 13).isoformat(),
                "pin": "1337",
                "participants": [
                    {"user_id": "jensda", "name": "JD"},
                ],
            }
        )
        db_trips.insert(
            {
                "area_name": "Magic Wood",
                "date_from": date(2023, 6, 19).isoformat(),
                "date_to": date(2023, 6, 26).isoformat(),
                "pin": "1337",
                "participants": [{"user_id": "jensda", "name": "JD"}],
            }
        )


@router.get("/trips")
async def trips() -> list[schemas.TripList]:
    async with DB_trips as db_trips:
        data = sorted(db_trips, key=lambda d: d["date_from"])
    res = []
    for trip in data:
        participants = [schemas.User(**u) for u in trip["participants"]]
        duration = (
            date.fromisoformat(trip["date_to"]) - date.fromisoformat(trip["date_from"])
        ).days
        trip["participants"] = participants
        date_to_display = "{0: %d %b}".format(date.fromisoformat(trip["date_to"]))
        date_from_display = "{0: %d %b}".format(date.fromisoformat(trip["date_from"]))
        res.append(
            schemas.TripList(
                id=trip.doc_id,
                duration=duration,
                date_from_display=date_from_display,
                date_to_display=date_to_display,
                **trip,
            )
        )
    return res


@router.get("/trips/{trip_id}")
async def trip_unauthed(trip_id):
    async with DB_trips as db_trips:
        trip = db_trips.get(doc_id=trip_id)
        participants = [schemas.User(**u) for u in trip["participants"]]
        trip["participants"] = participants
        duration = (
            date.fromisoformat(trip["date_to"]) - date.fromisoformat(trip["date_from"])
        ).days
        date_to_display = "{0: %d %b}".format(date.fromisoformat(trip["date_to"]))
        date_from_display = "{0: %d %b}".format(date.fromisoformat(trip["date_from"]))
    return schemas.TripList(
        id=trip.doc_id,
        duration=duration,
        date_from_display=date_from_display,
        date_to_display=date_to_display,
        **trip,
    )


@router.post("/trips/{trip_id}/{pin}/resync")
async def trip_resync(trip_id: int, pin: str, background_tasks: BackgroundTasks):
    async with DB_trips as db_trips:
        trip = db_trips.get(doc_id=trip_id)
    if trip["pin"] != pin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    background_tasks.add_task(
        refresh_27crags,
        usernames=[u["user_id"] for u in trip["participants"]],
        trip_id=trip_id,
    )
    return {"status": "OK"}


@router.post("/trips/{trip_id}/{pin}/update")
async def trip_update(
    trip_id: int,
    pin: str,
    trip_update: schemas.TripUpdate,
    background_tasks: BackgroundTasks,
):
    async with DB_trips as db:
        trip = db.get(doc_id=trip_id)
    if trip["pin"] != pin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    current_participants = {u["user_id"]: u["name"] for u in trip["participants"]}
    old_set = {u["user_id"] for u in trip["participants"]}
    trip["participants"] = [
        {
            "user_id": raw_user_id.strip(),
            "name": current_participants.get(raw_user_id.strip(), f"A{i}"),
        }
        for i, raw_user_id in enumerate(trip_update.participants.split(","))
    ]
    async with DB_trips as db:
        db.upsert(trip)
    new_set = {u["user_id"] for u in trip["participants"]}
    if old_set != new_set:
        background_tasks.add_task(
            refresh_27crags,
            usernames=[u["user_id"] for u in trip["participants"]],
            trip_id=trip_id,
        )
    return {"status": "OK"}


@router.get("/trips/{trip_id}/{pin}")
async def trip(trip_id: int, pin: str) -> schemas.Trip:
    async with (DB_trips as db_trips, DB_todos as db_todos, DB_users as db_users):
        trip = db_trips.get(doc_id=trip_id)
        if trip["pin"] != pin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        # get all todos for the trip area
        data = sorted(
            db_todos.search(
                (where("area_name") == trip["area_name"])
                & where("user_id").one_of([u["user_id"] for u in trip["participants"]])
            ),
            key=lambda d: d["app_url"],
        )

        # first group by app_url to make todos unique
        def grouper(d):
            for k, g in itertools.groupby(data, key=lambda d: d["app_url"]):
                lg = list(g)
                user_ids = [i["user_id"] for i in lg]
                # unpack all users comments
                comments = [u for i in lg for u in i["comment"]]
                yield {
                    **lg[0],
                    "user_ids": user_ids,
                    "comments": comments,
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
            participants=[schemas.User(**u) for u in trip["participants"]],
            sectors=[
                schemas.Sector(
                    name=k,
                    url=v[0]["sector_url"],
                    app_url=v[0]["sector_app_url"],
                    thumb_url=v[0]["sector_thumb_url"],
                    location=get_crag_location(v[0]["sector_name"]),
                    todos=[
                        schemas.TripTodo(**todo)
                        for todo in sorted(
                            v, key=lambda d: (reversor(d["grade"]), d["name"])
                        )
                    ],
                )
                for k, v in sectors_dict.items()
            ],
        )
