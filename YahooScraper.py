import pandas as pd
from bs4 import BeautifulSoup
import requests
from json import loads
import re


def getHistoricalStockData(ticker):
    start_time = pd.Timestamp(2010)
    start_seconds = int(start_time.timestamp())
    end_seconds = int(pd.Timestamp("now").timestamp())
    url = (
        "https://finance.yahoo.com/quote/"
        + ticker
        + "/history?period1="
        + str(start_seconds)
        + "&period2="
        + str(end_seconds)
        + "&interval=1d&filter=history&frequency=1d"
    )
    soup = BeautifulSoup(requests.get(url).content, features="html.parser")
    script = soup.find("script", text=re.compile("root.App.main")).text
    json_data = loads(re.search("root.App.main\s+=\s+(\{.*\})", script).group(1))
    time_zone = json_data["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]["timeZone"][
        "gmtOffset"
    ]
    data = pd.DataFrame(
        json_data["context"]["dispatcher"]["stores"]["HistoricalPriceStore"]["prices"]
    )
    data.date = pd.to_datetime(data.date * 1e9)
    data.set_index("date", inplace=True)
    data.index = data.index.date

    Prices = data[data["type"].isna()].copy() if "type" in data.columns else data.copy()
    Prices = Prices["close"].copy()
    Prices.sort_index(inplace=True)
    Prices = Prices.asfreq(freq="1D", method="ffill")
    PricesAdjusted = data[data["type"].isna()].copy() if "type" in data.columns else data.copy()
    PricesAdjusted = PricesAdjusted["adjclose"].copy()
    PricesAdjusted.sort_index(inplace=True)
    PricesAdjusted = PricesAdjusted.asfreq(freq="1D", method="ffill")

    if "amount" in data.columns:
        Dividends = data[data["type"] == "DIVIDEND"].copy()
        Dividends.index.name = "date"
        Dividends = Dividends.groupby("date")["amount"].sum().sort_index().copy()
        Dividends.name = "dividend_amount"
    else:
        Dividends = pd.DataFrame()

    if "splitRatio" in data.columns:
        Splits = data[data["type"] == "SPLIT"].copy()
        Splits = Splits["splitRatio"].copy()
        Splits.sort_index(inplace=True)
    else:
        Splits = pd.DataFrame()

    return Prices, PricesAdjusted, Dividends, Splits


def getHistoricalForexData(ticker):
    raise NotImplementedError


def getCurrentStockPrice(ticker):
    url = "https://finance.yahoo.com/quote/" + ticker
    ugly_soup = requests.get(url).content
    soup = BeautifulSoup(ugly_soup, features="html.parser")
    script = soup.find("script", text=re.compile("root.App.main")).text
    data = loads(re.search("root.App.main\s+=\s+({.*\})", script).group(1))
    price = data["context"]["dispatcher"]["stores"]["QuoteSummaryStore"]["price"][
        "regularMarketPrice"
    ]["raw"]
    return price


def getCurrentForexPrice(ticker1, ticker2):
    if ticker1.lower() == ticker2.lower():
        return 1
    return getCurrentStockPrice(f"{ticker1}{ticker2}=x")


if __name__ == "__main__":
    print("running yahoo.py")
    print(getCurrentStockPrice("VOO"))
    Prices, PricesAdjusted, Dividends, Splits = getHistoricalStockData("VOO")
    print(Prices)
    print(Dividends)
    print(Splits)
