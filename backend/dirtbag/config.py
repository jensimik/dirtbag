from pathlib import Path
from typing import Any, Tuple, Type

from dateutil.tz import gettz, tzfile
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
)


class MyCustomSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "tz":
            return gettz(value)
        elif field_name == "admin_user_ids":
            if value:
                return [int(v) for v in value.split()]
        return value


class Settings(BaseSettings):
    app_name: str = "Dirtbag"
    cors_origins: list = [
        "http://localhost:5173",
        "http://192.168.1.44:5173",
        "https://dirtbag.gnerd.dk",
        "https://dirtbag.dk",
    ]
    db_file_trips: Path = "/data/trips.json"
    db_file_27cache: Path = "/data/27cache.json"
    db_file_todos: Path = "/data/todos.json"
    db_file_sends: Path = "/data/sends.json"
    weather_directory: Path = "/data/"
    sentry_dsn: str = None
    httpx_user_agent: str = "dirtbag.dk wise.coffee2409@gnerd.dk"
    tz: tzfile = gettz("Europe/Copenhagen")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (MyCustomSource(settings_cls),)


settings = Settings()
