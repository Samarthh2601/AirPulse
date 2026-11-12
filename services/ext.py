import pandas as pd


def get_aqi_category_color(aqi):

    if aqi <= 50:
        return "Good", "#00E400"

    elif aqi <= 100:
        return "Moderate", "#FFFF00"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#FF7E00"

    elif aqi <= 200:
        return "Unhealthy", "#FF0000"

    elif aqi <= 300:
        return "Very Unhealthy", "#8F3F97"

    else:
        return "Hazardous", "#7E0023"



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



import pandas as pd


def generate_insights(current_air, current_weather, forecast_df):

    insights = []

    forecast = forecast_df.copy()
    forecast["time"] = pd.to_datetime(forecast["time"])

    # Select next 24 forecast hours
    forecast = forecast.head(24).copy()
    forecast = forecast.dropna(subset=["us_aqi"])

    if forecast.empty:
        return insights

    # ==================================
    # AIR QUALITY INSIGHTS
    # ==================================

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
                "Forecast AQI is expected to remain close "
                "to the current reading."
            ),
            "type": "info"
        })

    # AQI peak and minimum
    max_aqi_row = forecast.loc[forecast["us_aqi"].idxmax()]
    min_aqi_row = forecast.loc[forecast["us_aqi"].idxmin()]

    worst_time = max_aqi_row["time"].strftime("%d %b %Y, %I:%M %p")
    best_time = min_aqi_row["time"].strftime("%d %b %Y, %I:%M %p")

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

    # ==================================
    # TEMPERATURE INSIGHTS
    # ==================================

    current_temp = current_weather["temperature_2m"]

    avg_temp = forecast["temperature_2m"].mean()
    min_temp = forecast["temperature_2m"].min()
    max_temp = forecast["temperature_2m"].max()

    temp_difference = avg_temp - current_temp

    if temp_difference >= 2:
        temp_message = "Temperatures are expected to rise."
    elif temp_difference <= -2:
        temp_message = "Temperatures are expected to fall."
    else:
        temp_message = "Temperatures are expected to remain relatively stable."

    insights.append({
        "title": "Temperature outlook",
        "description": (
            f"{temp_message} Current temperature is "
            f"{current_temp:.1f}°C, while the forecast average "
            f"is {avg_temp:.1f}°C. Expected range: "
            f"{min_temp:.1f}°C–{max_temp:.1f}°C."
        ),
        "type": "info"
    })

    # ==================================
    # HUMIDITY INSIGHTS
    # ==================================

    current_humidity = current_weather["relative_humidity_2m"]
    avg_humidity = forecast["relative_humidity_2m"].mean()

    humidity_difference = avg_humidity - current_humidity

    if humidity_difference > 5:
        humidity_message = "Humidity is expected to increase."
    elif humidity_difference < -5:
        humidity_message = "Humidity is expected to decrease."
    else:
        humidity_message = "Humidity is expected to remain relatively stable."

    insights.append({
        "title": "Humidity outlook",
        "description": (
            f"{humidity_message} Current humidity is "
            f"{current_humidity:.0f}%, compared with a forecast "
            f"average of {avg_humidity:.0f}%."
        ),
        "type": "info"
    })

    # ==================================
    # WIND INSIGHTS
    # ==================================

    current_wind = current_weather["wind_speed_10m"]
    avg_wind = forecast["wind_speed_10m"].mean()
    max_wind = forecast["wind_speed_10m"].max()

    wind_difference = avg_wind - current_wind

    if wind_difference > 2:
        wind_message = "Wind speeds are expected to increase."
    elif wind_difference < -2:
        wind_message = "Wind speeds are expected to decrease."
    else:
        wind_message = "Wind speeds are expected to remain relatively stable."

    insights.append({
        "title": "Wind conditions",
        "description": (
            f"{wind_message} Current wind speed is "
            f"{current_wind:.1f} km/h. Forecast average: "
            f"{avg_wind:.1f} km/h, with a maximum of "
            f"{max_wind:.1f} km/h."
        ),
        "type": "info"
    })

    # ==================================
    # PRECIPITATION INSIGHTS
    # ==================================

    current_rain = current_weather["precipitation"]
    total_rain = forecast["precipitation"].sum()

    if total_rain > 0:
        insights.append({
            "title": "Precipitation expected",
            "description": (
                f"Current precipitation is {current_rain:.1f} mm. "
                f"Approximately {total_rain:.1f} mm of precipitation "
                "is forecast over the next 24 hours."
            ),
            "type": "info"
        })
    else:
        insights.append({
            "title": "No significant precipitation expected",
            "description": (
                f"Current precipitation is {current_rain:.1f} mm, "
                "and no precipitation is forecast over the next 24 hours."
            ),
            "type": "info"
        })

    # ==================================
    # CLOUD COVER INSIGHTS
    # ==================================

    current_cloud = current_weather["cloud_cover"]
    avg_cloud = forecast["cloud_cover"].mean()

    cloud_difference = avg_cloud - current_cloud

    if cloud_difference > 10:
        cloud_message = "Cloud cover is expected to increase."
    elif cloud_difference < -10:
        cloud_message = "Cloud cover is expected to decrease."
    else:
        cloud_message = "Cloud cover is expected to remain relatively stable."

    insights.append({
        "title": "Cloud cover",
        "description": (
            f"{cloud_message} Current cloud cover is "
            f"{current_cloud:.0f}%, compared with a forecast "
            f"average of {avg_cloud:.0f}%."
        ),
        "type": "info"
    })

    return insights
