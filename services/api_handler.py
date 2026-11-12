import requests
import pandas as pd
from datetime import datetime

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_air_quality(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,

        "hourly": [
            "pm2_5",
            "pm10",
            "carbon_monoxide",
            "carbon_dioxide",
            "nitrogen_dioxide",
            "sulphur_dioxide",
            "ozone",
            "ammonia",
            "us_aqi",
        ],

        "forecast_days": 3,
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(AIR_QUALITY_URL, params=params)
    response.raise_for_status()

    return pd.DataFrame(response.json()["hourly"])


def fetch_weather(latitude, longitude):


    params = {
        "latitude": latitude,
        "longitude": longitude,

        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "pressure_msl",
            "cloud_cover",
            "boundary_layer_height",
            "shortwave_radiation"
        ],
        "daily": "apparent_temperature_max",

        "forecast_days": 3,
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(WEATHER_URL, params=params)
    response.raise_for_status()

    return pd.DataFrame(response.json()["hourly"])


def get_current_aqi(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "pm2_5,pm10,us_aqi,carbon_monoxide,nitrogen_dioxide,ozone,sulphur_dioxide",
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(AIR_QUALITY_URL, params=params, timeout=15)
    response.raise_for_status()

    data = response.json()

    if "current" not in data:
        print("API Response:", data)
        return None

    return data["current"]

def get_current_weather(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
            "pressure_msl",
            "cloud_cover",
            "dew_point_2m"
        ],
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(WEATHER_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()["current"]

    data["time"] = datetime.fromisoformat(data["time"]).strftime("%d %b %Y, %I:%M %p")

    return data



#returns 3 days worth of predictions
def get_preds_df(latitude, longitude): 
    aq_df = fetch_air_quality(latitude, longitude)
    weather_df = fetch_weather(latitude, longitude)

    return pd.merge(
        aq_df,
        weather_df,
        on="time"
    )

def get_current_json(latitude, longitude):
    return get_current_aqi(latitude, longitude), get_current_weather(latitude, longitude),
