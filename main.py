from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from services import get_current_json, get_preds_df, get_aqi_category, create_forecast_graph
import plotly.io as pio


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
    current_aqi = int(air_quality_data["us_aqi"])
    aqi_category = get_aqi_category(current_aqi)


    return templates.TemplateResponse(
        request=request,
        name="current.html",
        context={
            "city": "Kolkata",
            "air": air_quality_data,
            "weather": weather_data,
            "current_aqi": current_aqi,
            "aqi_category": aqi_category,
        }
    )

@app.get("/forecast")
async def forecast(request: Request):

    df = get_preds_df(22.5675, 88.3700)

    # Create graph
    fig = create_forecast_graph(df)

    graph_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn"
    )

    # Weather summary cards
    weather_summary = {
        "Humidity": f"{df['relative_humidity_2m'].iloc[0]}%",
        "Pressure": f"{df['pressure_msl'].iloc[0]} hPa",
        "Cloud Cover": f"{df['cloud_cover'].iloc[0]}%",
        "Boundary Layer": f"{df['boundary_layer_height'].iloc[0]} m",
        "Shortwave Radiation": f"{df['shortwave_radiation'].iloc[0]} W/m²",
    }

    return templates.TemplateResponse(
        request=request,
        name="forecast.html",
        context={
            "graph_html": graph_html,
            "weather_summary": weather_summary
        }
    )