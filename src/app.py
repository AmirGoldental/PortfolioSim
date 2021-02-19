import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import datetime

from .modules import YahooScraper

# from FinScrapers import Alphavantage
# from FinScrapers import Bizportal
from dateutil.relativedelta import relativedelta


# data, _, _, _ = Alphavantage.getHistoricalData('IVV')
# data, _, _, _ = Bizportal.getHistoricalData('1115773')
_, IVV_df, _, _ = YahooScraper.getHistoricalStockData("IVV")
_, AGG_df, _, _ = YahooScraper.getHistoricalStockData("AGG")
app = dash.Dash(__name__, title="Portfolio Simulator")
server = app.server

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


controls_div = html.Div(
    className="controls",
    children=[
        TextControl("US bonds: ", 30, "%", "AGG_percent"),
        TextControl("S&P 500: ", 40, "%", "IVV_percent"),
        TextControl("USD: ", 0, "%", "USD_percent"),
        html.Br(),
        TextControl("Rebalance every ", 4, "months", "rebelance_preiod"),
        DateRangeSlider("Date range:", [2006, 2021], [2016, 2020]),
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


app.layout = html.Div(
    className="dash-main",
    children=[
        html.H1(["Passive Investment", html.Br(), "Portfolio Simuation"]),
        controls_div,
        LineGraph("PorftfolioGraph"),
        SingleStock(),
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
    if len(AGG_prices) != len(IVV_prices):
        print("Not the same number of elemets from scraper")
    return {
        "data": [
            {"x": dates, "y": IVV_prices, "type": "line", "name": "S&P 500"},
            {"x": dates, "y": AGG_prices, "type": "line", "name": "US Bonds"},
            {"x": dates, "y": AGG_prices * 0 + 100, "type": "line", "name": "USD"},
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
