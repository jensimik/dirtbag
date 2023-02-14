import httpx
import hashlib
import random
from urllib.parse import urlparse
from aiolimiter import AsyncLimiter
from requests_html import HTML
from datetime import datetime
from .helpers import DB_27cache, DB_todos, DB_users, DB_trips, where, tinydb_set
from .config import settings

rate_limit = AsyncLimiter(1, 15)


def get_app_argument_from_html(html) -> str:
    meta_content = html.find("meta[name='apple-itunes-app']", first=True).attrs[
        "content"
    ]
    return meta_content.split("app-argument=")[1]


async def get_problem_data(problem_url: str, client: httpx.AsyncClient) -> str:
    async with DB_27cache as db:
        data = db.get(where("problem_url") == problem_url)
    if data:
        return data["app_argument"]
    # be gentle with 27crags
    await rate_limit.acquire()
    r = await client.get(problem_url)
    if r.is_success:
        # to get big image and canvas markup i have to be logged in for premium sites
        app_argument = get_app_argument_from_html(html=HTML(html=r.content))
    async with DB_27cache as db:
        data = db.upsert(
            {"problem_url": problem_url, "app_argument": app_argument},
            where("problem_url") == problem_url,
        )
    return app_argument


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
        crag_location = html.find("h2.craglocation", first=True)
        ass = crag_location.find("a")
        if "in the area of" in ass[0].text:
            area_url = "https://27crags.com" + ass[0].attrs["href"]
            area_name = ass[0].text.replace("in the area of ", "").split(",")[0]
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
        todo_list = html.find("table.todo-list tbody", first=True)
        for tr in todo_list.find("tr"):
            tds = tr.find("td.stxt")
            grade = tr.find("td.grade", first=True).text
            img_element = tr.find("img", first=True)
            thumb_url = img_element.attrs["src"] if img_element else ""
            ass = tr.find("td.stxt > a")
            url = "https://27crags.com" + ass[1].attrs["href"]
            app_url = await get_problem_data(problem_url=url, client=client)
            name = ass[1].text
            comment = []
            if ascent_details := tr.find("td.stxt > div.ascent-details", first=True):
                for link in ascent_details.find("a"):
                    url = link.attrs["href"]
                    o = urlparse(url)
                    comment.append({"type": "link", "url": url, "text": o.hostname})
                if not comment:
                    comment = [{"type": "text", "text": ascent_details.text}]
            sector_url = (
                "https://27crags.com" + tds[1].find("a", first=True).attrs["href"]
            )
            sector_name = tds[1].text
            sector_data = await get_sector_data(sector_url=sector_url, client=client)
            unique_id = hashlib.md5(str.encode(f"{username}-{app_url}")).hexdigest()
            area_name = (
                sector_data["area_name"] if sector_data["area_name"] else sector_name
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


async def refresh_27crags(usernames: list[str], trip_id: int = None):
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
            print(f"done with {username}")
