import pandas as pd

def get_pollution_actions(current_air: dict, forecast_df: pd.DataFrame):

    aqi = current_air.get("us_aqi")

    pm25 = current_air.get("pm2_5")
    pm10 = current_air.get("pm10")

    if aqi is None:
        return {
            "category": "Unavailable",
            "color": "#808080",
            "level": "Data unavailable",
            "individual": [],
            "community": [],
            "authority": [],
            "alerts": []
        }


    if aqi <= 50:
        category = "Good"
        color = "#00E400"
        level = "Air quality is satisfactory."

    elif aqi <= 100:
        category = "Moderate"
        color = "#FFFF00"
        level = "Air quality is generally acceptable."

    elif aqi <= 150:
        category = "Unhealthy for Sensitive Groups"
        color = "#FF7E00"
        level = "Sensitive groups may experience health effects."

    elif aqi <= 200:
        category = "Unhealthy"
        color = "#FF0000"
        level = "Everyone may begin to experience health effects."

    elif aqi <= 300:
        category = "Very Unhealthy"
        color = "#8F3F97"
        level = "Health alert: increased risk for everyone."

    else:
        category = "Hazardous"
        color = "#7E0023"
        level = "Health warning: everyone may experience serious effects."

    individual = []
    community = []
    authority = []
    alerts = []


    if aqi <= 50:
        individual.append(
            "Air quality is good. Normal outdoor activities can continue."
        )

    elif aqi <= 100:
        individual.append(
            "Most people can continue normal outdoor activities. "
            "Unusually sensitive individuals should monitor symptoms."
        )

    elif aqi <= 150:
        individual.extend([
            "Children, older adults and people with heart or lung "
            "conditions should reduce prolonged or strenuous outdoor activity.",
            "Consider indoor alternatives if you are particularly sensitive "
            "to air pollution."
        ])

    elif aqi <= 200:
        individual.extend([
            "Reduce prolonged or strenuous outdoor physical activity.",
            "Consider moving exercise indoors or rescheduling it.",
            "People with respiratory or cardiovascular conditions should "
            "follow their healthcare professional's advice."
        ])

    elif aqi <= 300:
        individual.extend([
            "Avoid prolonged outdoor physical exertion.",
            "Reduce outdoor exposure as much as possible.",
            "Keep windows closed when outdoor air is polluted, if indoor "
            "conditions remain comfortable, and use suitable indoor filtration "
            "if available."
        ])

    else:
        individual.extend([
            "Avoid outdoor physical activity.",
            "Stay indoors in a cleaner-air environment where possible.",
            "Follow local health advisories and seek medical advice "
            "if you experience concerning symptoms."
        ])


    community.extend([
        "Encourage public transport, carpooling, cycling and fewer "
        "unnecessary vehicle trips.",
        "Avoid burning household waste, leaves or other open materials."
    ])

    if aqi > 100:
        community.append(
            "Share local air-quality advisories and encourage people "
            "to reduce avoidable outdoor exposure."
        )

    if pm25 is not None and pm25 > 35.4:
        community.append(
            "Promote awareness about fine-particle pollution and "
            "ways to reduce exposure."
        )

    if pm10 is not None and pm10 > 154:
        community.append(
            "Encourage dust-control practices at construction sites "
            "and along dusty roads."
        )

    authority.extend([
        "Review local air-quality monitoring data and investigate "
        "recurring pollution episodes.",
        "Encourage compliance with industrial emission standards."
    ])

    if pm10 is not None and pm10 > 154:
        authority.append(
            "Prioritise construction-site dust inspections, road-dust "
            "management and covered transport of loose materials."
        )

    if pm25 is not None and pm25 > 35.4:
        authority.append(
            "Investigate possible fine-particle sources using local "
            "monitoring and emissions information."
        )

    if aqi > 150:
        authority.append(
            "Coordinate public advisories and review applicable "
            "pollution-control response measures."
        )


    if forecast_df is not None and not forecast_df.empty:

        forecast = forecast_df.copy()

        if "us_aqi" in forecast.columns:

            forecast["us_aqi"] = (
                pd.to_numeric(
                    forecast["us_aqi"],
                    errors="coerce"
                )
            )

            valid_aqi = forecast.dropna(subset=["us_aqi"])

            if not valid_aqi.empty:

                peak_aqi = valid_aqi["us_aqi"].max()
                average_aqi = valid_aqi["us_aqi"].mean()

                if peak_aqi > aqi + 20:
                    alerts.append({
                        "title": "Pollution may increase",
                        "description": (
                            f"Forecast AQI may reach {peak_aqi:.0f}, "
                            f"compared with the current AQI of {aqi:.0f}."
                        ),
                        "type": "warning"
                    })

                elif peak_aqi <= aqi - 20:
                    alerts.append({
                        "title": "Air quality may improve",
                        "description": (
                            f"Forecast peak AQI is {peak_aqi:.0f}, "
                            f"below the current AQI of {aqi:.0f}."
                        ),
                        "type": "success"
                    })

                else:
                    alerts.append({
                        "title": "Monitor upcoming conditions",
                        "description": (
                            f"The forecast average AQI is "
                            f"{average_aqi:.0f}, with a peak of "
                            f"{peak_aqi:.0f}."
                        ),
                        "type": "info"
                    })

    return {
        "aqi": aqi,
        "category": category,
        "color": color,
        "level": level,
        "individual": individual,
        "community": community,
        "authority": authority,
        "alerts": alerts
    }
