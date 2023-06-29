import itertools
from fastapi import APIRouter, Response, BackgroundTasks, HTTPException, status
from datetime import datetime, date
from tinydb import where
from markdown import markdown
from dirtbag import schemas
from dirtbag.helpers import (
    DB_trips,
    DB_todos,
    DB_sends,
    reversor,
    yr_data,
)
from dirtbag.c27_fetcher import refresh_27crags
from dirtbag.config import settings

router = APIRouter(tags=["trips"])


@router.post("/trips")
async def new_trip(new_trip: schemas.TripDB, background_tasks: BackgroundTasks) -> int:
    async with DB_trips as db:
        data = {
            "area_name": new_trip.area_name,
            "date_from": new_trip.date_from.isoformat(),
            "date_to": new_trip.date_to.isoformat(),
            "pin": new_trip.pin,
            "participants": [
                {"user_id": user_id.strip().lower(), "name": f"A{i}"}
                for i, user_id in enumerate(new_trip.participants.split(","))
            ],
        }
        doc_id = db.insert(data)
    background_tasks.add_task(
        refresh_27crags,
        usernames=[u["user_id"] for u in data["participants"]],
        trip_id=doc_id,
    )
    return doc_id


@router.get("/trips")
async def trips() -> dict[str, list[schemas.TripList]]:
    now = datetime.utcnow().isoformat()
    async with DB_trips as db_trips:
        data = sorted(db_trips, key=lambda d: d["date_from"])
    res = {"current": [], "past": []}
    for trip in data:
        participants = [schemas.User(**u) for u in trip["participants"]]
        duration = (
            date.fromisoformat(trip["date_to"]) - date.fromisoformat(trip["date_from"])
        ).days
        trip["participants"] = participants
        date_to_display = "{0: %d %b}".format(date.fromisoformat(trip["date_to"]))
        date_from_display = "{0: %d %b}".format(date.fromisoformat(trip["date_from"]))
        res["current" if trip["date_to"] > now else "past"].append(
            schemas.TripList(
                id=trip.doc_id,
                duration=duration,
                date_from_display=date_from_display,
                date_to_display=date_to_display,
                **trip,
            )
        )
        # sort past trips in reverse order
        res["past"] = sorted(
            res["past"], key=lambda d: d.date_from_display, reverse=True
        )
    return res


# @router.get("/trips/{trip_id}")
# async def trip_unauthed(trip_id):
#     async with DB_trips as db_trips:
#         trip = db_trips.get(doc_id=trip_id)
#         participants = [schemas.User(**u) for u in trip["participants"]]
#         trip["participants"] = participants
#         duration = (
#             date.fromisoformat(trip["date_to"]) - date.fromisoformat(trip["date_from"])
#         ).days
#         date_to_display = "{0: %d %b}".format(date.fromisoformat(trip["date_to"]))
#         date_from_display = "{0: %d %b}".format(date.fromisoformat(trip["date_from"]))
#     return schemas.TripList(
#         id=trip.doc_id,
#         duration=duration,
#         date_from_display=date_from_display,
#         date_to_display=date_to_display,
#         **trip,
#     )


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


@router.patch("/trips/{trip_id}/{pin}")
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
            "user_id": raw_user_id.strip().lower(),
            "name": current_participants.get(raw_user_id.strip(), f"A{i}"),
        }
        for i, raw_user_id in enumerate(trip_update.participants.split(","))
    ]
    trip["date_from"] = trip_update.date_from.isoformat()
    trip["date_to"] = trip_update.date_to.isoformat()
    trip["markdown"] = trip_update.markdown
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


@router.delete("/trips/{trip_id}/{pin}")
async def trip_delete(trip_id: int, pin: str):
    async with DB_trips as db:
        trip = db.get(doc_id=trip_id)
        if trip["pin"] != pin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        db.remove(doc_ids=[trip.doc_id])
    return {"status": "OK"}


@router.get("/trips/{trip_id}")
async def trip(trip_id: int, response: Response) -> schemas.Trip:
    async with (DB_trips as db_trips, DB_todos as db_todos, DB_sends as db_sends):
        trip = db_trips.get(doc_id=trip_id)

        ticks = sorted(
            db_sends.search(
                (where("area_name") == trip["area_name"])
                & where("user_id").one_of([u["user_id"] for u in trip["participants"]])
            ),
            key=lambda d: d["app_url"],
        )

        ticks_by_app_url = {
            k: [i["user_id"] for i in list(g)]
            for k, g in itertools.groupby(ticks, key=lambda d: d["app_url"])
        }

        is_past_trip = trip["date_to"] < date.today().isoformat()

        # get all todos for the trip area
        if is_past_trip:
            data = []
            yr_link, yr_svg = "", ""
        else:
            yr_link, yr_svg = yr_data(trip["area_name"])
            data = sorted(
                db_todos.search(
                    (where("area_name") == trip["area_name"])
                    & where("user_id").one_of(
                        [u["user_id"] for u in trip["participants"]]
                    )
                ),
                key=lambda d: d["app_url"],
            )
        # concat todos and ticks together (only take the ticks during the trip)
        data = sorted(
            data
            + [
                t
                for t in ticks
                if (
                    (t["ascent_date"] >= trip["date_from"][:10])
                    & (t["ascent_date"] <= trip["date_to"][:10])
                )
            ],
            key=lambda d: d["app_url"],
        )

        # first group by app_url to make todos unique
        def grouper(d):
            for k, g in itertools.groupby(data, key=lambda d: d["app_url"]):
                lg = list(g)
                user_ids = [
                    i["user_id"]
                    for i in lg
                    if (("ascent_date" not in i) or is_past_trip)
                ]
                # unpack all users comments
                comments = [u for i in lg for u in i.get("comment", "")]
                yield {
                    **lg[0],
                    "user_ids": [] if is_past_trip else user_ids,
                    "ticks": user_ids if is_past_trip else ticks_by_app_url.get(k, []),
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
            markdown=trip.get("markdown", ""),
            markdown_html=markdown(trip.get("markdown", "")),
            yr_link=yr_link,
            yr_svg=yr_svg,
            participants=[schemas.User(**u) for u in trip["participants"]],
            sectors=[
                schemas.Sector(
                    name=k,
                    url=v[0]["sector_url"],
                    app_url=v[0]["sector_app_url"],
                    thumb_url=v[0]["sector_thumb_url"],
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
