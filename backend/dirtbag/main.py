import sentry_sdk
from dirtbag.repeat_every_helper import repeat_every
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dirtbag import __version__

from .c27_fetcher import daily_resync
from .config import settings
from .helpers import DB_27cache, DB_sends, DB_todos, where
from .routers import trips, users

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=0,
        release=__version__,
    )

app = FastAPI(
    title="dirtbag-api",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex="https://dirtbag-pr-.*\.onrender\.com",  # allow onrender.com pull-requests
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips.router)
app.include_router(users.router)


@app.get("/healtz")
async def healtz():
    return {"everything": "is awesome"}


@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 12)
async def _maintenance():
    # todo clear out old trips automatic after trip is done?
    print("doing maintenance stuff")
    await daily_resync()


@app.get("/fixup")
async def fixup():
    async with DB_todos as db:
        db.delete(where("name") == "")
    async with DB_sends as db:
        db.delete(where("name") == "")
