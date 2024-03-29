import hashlib
import random
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

import httpx
from aiolimiter import AsyncLimiter

from .config import settings
from .helpers import DB_27cache, DB_sends, DB_todos, DB_trips, tinydb_set, where
from .parse import HTML, HtmlElement

rate_limit = AsyncLimiter(1, 15)


def get_app_argument_from_html(html) -> str:
    meta_content = html.find("meta[name='apple-itunes-app']", first=True).attrs[
        "content"
    ]
    return meta_content.split("app-argument=")[1]


async def get_thumb_url(element: HtmlElement) -> str:
    img_element = element.find("img", first=True)
    thumb_url = img_element.attrs["src"] if img_element else ""
    return thumb_url


async def get_problem_data(
    problem_url: str, client: httpx.AsyncClient, element: HtmlElement
) -> str:
    async with DB_27cache as db:
        data = db.get(where("problem_url") == problem_url)
    if data:
        thumb_url = data.get("thumb_url")
        if not thumb_url:
            thumb_url = await get_thumb_url(element)
            print(f"found thumb_url {thumb_url}")
            async with DB_27cache as db:
                db.update(
                    tinydb_set("thumb_url", thumb_url),
                    where("problem_url") == problem_url,
                )
        return data["app_argument"], thumb_url
    # # be gentle with 27crags
    await rate_limit.acquire()
    r = await client.get(problem_url)
    if r.is_success:
        # to get big image and canvas markup i have to be logged in for premium sites
        app_argument = get_app_argument_from_html(html=HTML(html=r.content))
    thumb_url = await get_thumb_url(element)
    async with DB_27cache as db:
        data = db.upsert(
            {
                "problem_url": problem_url,
                "app_argument": app_argument,
                "thumb_url": thumb_url,
            },
            where("problem_url") == problem_url,
        )
    return app_argument, thumb_url


async def get_sector_data(sector_url: str, client: httpx.AsyncClient) -> dict:
    # check cache first
    async with DB_27cache as db:
        data = db.get(where("sector_url") == sector_url)
    if data:
        return data
    # be gentle with 27crags
    await rate_limit.acquire()
    # no cache result then fetch
    r = await client.get(sector_url)
    if r.is_success:
        html = HTML(html=r.content)
        app_url = get_app_argument_from_html(html=html)
        area_div = html.find("div.area-container", first=True)
        ass = area_div.find("a", first=True)
        if ", " in ass.text:
            area_url = "https://27crags.com" + ass.attrs["href"]
            area_name = ass.text.split(", ")[0]
        else:
            area_url = ""
            area_name = ""
        sector_thumb_url = html.find("meta[property='og:image']", first=True).attrs[
            "content"
        ]
        data = {
            "area_url": area_url,
            "area_name": area_name,
            "app_url": app_url,
            "sector_url": sector_url,
            "sector_thumb_url": sector_thumb_url,
        }
        async with DB_27cache as db:
            db.upsert(data, where("sector_url") == sector_url)
        return data
    raise Exception(f"Sector not found {sector_url}")


async def refresh_todo_list(
    username: str, client: httpx.AsyncClient, trip_id: int = None
):
    async with DB_27cache as db:
        db.upsert(
            {"user_id_lock": username, "locked": True},
            where("user_id_lock") == username,
        )
    # now get the todo list
    batch_id = datetime.utcnow().isoformat()
    # be gentle with 27crags
    await rate_limit.acquire()
    r = await client.get(f"https://27crags.com/climbers/{username}/ascents/todo")
    if r.is_success:
        print(f"got todo list of {username}")
        html = HTML(html=r.content)
        climber_name = html.find("div.climber-name", first=True).text
        if trip_id:
            climber_initials = climber_name.split()[0][0] + climber_name.split()[-1][0]
            async with DB_trips as db_trips:
                trip = db_trips.get(doc_id=trip_id)
                for u in trip["participants"]:
                    if u["user_id"] == username:
                        u["name"] = climber_initials
                db_trips.upsert(trip)
        if todo_list := html.find("table.todo-list tbody", first=True):
            for tr in todo_list.find("tr"):
                grade = tr.find("td.grade", first=True).text
                first_td = tr.find("td", first=True)
                ass = first_td.find("a")
                img_element = first_td.find("img", first=True)
                name = ass[1 if img_element else 0].text
                print(f"fetching problem {name}")
                url = "https://27crags.com" + ass[1 if img_element else 0].attrs["href"]
                app_url, thumb_url = await get_problem_data(
                    problem_url=url, client=client, element=tr
                )
                comment = []
                if ascent_details := tr.find("div.ascent-details", first=True):
                    for link in ascent_details.find("a"):
                        _url = link.attrs["href"]
                        o = urlparse(_url)
                        comment.append(
                            {"type": "link", "url": _url, "text": o.hostname}
                        )
                    if not comment:
                        comment = [{"type": "text", "text": ascent_details.text}]
                sector_url = (
                    "https://27crags.com"
                    + tr.find("td.stxt", first=True).find("a", first=True).attrs["href"]
                )
                sector_name = tr.find("td.stxt", first=True).text
                try:
                    sector_data = await get_sector_data(
                        sector_url=sector_url, client=client
                    )
                except Exception:
                    print(f"could not find sector_data for {sector_name}")
                    continue
                unique_id = hashlib.md5(str.encode(f"{username}-{app_url}")).hexdigest()
                area_name = (
                    sector_data["area_name"]
                    if sector_data["area_name"]
                    else sector_name
                )
                area_url = (
                    sector_data["area_url"] if sector_data["area_name"] else sector_url
                )
                data = {
                    "id": unique_id,
                    "user_id": username,
                    "name": name,
                    "grade": grade,
                    "thumb_url": thumb_url,
                    "url": url,
                    "app_url": app_url,
                    "sector_name": sector_name,
                    "sector_url": sector_url,
                    "sector_app_url": sector_data["app_url"],
                    "sector_thumb_url": sector_data["sector_thumb_url"],
                    "area_name": area_name,
                    "area_url": area_url,
                    "comment": comment,
                    "batch_id": batch_id,
                }
                async with DB_todos as db:
                    db.upsert(data, where("id") == unique_id)
    else:
        print(f"error getting todolist for {username}")
    # clear out those not updated in the batch
    async with DB_todos as db:
        db.remove((where("user_id") == username) & (where("batch_id") < batch_id))
    # clear simple sync lock
    async with DB_27cache as db:
        db.upsert(
            {"user_id_lock": username, "locked": False},
            where("user_id_lock") == username,
        )


