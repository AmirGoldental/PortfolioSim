import numpy as np
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import datetime

from .modules import yahoo_scraper, dash_modules, utils

_, IVV_df, _, _ = yahoo_scraper.getHistoricalStockData("IVV")
_, AGG_df, _, _ = yahoo_scraper.getHistoricalStockData("AGG")
app = dash.Dash(__name__, title="Portfolio Simulator")
server = app.server

colors = {
    "background": "#111111",
    "text": "#7FDBFF",
}

controls_div = html.Div(
    className="controls",
    children=[
        dash_modules.TextControl("US bonds: ", 30, "%", "AGG_percent"),
        dash_modules.TextControl("S&P 500: ", 40, "%", "IVV_percent"),
        dash_modules.TextControl("USD: ", 0, "%", "USD_percent"),
        html.Br(),
        dash_modules.TextControl("Rebalance every ", 4, "months", "rebelance_preiod"),
        dash_modules.DateRangeSlider("Date range:", [2006, 2021], [2016, 2020]),
    ],
)


app.layout = html.Div(
    className="dash-main",
    children=[
        html.H1(["Passive Investment", html.Br(), "Portfolio Simuation"]),
        controls_div,
        dash_modules.LineGraph("PorftfolioGraph"),
        dash_modules.LineGraph("stacked_graph"),
        dash_modules.SingleStock(),
    ],
)


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
    Output("datetime_RangeSlider", "marks"),
    Input("datetime_RangeSlider", "value"),
)
def update_datetime_RangeSlider_marks(values):
    style_dict = {"font-size": 20}
    return {
        values[0]: {"label": str(values[0]), "style": style_dict},
        values[1]: {"label": str(values[1]), "style": style_dict},
    }


@app.callback(
    Output("PorftfolioGraph", "figure"),
    [
        Input("IVV_percent", "value"),
        Input("AGG_percent", "value"),
        Input("USD_percent", "value"),
        Input("datetime_RangeSlider", "value"),
    ],
)
def update_PorftfolioGraph(IVV_percent, AGG_percent, USD_percent, date_range):
    start_date = date_time_obj = datetime.datetime.strptime(str(date_range[0]), "%Y")
    end_date = date_time_obj = datetime.datetime.strptime(str(date_range[1]), "%Y")
    dates = IVV_df.index[(IVV_df.index > start_date) * (IVV_df.index < end_date)]
    IVV_prices = IVV_df.values[(IVV_df.index > start_date) * (IVV_df.index < end_date)]
    AGG_prices = AGG_df.values[(AGG_df.index > start_date) * (AGG_df.index < end_date)]
    IVV_prices = 100 * IVV_prices / IVV_prices[0]
    AGG_prices = 100 * AGG_prices / AGG_prices[0]
    if len(AGG_prices) != len(IVV_prices):
        print("Not the same number of elemets from scraper")
    return {
        "data": [
            {"x": dates, "y": IVV_prices, "type": "line", "name": "S&P 500"},
            {
                "x": dates,
                "y": AGG_prices,
                "type": "line",
                "name": "US Bonds",
            },
            {"x": dates, "y": AGG_prices * 0 + 100, "type": "line", "name": "USD"},
        ],
        "layout": {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
            "title": "Portfolio Simulation",
        },
    }


@app.callback(
    Output("stacked_graph", "figure"),
    [
        Input("IVV_percent", "value"),
        Input("AGG_percent", "value"),
        Input("USD_percent", "value"),
        Input("rebelance_preiod", "value"),
        Input("datetime_RangeSlider", "value"),
    ],
)
def update_stacked_graph(IVV_percent, AGG_percent, USD_percent, rebelance_preiod, date_range):
    def to_int(string):
        if string == "":
            return 0
        else:
            return int(string)

    IVV_percent = to_int(IVV_percent)
    AGG_percent = to_int(AGG_percent)
    USD_percent = 100 - IVV_percent - AGG_percent
    rebelance_preiod = to_int(rebelance_preiod)
    start_date = date_time_obj = datetime.datetime.strptime(str(date_range[0]), "%Y")
    end_date = date_time_obj = datetime.datetime.strptime(str(date_range[1]), "%Y")
    dates = IVV_df.index[(IVV_df.index > start_date) * (IVV_df.index < end_date)]
    IVV_prices = IVV_df.values[(IVV_df.index > start_date) * (IVV_df.index < end_date)]
    AGG_prices = AGG_df.values[(AGG_df.index > start_date) * (AGG_df.index < end_date)]
    IVV_prices = 100 * IVV_prices / IVV_prices[0]
    AGG_prices = 100 * AGG_prices / AGG_prices[0]

    IVV_value = np.array([IVV_percent])
    AGG_value = np.array([AGG_percent])
    USD_value = np.array([USD_percent])
    dates_calculated = np.array(dates[0], dtype="datetime64[D]")
    total_value = 100
    while len(dates) > 0:
        next_idxs = dates < utils.add_months(dates[0], rebelance_preiod)
        dates_calculated = np.append(
            dates_calculated, np.array(dates[next_idxs], dtype="datetime64[D]")
        )
        IVV_value = np.append(
            IVV_value,
            total_value * (IVV_prices[next_idxs] / IVV_prices[0]) * IVV_percent / 100,
        )
        AGG_value = np.append(
            AGG_value,
            total_value * (AGG_prices[next_idxs] / AGG_prices[0]) * AGG_percent / 100,
        )
        USD_value = np.append(
            USD_value, total_value * (AGG_prices[next_idxs] * 0 + 1) * USD_percent / 100
        )
        total_value = USD_value[-1] + AGG_value[-1] + IVV_value[-1]

        dates = dates[~next_idxs]
        IVV_prices = IVV_prices[~next_idxs]
        AGG_prices = AGG_prices[~next_idxs]
    df = pd.DataFrame(
        {"S&P 500": IVV_value, "US bonds": AGG_value, "USD": USD_value}, index=dates_calculated
    )
    fig = px.area(
        df,
        template="plotly_dark",
    )
    return fig


@app.callback(Output("Price_Graph", "figure"), [Input("ticker", "value")])
def update_figure(ticker):
    try:
        _, df, _, _ = yahoo_scraper.getHistoricalStockData(ticker)
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


if __name__ == "__main__":
    app.run_server(debug=True, port=8051, host="0.0.0.0")
