import json
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