async def refresh_tick_list(username: str, client: httpx.AsyncClient):
    async with DB_27cache as db:
        db.upsert(
            {"user_id_lock": username, "locked": True},
            where("user_id_lock") == username,
        )
    # now get the todo list
    batch_id = datetime.utcnow().isoformat()
    # be gentle with 27crags
    await rate_limit.acquire()
    r = await client.get(f"https://27crags.com/climbers/{username}/ascents")
    if r.is_success:
        print(f"got tick list of {username}")
        html = HTML(html=r.content)
        if todo_list := html.find("table.route-list tbody", first=True):
            for tr in todo_list.find("tr"):
                try:
                    ascent_date = tr.find("td.ascent-date", first=True).text
                    grade = tr.find("span.grade")[-1].text.upper()
                    tds = tr.find("td.stxt")
                    first_td = tr.find("td", first=True)
                    ass = first_td.find("a")
                    img_element = first_td.find("img", first=True)
                    name = ass[1 if img_element else 0].text
                    print(f"fetching problem {name}")
                    url = (
                        "https://27crags.com"
                        + ass[1 if img_element else 0].attrs["href"]
                    )
                    print(f"fetching problem {name}")
                    app_url, thumb_url = await get_problem_data(
                        problem_url=url, client=client, element=tr
                    )
                    sector_url = (
                        "https://27crags.com"
                        + tds[1].find("a", first=True).attrs["href"]
                    )
                    sector_name = tds[1].text
                    sector_data = await get_sector_data(
                        sector_url=sector_url, client=client
                    )
                    unique_id = hashlib.md5(
                        str.encode(f"{username}-{app_url}")
                    ).hexdigest()
                    area_name = (
                        sector_data["area_name"]
                        if sector_data["area_name"]
                        else sector_name
                    )
                    area_url = (
                        sector_data["area_url"]
                        if sector_data["area_name"]
                        else sector_url
                    )
                    data = {
                        "id": unique_id,
                        "user_id": username,
                        "name": name,
                        "grade": grade,
                        "url": url,
                        "app_url": app_url,
                        "thumb_url": thumb_url,
                        "sector_name": sector_name,
                        "sector_url": sector_url,
                        "sector_app_url": sector_data["app_url"],
                        "sector_thumb_url": sector_data["sector_thumb_url"],
                        "area_name": area_name,
                        "area_url": area_url,
                        "ascent_date": ascent_date,
                        "batch_id": batch_id,
                    }
                    async with DB_sends as db:
                        db.upsert(data, where("id") == unique_id)
                except Exception as ex:
                    print(f"tick-fetch failed with {ex}")
    else:
        print(f"error getting tick-list for {username}")
    # clear out those not updated in the batch
    async with DB_sends as db:
        db.remove((where("user_id") == username) & (where("batch_id") < batch_id))
    # clear simple sync lock
    async with DB_27cache as db:
        db.upsert(
            {"user_id_lock": username, "locked": False},
            where("user_id_lock") == username,
        )


async def refresh_27crags(usernames: list[str], trip_id: int = None, ticks=False):
    # async with DB_27cache as db:
    #     db.drop_tables()
    print("refreshing 27crags")
    async with httpx.AsyncClient(
        headers={"User-Agent": settings.httpx_user_agent}
    ) as client:
        if random.randint(0, 4) == 2:
            r = await client.get("https://27crags.com/robots.txt")
            if r.is_success:
                print("got robots.txt ok")
                print(r.content)
        for username in usernames:
            print(f"refreshing {username}")
            await refresh_todo_list(username=username, client=client, trip_id=trip_id)
            if ticks:
                await refresh_tick_list(username=username, client=client)
            print(f"done with {username}")


async def daily_resync():
    print("doing daily resync")
    async with DB_trips as db:
        usernames = set(
            [
                u["user_id"]
                for d in db.search(
                    where("date_to")
                    >= (datetime.utcnow() - timedelta(days=2)).isoformat()
                )
                for u in d["participants"]
            ]
        )
    await refresh_27crags(usernames=list(usernames), ticks=True)
