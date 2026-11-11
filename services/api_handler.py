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
            "cloud_cover"
        ],
        "timezone": "Asia/Kolkata"
    }

    response = requests.get(WEATHER_URL, params=params, timeout=15)
    response.raise_for_status()

    return response.json()["current"]



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


def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"

def get_aqi_color(aqi):

    if aqi <= 50:
        return "#00E400"

    elif aqi <= 100:
        return "#FFFF00"

    elif aqi <= 150:
        return "#FF7E00"

    elif aqi <= 200:
        return "#FF0000"

    elif aqi <= 300:
        return "#8F3F97"

    else:
        return "#7E0023"



def get_forecast_summary(df, current_weather):

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])

    current_time = pd.to_datetime(current_weather["time"])

    next_24 = df[df["time"] >= current_time].head(24)

    if next_24.empty:
        next_24 = df.tail(24)

    next_24 = next_24.dropna(subset=["us_aqi"])

    average_columns = [
        "us_aqi",
        "pm2_5",
        "pm10",
        "carbon_monoxide",
        "nitrogen_dioxide",
        "sulphur_dioxide",
        "ozone",
        "ammonia",
        "temperature_2m",
        "relative_humidity_2m",
        "dew_point_2m",
        "wind_speed_10m",
        "pressure_msl",
        "cloud_cover",
        "boundary_layer_height",
        "shortwave_radiation"
    ]

    summary = {}

    for col in average_columns:
        if col in next_24.columns:
            summary[col] = round(next_24[col].mean(), 1)

    summary["aqi_min"] = next_24["us_aqi"].min()
    summary["aqi_max"] = next_24["us_aqi"].max()

    summary["max_temperature"] = next_24["temperature_2m"].max()
    summary["min_temperature"] = next_24["temperature_2m"].min()

    # Total rainfall over the selected period
    summary["total_precipitation"] = round(
        next_24["precipitation"].sum(), 1
    )

    # Maximum wind speed
    summary["max_wind_speed"] = next_24["wind_speed_10m"].max()

    # Times of minimum and maximum AQI
    summary["best_aqi_time"] = next_24.loc[
        next_24["us_aqi"].idxmin(), "time"
    ]

    summary["worst_aqi_time"] = next_24.loc[
        next_24["us_aqi"].idxmax(), "time"
    ]

    return summary, next_24





from datetime import datetime


def generate_insights(current_air, current_weather, forecast_df):

    insights = []

    # Select next 24 forecast hours
    forecast = forecast_df.copy()
    forecast["time"] = datetime_format = __import__("pandas").to_datetime(
        forecast["time"]
    )

    forecast = forecast.head(24).copy()
    forecast = forecast.dropna(subset=["us_aqi"])

    if forecast.empty:
        return insight
    current_aqi = current_air["us_aqi"]
    avg_aqi = forecast["us_aqi"].mean()

    difference = avg_aqi - current_aqi

    if difference < -5:
        insights.append({
            "title": "Air quality is expected to improve",
            "description": (
                f"Average AQI may decrease by "
                f"{abs(difference):.0f} points "
                "over the next 24 hours."
            ),
            "type": "success"
        })

    elif difference > 5:
        insights.append({
            "title": "Air quality may deteriorate",
            "description": (
                f"Average AQI may increase by "
                f"{difference:.0f} points "
                "over the next 24 hours."
            ),
            "type": "warning"
        })

    else:
        insights.append({
            "title": "Air quality is expected to remain stable",
            "description": (
                "The forecast average AQI is close "
                "to the current reading."
            ),
            "type": "info"
        })

    max_aqi_row = forecast.loc[forecast["us_aqi"].idxmax()]
    min_aqi_row = forecast.loc[forecast["us_aqi"].idxmin()]

    worst_time = datetime.fromisoformat(
        str(max_aqi_row["time"])
    ).strftime("%d %b %Y, %I:%M %p")

    best_time = datetime.fromisoformat(
        str(min_aqi_row["time"])
    ).strftime("%d %b %Y, %I:%M %p")

    insights.append({
        "title": "Expected AQI peak",
        "description": (
            f"AQI may reach {max_aqi_row['us_aqi']:.0f} "
            f"around {worst_time}."
        ),
        "type": "warning"
    })

    insights.append({
        "title": "Best expected air quality",
        "description": (
            f"The lowest forecast AQI is "
            f"{min_aqi_row['us_aqi']:.0f}, "
            f"around {best_time}."
        ),
        "type": "success"
    })


    min_temp = forecast["temperature_2m"].min()
    max_temp = forecast["temperature_2m"].max()

    insights.append({
        "title": "Temperature outlook",
        "description": (
            f"Temperature is expected to range "
            f"between {min_temp:.1f}°C and "
            f"{max_temp:.1f}°C."
        ),
        "type": "info"
    })

    total_rain = forecast["precipitation"].sum()

    if total_rain > 0:
        insights.append({
            "title": "Precipitation expected",
            "description": (
                f"Approximately {total_rain:.1f} mm "
                "of precipitation is forecast "
                "over the next 24 hours."
            ),
            "type": "info"
        })

    # -------------------------
    # WIND CONDITIONS
    # -------------------------

    max_wind = forecast["wind_speed_10m"].max()

    insights.append({
        "title": "Wind conditions",
        "description": (
            f"Wind speeds may reach {max_wind:.1f} km/h "
            "during the forecast period."
        ),
        "type": "info"
    })

    return insights
