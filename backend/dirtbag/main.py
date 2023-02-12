import sentry_sdk
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .repeat_every_helper import repeat_every
from .c27_fetcher import refresh_27crags
from .config import settings
from dirtbag import __version__
from .routers import test

# from .routers import calendar, problems, webp, misc


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
app.mount("/static", StaticFiles(directory=settings.static_directory), name="static")

app.include_router(test.router)
# app.include_router(calendar.router)


# @app.on_event("startup")
# @repeat_every(seconds=60 * 60)
# async def _refresh_27crags():
#     await refresh_27crags()
