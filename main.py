from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from get_predictions import get_current_json, get_preds_df

app = FastAPI(title="AirPulse")

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "city": "Ludhiana"
        }
    )



@app.get("/current")
def current(request: Request):

    air_quality_data, weather_data = get_current_json(30.9, 75.85)

    return templates.TemplateResponse(
        request=request,
        name="current.html",
        context={
            "city": "Kolkata",
            "air": air_quality_data,
            "weather": weather_data
        }
    )
