import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


def create_forecast_graph(df):

    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    fig = make_subplots(
        rows=4,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.065,
        subplot_titles=[
            "Air Quality",
            "Temperature",
            "Wind Conditions",
            "Precipitation"
        ]
    )

    # -------------------------
    # 1. AIR QUALITY
    # -------------------------

    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["pm2_5"],
            name="PM2.5",
            line=dict(color="#e76f51", width=2.5),
            hovertemplate="%{y:.1f} µg/m³<extra>PM2.5</extra>"
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["pm10"],
            name="PM10",
            line=dict(color="#e9c46a", width=2.5),
            hovertemplate="%{y:.1f} µg/m³<extra>PM10</extra>"
        ),
        row=1, col=1
    )

    # -------------------------
    # 2. TEMPERATURE
    # -------------------------

    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["temperature_2m"],
            name="Temperature",
            line=dict(color="#219ebc", width=2.5),
            hovertemplate="%{y:.1f} °C<extra>Temperature</extra>"
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["dew_point_2m"],
            name="Dew Point",
            line=dict(color="#8ecae6", width=2),
            hovertemplate="%{y:.1f} °C<extra>Dew Point</extra>"
        ),
        row=2, col=1
    )

    # -------------------------
    # 3. WIND
    # -------------------------

    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["wind_speed_10m"],
            name="Wind Speed",
            line=dict(color="#90a955", width=2.5),
            hovertemplate="%{y:.1f} km/h<extra>Wind Speed</extra>"
        ),
        row=3, col=1
    )

    # -------------------------
    # 4. PRECIPITATION
    # -------------------------

    fig.add_trace(
        go.Scatter(
            x=df["time"],
            y=df["precipitation"],
            name="Precipitation",
            mode="lines",
            line=dict(color="#2196d2", width=2),
            fill="tozeroy",
            fillcolor="rgba(33,150,210,0.30)",
            hovertemplate="%{y:.1f} mm<extra>Precipitation</extra>"
        ),
        row=4, col=1
    )

    # -------------------------
    # LAYOUT
    # -------------------------

    fig.update_layout(
        height=950,
        template="plotly_white",
        title=dict(
            text="Air Quality & Weather Forecast",
            x=0.02,
            font=dict(size=23)
        ),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=1.04,
            x=1,
            xanchor="right"
        ),
        margin=dict(l=65, r=35, t=110, b=50)
    )

    fig.update_yaxes(title_text="µg/m³", row=1, col=1)
    fig.update_yaxes(title_text="°C", row=2, col=1)
    fig.update_yaxes(title_text="km/h", row=3, col=1)
    fig.update_yaxes(title_text="mm", row=4, col=1)

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(150,150,150,0.15)",
        tickformat="%b %d\n%H:%M"
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(150,150,150,0.15)"
    )

    return fig
