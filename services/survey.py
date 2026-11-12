from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


CSV_PATH = Path(__file__).resolve().parent.parent / "survey.csv"

QUESTION_CONFIG = [
    {
        "column": "How frequently do you experience problems that you associate with air pollution?",
        "title": "Experiences with Air Pollution",
        "description": "How frequently respondents experience problems associated with air pollution."
    },
    {
        "column": "Which of the following affects you the most during periods of poor air quality?",
        "title": "Effects of Poor Air Quality",
        "description": "The most commonly reported effects during periods of poor air quality."
    },
    {
        "column": "How often do you check the air quality (AQI) before going outdoors?",
        "title": "AQI Awareness",
        "description": "How frequently respondents check AQI before going outdoors."
    },
    {
        "column": "Which feature would be most useful to you in an air-quality monitoring platform like AirPulse?",
        "title": "Preferred AirPulse Features",
        "description": "Which features respondents would find most useful."
    }
]


def analyse_survey(file_path=CSV_PATH):

    file_path = Path(file_path)

    if not file_path.exists():
        return {
            "error": "Survey CSV file not found.",
            "total_responses": 0,
            "charts": [],
            "insights": []
        }

    df = pd.read_csv(file_path, encoding="utf-8-sig")
    df = df.dropna(how="all")

    if df.empty:
        return {
            "error": "No survey responses found.",
            "total_responses": 0,
            "charts": [],
            "insights": []
        }

    total_responses = len(df)

    timestamp_col = "Timestamp"
    survey_period = "Not available"

    if timestamp_col in df.columns:
        timestamps = pd.to_datetime(
            df[timestamp_col],
            errors="coerce",
            dayfirst=True
        ).dropna()

        if not timestamps.empty:
            start = timestamps.min().strftime("%d %b %Y")
            end = timestamps.max().strftime("%d %b %Y")

            survey_period = (
                start if start == end else f"{start} – {end}"
            )

    charts = []
    insights = []
    question_stats = []

    answered_counts = []

    for question in QUESTION_CONFIG:

        column = question["column"]

        if column not in df.columns:
            continue

        answers = (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        answers = answers[answers != ""]

        if answers.empty:
            continue

        counts = answers.value_counts()
        percentages = (
            counts / len(answers) * 100
        ).round(1)

        labels = counts.index.tolist()
        values = counts.tolist()
        percentage_values = percentages.tolist()

        answered_counts.append(len(answers))

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=values,
                y=labels,
                orientation="h",
                text=[
                    f"{count} ({percentage}%)"
                    for count, percentage in zip(
                        values, percentage_values
                    )
                ],
                textposition="auto",
                marker=dict(
                    color="#2695d6",
                    line=dict(width=0)
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Responses: %{x}<br>"
                    "Percentage: %{customdata}%"
                    "<extra></extra>"
                ),
                customdata=percentage_values
            )
        )

        fig.update_layout(
            height=max(300, len(labels) * 55 + 100),
            margin=dict(l=10, r=25, t=15, b=45),
            xaxis_title="Number of responses",
            yaxis_title="",
            yaxis=dict(autorange="reversed"),
            template="plotly_white",
            font=dict(family="Arial", size=12),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        charts.append({
            "title": question["title"],
            "description": question["description"],
            "response_count": len(answers),
            "graph_html": fig.to_html(
                full_html=False,
                include_plotlyjs=False,
                config={
                    "responsive": True,
                    "displayModeBar": False
                }
            )
        })

        top_answer = counts.index[0]
        top_count = int(counts.iloc[0])
        top_percentage = round(
            top_count / len(answers) * 100, 1
        )

        insights.append({
            "title": question["title"],
            "answer": top_answer,
            "count": top_count,
            "percentage": top_percentage
        })

        question_stats.append({
            "title": question["title"],
            "total": len(answers),
            "top_answer": top_answer,
            "top_percentage": top_percentage
        })

    total_answered = sum(answered_counts)
    possible_answers = total_responses * len(QUESTION_CONFIG)

    completion_rate = (
        round(total_answered / possible_answers * 100, 1)
        if possible_answers else 0
    )

    return {
        "error": None,
        "total_responses": total_responses,
        "total_questions": len(QUESTION_CONFIG),
        "survey_period": survey_period,
        "completion_rate": completion_rate,
        "total_answers": total_answered,
        "charts": charts,
        "insights": insights,
        "question_stats": question_stats
    }
