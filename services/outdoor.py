import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo


def get_outdoor_recommendations(forecast_df, hours=48):

    if forecast_df is None or forecast_df.empty:
        return {
            "best_window": None,
            "alternatives": [],
            "hourly_data": [],
            "message": "Forecast data is unavailable."
        }

    df = forecast_df.copy()

    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Keep only future forecast hours
    now = datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)

    df = (
        df.dropna(subset=["time"])
        .sort_values("time")
    )

    df = df[df["time"] > now].head(hours).copy()

    if df.empty or "us_aqi" not in df.columns:
        return {
            "best_window": None,
            "alternatives": [],
            "hourly_data": [],
            "message": "No upcoming AQI forecast is available."
        }

    # Convert relevant columns to numeric
    columns = [
        "us_aqi",
        "temperature_2m",
        "precipitation",
        "wind_speed_10m"
    ]

    for column in columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["us_aqi"]).copy()

    if df.empty:
        return {
            "best_window": None,
            "alternatives": [],
            "hourly_data": [],
            "message": "AQI forecast values are unavailable."
        }

    # AQI scoring
    def aqi_score(aqi):
        if aqi <= 50:
            return 100
        elif aqi <= 100:
            return 75
        elif aqi <= 150:
            return 45
        elif aqi <= 200:
            return 20
        elif aqi <= 300:
            return 5
        return 0

    # Temperature scoring
    def temperature_score(temp):
        if pd.isna(temp):
            return 50

        if 18 <= temp <= 28:
            return 100
        elif 15 <= temp < 18 or 28 < temp <= 32:
            return 75
        elif 10 <= temp < 15 or 32 < temp <= 36:
            return 40

        return 15

    # Precipitation scoring
    def precipitation_score(rain):
        if pd.isna(rain):
            return 50

        if rain <= 0:
            return 100
        elif rain <= 0.5:
            return 75
        elif rain <= 2:
            return 40

        return 10

    # Wind scoring
    def wind_score(wind):
        if pd.isna(wind):
            return 50

        if wind <= 20:
            return 100
        elif wind <= 30:
            return 70
        elif wind <= 40:
            return 40

        return 15

    # Calculate suitability score
    def get_optional_column(column):
        if column in df.columns:
            return df[column]
        return pd.Series(float("nan"), index=df.index)

    df["score"] = (
        df["us_aqi"].apply(aqi_score) * 0.70
        + get_optional_column("temperature_2m")
            .apply(temperature_score) * 0.15
        + get_optional_column("precipitation")
            .apply(precipitation_score) * 0.10
        + get_optional_column("wind_speed_10m")
            .apply(wind_score) * 0.05
    ).round(1)

    df["suitable"] = df["score"] >= 55

    # Find consecutive suitable windows
    windows = []
    current_window = []

    for _, row in df.iterrows():

        if current_window:
            previous_time = current_window[-1]["time"]

            # Split if there is a gap in hourly forecast data
            if row["time"] - previous_time != pd.Timedelta(hours=1):
                windows.append(current_window)
                current_window = []

        if row["suitable"]:
            current_window.append(row)

        else:
            if current_window:
                windows.append(current_window)
                current_window = []

    if current_window:
        windows.append(current_window)

    # Generate window summaries
    results = []

    for window in windows:

        window_df = pd.DataFrame(window)

        # Split long windows into maximum 4-hour blocks
        for start_index in range(0, len(window_df), 4):

            block = window_df.iloc[start_index:start_index + 4]

            if block.empty:
                continue

            start = block["time"].iloc[0]

            # End time is one hour after the final included forecast hour
            end = block["time"].iloc[-1] + pd.Timedelta(hours=1)

            avg_aqi = round(block["us_aqi"].mean())
            avg_score = round(block["score"].mean(), 1)

            reasons = []

            if avg_aqi <= 50:
                reasons.append("Good AQI conditions")
            elif avg_aqi <= 100:
                reasons.append("Moderate AQI conditions")

            if "temperature_2m" in block:
                avg_temp = block["temperature_2m"].mean()

                if pd.notna(avg_temp) and 18 <= avg_temp <= 28:
                    reasons.append("Comfortable temperature")

            if "precipitation" in block:
                max_rain = block["precipitation"].max()

                if pd.notna(max_rain) and max_rain == 0:
                    reasons.append("No precipitation expected")

            results.append({
                "start": start.strftime("%d %b, %I:%M %p"),
                "end": end.strftime("%d %b, %I:%M %p"),
                "start_time": start,
                "end_time": end,
                "avg_aqi": avg_aqi,
                "avg_score": avg_score,
                "reasons": reasons
            })

    # Rank best windows first
    results.sort(
        key=lambda item: item["avg_score"],
        reverse=True
    )

    best_window = results[0] if results else None
    alternatives = results[1:4] if results else []

    # Prepare hourly data for template
    hourly_data = []

    for _, row in df.iterrows():

        hourly_data.append({
            "time": row["time"].strftime("%d %b, %I:%M %p"),
            "aqi": round(row["us_aqi"]),
            "score": row["score"],

            "temperature": (
                round(row["temperature_2m"], 1)
                if pd.notna(row.get("temperature_2m"))
                else None
            ),

            "precipitation": (
                round(row["precipitation"], 1)
                if pd.notna(row.get("precipitation"))
                else None
            )
        })

    return {
        "best_window": best_window,
        "alternatives": alternatives,
        "hourly_data": hourly_data,
        "message": (
            "No suitable outdoor window was found in the next 48 hours."
            if not best_window else None
        )
    }
