import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output


# from FinScrapers import Alphavantage
# from FinScrapers import Bizportal
import YahooScraper

# data, _, _, _ = Alphavantage.getHistoricalData('VOO')
# data, _, _, _ = Bizportal.getHistoricalData('1115773')
data, _, _, _ = YahooScraper.getHistoricalStockData("VOO")
app = dash.Dash(__name__)

colors = {"background": "#111111", "text": "#7FDBFF"}

app.layout = html.Div(
    style={"backgroundColor": colors["background"]},
    children=[
        html.H1(
            children="Hello Dash",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Div(
            children="Dash: A web application framework for Python.",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Div(
            children=[dcc.Input(id="ticker", value="VOO", type="text")],
            style={"textAlign": "center", "color": colors["text"]},
        ),
        dcc.Graph(
            id="Price_Graph",
            figure={
                "data": [{"x": data.index, "y": data.values, "type": "line", "name": "SF"}],
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
        "data": [{"x": df.index, "y": df.values, "type": "line", "name": "SF"}],
        "layout": {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
        },
    }


if __name__ == "__main__":
    app.run_server(debug=True, port=8051, host="0.0.0.0")
