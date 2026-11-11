from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from services import get_current_json, get_preds_df, get_aqi_category_color, create_forecast_graph, create_aqi_forecast_graph,  generate_insights, get_forecast_summary, get_coords, CITIES
import plotly.io as pio


app = FastAPI(title="AirPulse")

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


def get_template_context(request: Request, context=None):

    city = request.cookies.get("selected_city", CITIES[0])

    if city not in CITIES:
        city = CITIES[0]

    return {
        "request": request,
        "cities": CITIES,
        "selected_city": city,
        **(context or {})
    }


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context=get_template_context(request, {})
    )



@app.get("/current")
def current(request: Request):
    city = request.cookies.get(
        "selected_city",
        "Ludhiana"
    )

    lat, lng = get_coords(city)

    air_quality_data, weather_data = get_current_json(lat, lng)
    
    current_aqi = int(air_quality_data["us_aqi"])
    aqi_category, aqi_color = get_aqi_category_color(current_aqi)

    return templates.TemplateResponse(
        request=request,
        name="current.html",
        context=get_template_context(request, {
            "city": city,
            "air": air_quality_data,
            "weather": weather_data,
            "current_aqi": current_aqi,
            "aqi_category": aqi_category,
            "aqi_color": aqi_color,
        })
    )

@app.get("/forecast")
async def forecast(request: Request):

    city = request.cookies.get(
            "selected_city",
            "Ludhiana"
        )
    
    lat, lng = get_coords(city)

    df = get_preds_df(lat, lng)

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
        context=get_template_context(request, {
            "graph_html": graph_html,
            "weather_summary": weather_summary
        })
    )


@app.get("/compare/forecast")
async def compare_forecast(request: Request):

    city = request.cookies.get("selected_city", CITIES[0])

    lat, lng = get_coords(city)


    current_air, current_weather = get_current_json(lat, lng)


    forecast_df = get_preds_df(lat, lng)

    forecast_summary, next_24 = get_forecast_summary(
        forecast_df,
        current_weather
    )

    fig = create_aqi_forecast_graph(next_24)

    graph_html = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn"
    )

    insights = generate_insights(
    current_air,
    current_weather,
    forecast_df)

    return templates.TemplateResponse(
        request=request,
        name="compare_forecast.html",
        context=get_template_context(
            request,
            {
                "city": city,
                "current_air": current_air,
                "current_weather": current_weather,
                "forecast": forecast_summary,
                "graph_html": graph_html,
                "insights": insights,
            }
        )
    )

@app.post("/set-city")
async def set_city(
    request: Request,
    city: str = Form(...),
    next: str = Form("/")
):
    if city not in CITIES:
        city = CITIES[0]

    response = RedirectResponse(
        url=next if next.startswith("/") and not next.startswith("//") else "/",
        status_code=303
    )

    response.set_cookie(
        key="selected_city",
        value=city,
        max_age=60 * 60 * 24 * 30,
        httponly=True,
        samesite="lax"
    )

    return response