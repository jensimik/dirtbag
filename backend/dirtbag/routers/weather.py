from fastapi import APIRouter, Request, HTTPException, status
from datetime import datetime, date
from dirtbag import schemas
from metno_locationforecast import Place, Forecast
from dirtbag.helpers import get_crag_location
from dirtbag.config import settings

router = APIRouter(tags=["weather"])


@router.get("/sector/{sector_name}/forecast")
def sector_forecast(sector_name: str):
    latitute, longitude = get_crag_location(sector_name)
    sector_place = Place(sector_name, latitute, longitude)
    forecast = Forecast(sector_place, "dirtbag.gnerd.dk jens@gnerd.dk", save_location="/data/")
    forecast.update()
    return {
        "x": [i.start_time for i in forecast.data.intervals][:48],
        "temperature": [
            i.variables["air_temperature"].value for i in forecast.data.intervals
        ][:48],
        "precipitation": [
            i.variables["precipitation_amount"].value
            if "precipitation_amount" in i.variables
            else 0
            for i in forecast.data.intervals
        ][:48],
    }
