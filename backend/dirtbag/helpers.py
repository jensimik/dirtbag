import json
import pathlib
from functools import lru_cache
from itertools import cycle
from aiotinydb import AIOTinyDB
from tinydb import where
from tinydb.operations import set as tinydb_set
from .config import settings

# the database instances
DB_trips = AIOTinyDB(settings.db_file_trips)
DB_27cache = AIOTinyDB(settings.db_file_27cache)
DB_todos = AIOTinyDB(settings.db_file_todos)
DB_sends = AIOTinyDB(settings.db_file_sends)

MODULE_DIR = pathlib.Path(__file__).resolve().parent


@lru_cache
def get_crags():
    with open(MODULE_DIR / "all_crags.json", "r") as f:
        return {
            crag["name"]: (float(crag["latitude"]), float(crag["longitude"]))
            for crag in json.load(f)["crags"]
        }


# get location by sector name
def get_crag_location(sector_name):
    return get_crags().get(sector_name, (None, None))


# to sort things in reverse order
class reversor:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
        return other.obj < self.obj


yr_lookup = {
    "Fontainebleau": "2-3018074",
    "Albarracin": "2-3130679",
    "Alcañiz": "2-3130606",
    "Bohuslän": "2-2720857",
    "Lofoten": "1-543929",
    "Bodø": "1-269359",
    "Magic Wood": "2-2661670",
    "Göteborg": "2-2711537",
    "Kjugekull": "2-2700743",
    "Barcelona": "2-3128760",
    "Chironico": "2-2661171",
    "Rocklands": "2-3362340",
    "Västervik": "2-2664203",
    "Åland": "2-3041792",
}


def yr_data(area_name: str):
    svg_temp = "https://www.yr.no/nb/innhold/{id}/meteogram.svg"
    link_temp = "https://www.yr.no/nb/v%C3%A6rvarsel/daglig-tabell/{id})"
    if yr_id := yr_lookup.get(area_name, ""):
        return link_temp.format(id=yr_id), svg_temp.format(id=yr_id)
    return None, None
