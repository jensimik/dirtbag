from typing import Any
from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable
from pathlib import Path
from dateutil.tz import tzfile, gettz


class Settings(BaseSettings):
    app_name: str = "Dirtbag"
    cors_origins: list = [
        "http://localhost:5173",
        "http://192.168.1.44:5173",
        "https://dirtbag.gnerd.dk",
    ]
    static_directory: Path = "/static"
    db_file_trips: Path = "/tmp/trips.json"
    db_file_27cache: Path = "/tmp/27cache.json"
    db_file_users: Path = "/tmp/users.json"
    db_file_todos: Path = "/tmp/todos.json"
    db_file_sends: Path = "/tmp/sends.json"
    sentry_dsn: str = None
    tz: tzfile = gettz("Europe/Copenhagen")

    class Config:
        # parse tz field as a dateutil.tz
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == "tz":
                return gettz(raw_val)
            return cls.json_loads(raw_val)

        # do not try to load from file
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings


settings = Settings()
