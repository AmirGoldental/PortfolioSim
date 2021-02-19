import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output


# from FinScrapers import Alphavantage
# from FinScrapers import Bizportal
import YahooScraper
from dateutil.relativedelta import relativedelta


# data, _, _, _ = Alphavantage.getHistoricalData('IVV')
# data, _, _, _ = Bizportal.getHistoricalData('1115773')
_, IVV_df, _, _ = YahooScraper.getHistoricalStockData("IVV")
_, AGG_df, _, _ = YahooScraper.getHistoricalStockData("AGG")
app = dash.Dash(__name__, title="Portfolio Simulator")
server = app.server

colors = {"background": "#111111", "text": "#7FDBFF"}

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
        html.H1(
            children="Simulate your portfolio",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Div(
            children=[
                "US Bonds: ",
                dcc.Input(
                    id="AGG_percent",
                    value="30",
                    type="number",
                    style={
                        "backgroundColor": colors["background"],
                        "width": "50px",
                        "border": 0,
                        "color": colors["text"],
                        "font-size": "inherit",
                        "text-decoration": "underline",
                    },
                ),
                "%",
            ],
            style={
                "margin-left": "10%",
                "textAlign": "left",
                "font-size": "20px",
                "color": colors["text"],
            },
        ),
        html.Div(
            children=[
                "S&P 500: ",
                dcc.Input(
                    id="IVV_percent",
                    value="40",
                    type="number",
                    style={
                        "backgroundColor": colors["background"],
                        "width": "50px",
                        "border": 0,
                        "color": colors["text"],
                        "font-size": "inherit",
                        "text-decoration": "underline",
                    },
                ),
                "%",
            ],
            style={
                "margin-left": "10%",
                "textAlign": "left",
                "font-size": "20px",
                "color": colors["text"],
            },
        ),
        html.Div(
            children=[
                "USD: ",
                dcc.Input(
                    id="USD_percent",
                    value="0",
                    type="number",
                    style={
                        "backgroundColor": colors["background"],
                        "width": "50px",
                        "border": 0,
                        "color": colors["text"],
                        "font-size": "inherit",
                        "text-decoration": "underline",
                    },
                ),
                "%",
            ],
            style={
                "margin-left": "10%",
                "textAlign": "left",
                "font-size": "20px",
                "color": colors["text"],
            },
        ),
        html.Div(
            children=[
                dcc.RangeSlider(
                    id="datetime_RangeSlider",
                    updatemode="mouseup",  # don't let it update till mouse released
                    min=2006,
                    max=2021,
                    value=[2016, 2021],
                ),
            ],
            style={
                "margin-left": "10%",
                "margin-right": "10%",
                "textAlign": "left",
                "font-size": "20px",
                "color": colors["text"],
            },
        ),
        dcc.Graph(
            id="Porftfolio_Graph",
            figure={
                "data": [],
                "layout": {
                    "plot_bgcolor": colors["background"],
                    "paper_bgcolor": colors["background"],
                    "font": {"color": colors["text"]},
                },
            },
        ),
        html.Div(
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
            ],
            style={"textAlign": "center", "color": colors["text"]},
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
)


@app.callback(Output("Price_Graph", "figure"), [Input("ticker", "value")])
def update_figure(ticker):
    try:
        _, df, _, _ = YahooScraper.getHistoricalStockData(ticker)
    except:
        df = pd.DataFrame([])
    return {
        "data": [{"x": df.index, "y": df.values, "type": "line", "name": ticker}],
        "layout": {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
            "title": ticker,
        },
    }


@app.callback(
    Output("USD_percent", "value"), [Input("IVV_percent", "value"), Input("AGG_percent", "value")]
)
def update_USD_percent(IVV_percent, AGG_percent):
    if IVV_percent is None or AGG_percent is None:
        return 0
    USD_percent = 100 - int(IVV_percent) - int(AGG_percent)
    if USD_percent < 0:
        USD_percent = 0
    return USD_percent


@app.callback(
    Output("Porftfolio_Graph", "figure"),
    [Input("IVV_percent", "value"), Input("AGG_percent", "value"), Input("USD_percent", "value")],
)
def update_Porftfolio_Graph(IVV_percent, AGG_percent, USD_percent):
    return {
        "data": [
            {"x": IVV_df.index, "y": IVV_df.values, "type": "line", "name": "S&P 500"},
            {"x": AGG_df.index, "y": AGG_df.values, "type": "line", "name": "US Bonds"},
            {"x": AGG_df.index, "y": AGG_df.values * 0 + 100, "type": "line", "name": "USD"},
        ],
        "layout": {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
            "title": "Portfolio Simulation",
        },
    }


if __name__ == "__main__":
    app.run_server(debug=True, port=8051, host="0.0.0.0")
