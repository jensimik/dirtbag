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
DB_users = AIOTinyDB(settings.db_file_users)
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
