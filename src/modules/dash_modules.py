import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import datetime


colors = {
    "background": "#111111",
    "text": "#7FDBFF",
}


def TextControl(pre_string, default_value, post_string, input_id):
    return html.Div(
        className="controls-line",
        children=[
            pre_string,
            dcc.Input(
                id=input_id,
                value=default_value,
            ),
            post_string,
        ],
    )


def DateRangeSlider(string, date_span, default_values):
    return html.Div(
        style={"margin-top": 10},
        children=[
            string,
            html.Div(
                children=[
                    date_span[0],
                    dcc.RangeSlider(
                        id="datetime_RangeSlider",
                        updatemode="mouseup",  # don't let it update till mouse released
                        min=date_span[0],
                        max=date_span[1],
                        value=default_values,
                    ),
                    date_span[1],
                ],
                style={
                    "display": "grid",
                    "grid-template-columns": "10% 80% 10%",
                    "margin-top": 5,
                },
            ),
        ],
    )


def LineGraph(element_id):
    return dcc.Graph(
        id=element_id,
        figure={
            "data": [],
            "layout": {
                "plot_bgcolor": colors["background"],
                "paper_bgcolor": colors["background"],
                "font": {"color": colors["text"]},
            },
        },
    )


def SingleStock():
    return html.Div(
        children=[
            "Single stock return: ",
            dcc.Input(
                id="ticker",
                value="IVV",
                type="text",
                style={
                    "backgroundColor": colors["background"],
                    "width": "50px",
                    "border": 0,
                    "color": colors["text"],
                    "font-size": "inherit",
                    "text-decoration": "underline",
                },
            ),
            dcc.Graph(
                id="Price_Graph",
                figure={
                    "data": [],
                    "layout": {
                        "plot_bgcolor": colors["background"],
                        "paper_bgcolor": colors["background"],
                        "font": {"color": colors["text"]},
                    },
                },
            ),
        ],
        style={"textAlign": "center", "color": colors["text"]},
    )
