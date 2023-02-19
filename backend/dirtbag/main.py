import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dirtbag.repeat_every_helper import repeat_every
from .config import settings
from dirtbag import __version__
from .routers import trips, users, weather


if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
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
app.include_router(weather.router)

@app.get("/healtz")
async def healtz():
    return {"everything": "is awesome"}


@app.on_event("startup")
@repeat_every(seconds=60 * 60 * 24)
async def _maintenance():
    # todo clear out old trips automatic after trip is done?
    print("doing maintenance stuff")
