from statistics import mean
import numpy as np
import pandas as pd
import requests
import math
import xlsxwriter
from scipy.stats import percentileofscore as score

# IEX_CLOUD_API_TOKEN = "super secret token"
# Let's call it instead from a different file named "secrets"
from secrets import IEX_CLOUD_API_TOKEN


def load_data():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header=0)
    df = html[0]
    return df


stocks = load_data()

symbol = "AAPL"
api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}\
/quote/?token={IEX_CLOUD_API_TOKEN}"

data = requests.get(api_url).json()
# data

price = data["latestPrice"]
# price
pe_ratio = data["peRatio"]
# pe_ratio


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


symbol_groups = list(chunks(stocks["Symbol"], 100))
symbol_strings = []
# symbol_groups
for i in range(0, len(symbol_groups)):
    symbol_strings.append(",".join(symbol_groups[i]))

my_columns = [
    "Ticker",
    "Price",
    "Price-to-Earnings Ratio",
    "Number of Shares to Buy"]

final_dataframe = pd.DataFrame(columns=my_columns)
# final_dataframe

for symbol_string in symbol_strings:
    batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}"  # noqa
    data = requests.get(batch_api_call_url).json()
    # print(data["AAPL"]["price"])
    # print(symbol_string.split(","))
    for symbol in symbol_string.split(","):
        final_dataframe = final_dataframe.append(
            pd.Series([
                symbol,
                data[symbol]["quote"]["latestPrice"],
                data[symbol]["quote"]["peRatio"],
                "N/A"
            ],
                index=my_columns
            ),
            ignore_index=True
        )

# final_dataframe

"""Removing Glamour Stocks"""

final_dataframe.sort_values(
    "Price-to-Earnings Ratio", ascending=True, inplace=True)
final_dataframe = final_dataframe[
    final_dataframe["Price-to-Earnings Ratio"] > 0]
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace=True)
final_dataframe.drop("index", axis=1, inplace=True)
final_dataframe

"""Calculating Number of Shares to Buy"""


def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the size of your portfolio:")

    try:
        float(portfolio_size)
    except ValueError:
        print("That is not a number! \nPlease try again ")
        portfolio_size = input("Enter the size of your portfolio:")


portfolio_input()
# print(portfolio_size)

position_size = float(portfolio_size) / len(final_dataframe.index)
position_size

for row in final_dataframe.index:
    final_dataframe.loc[row, "Number of Shares to Buy"] = math.floor(
        position_size / final_dataframe.loc[row, "Price"])

# final_dataframe

"""Building a Better (and more Realistic) Value Strategy - Robust Value (rv)"""

"""

"""
symbol = "AAPL"
batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote,advanced-stats&symbols={symbol}&token={IEX_CLOUD_API_TOKEN}"  # noqa
data = requests.get(batch_api_call_url).json()

# Price-to-Earnings Ratio
pe_ratio = data[symbol]["quote"]["peRatio"]

# Price-to-book Ratio
pb_ratio = data[symbol]["advanced-stats"]["priceToBook"]

# Price-to-Sales Ratio
ps_ratio = data[symbol]["advanced-stats"]["priceToSales"]

# EV/EBITDA
enterprise_value = data[symbol]["advanced-stats"]["enterpriseValue"]
ebitda = data[symbol]["advanced-stats"]["EBITDA"]

ev_to_ebitda = enterprise_value/ebitda

# EV/GP
gross_profit = data[symbol]["advanced-stats"]["grossProfit"]

ev_to_gross_profit = enterprise_value/gross_profit

"""Creating and automating the DataFrame"""

rv_columns = [
    "Ticker",
    "Price",
    "Number of Shares to Buy",
    "Price-to-Earnings Ratio",
    "PE Percentile",
    "Price-to-book Ratio",
    "PB Percentile",
    "Price-to-Sales Ratio",
    "PS Percentile",
    "EV/EBITDA",
    "EV/EBITDA Percentile",
    "EV/GP",
    "EV/GP Percentile",
    "RV Score"
]

rv_dataframe = pd.DataFrame(columns=rv_columns)

for symbol_string in symbol_strings:
    batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote,advanced-stats&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}"  # noqa
    # print(batch_api_call_url)
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(","):
        enterprise_value = data[symbol]["advanced-stats"]["enterpriseValue"]
        ebitda = data[symbol]["advanced-stats"]["EBITDA"]
        gross_profit = data[symbol]["advanced-stats"]["grossProfit"]

        try:
            ev_to_ebitda = enterprise_value/ebitda
        except TypeError:
            ev_to_ebitda = np.NaN

        try:
            ev_to_gross_profit = enterprise_value/gross_profit
        except TypeError:
            ev_to_gross_profit = np.NaN

        rv_dataframe = rv_dataframe.append(
            pd.Series([
                symbol,
                data[symbol]["quote"]["latestPrice"],
                "N/A",
                data[symbol]["quote"]["peRatio"],
                "N/A",
                data[symbol]["advanced-stats"]["priceToBook"],
                "N/A",
                data[symbol]["advanced-stats"]["priceToSales"],
                "N/A",
                ev_to_ebitda,
                "N/A",
                ev_to_gross_profit,
                "N/A",
                "N/A"
            ],
                index=rv_columns
            ),
            ignore_index=True
        )

# print(rv_dataframe)

"""Dealing with Missing Data in our DataFrame"""

# rv_dataframe[rv_dataframe.isnull().any(axis=1)]

for column in ['Price-to-Earnings Ratio', 'Price-to-book Ratio',
               'Price-to-Sales Ratio', 'EV/EBITDA', 'EV/GP']:
    rv_dataframe[column].fillna(rv_dataframe[column].mean(), inplace=True)

# rv_dataframe.columns

rv_dataframe[rv_dataframe.isnull().any(axis=1)]

"""Calculating Value Percentiles"""
# Summary at 4:07

# Create dictionary
metrics = {"Price-to-Earnings Ratio": "PE Percentile",
           "Price-to-book Ratio": "PB Percentile",
           "Price-to-Sales Ratio": "PS Percentile",
           "EV/EBITDA": "EV/EBITDA Percentile",
           "EV/GP": "EV/GP Percentile"}
for metric in metrics.keys():
    for row in rv_dataframe.index:
        rv_dataframe.loc[row, metrics[metric]] = score(
            rv_dataframe[metric], rv_dataframe.loc[row, metric]) / 100

# rv_dataframe

"""Calculating the RV Score"""

# mean([5, 10])

for row in rv_dataframe.index:
    value_percentiles = []
    for metric in metrics.keys():
        value_percentiles.append(rv_dataframe.loc[row, metrics[metric]])
    rv_dataframe.loc[row, "RV Score"] = mean(value_percentiles)

# rv_dataframe

"""Selecting the 50 Best Value Stocks"""

rv_dataframe.sort_values("RV Score", ascending=True, inplace=True)
rv_dataframe = rv_dataframe[:50]
# rv_dataframe
# len(rv_dataframe.index)
rv_dataframe.reset_index(drop=True, inplace=True)
# rv_dataframe

""" Calculating Shares to Buy"""
portfolio_input()
# print(portfolio_size)

position_size = float(portfolio_size)/len(rv_dataframe.index)
# position_size

for row in rv_dataframe.index:
    rv_dataframe.loc[row, "Number of Shares to Buy"] = math.floor(
        position_size/rv_dataframe.loc[row, "Price"])

# rv_dataframe

"""Formatting Excel Output"""
writer = pd.ExcelWriter("value_strategy.xlsx", engine="xlsxwriter")
rv_dataframe.to_excel(writer, sheet_name="Value Strategy", index=False)

"""Formatting"""
background_color = "#0a0a23"
font_color = "#ffffff"

string_format = writer.book.add_format(
    {
        "font_color": font_color,
        "bg_color": background_color,
        "border": 1
    }
)

dollar_format = writer.book.add_format(
    {
        "num_format": "$0.00",
        "font_color": font_color,
        "bg_color": background_color,
        "border": 1
    }
)

integer_format = writer.book.add_format(
    {
        "num_format": "0",
        "font_color": font_color,
        "bg_color": background_color,
        "border": 1
    }
)

float_format = writer.book.add_format(
    {
        "num_format": "0.0",
        "font_color": font_color,
        "bg_color": background_color,
        "border": 1
    }
)

percent_format = writer.book.add_format(
    {
        'num_format': '0.0%',
        'font_color': font_color,
        'bg_color': background_color,
        'border': 1
    }
)

column_formats = {
    "A": ["Ticker", string_format],
    "B": ["Price", dollar_format],
    "C": ["Number of Shares to Buy", integer_format],
    "D": ["Price-to-Earnings Ratio", float_format],
    "E": ["PE Percentile", percent_format],
    "F": ["Price-to-book Ratio", float_format],
    "G": ["PB Percentile", percent_format],
    "H": ["Price-to-Sales Ratio", float_format],
    "I": ["PS Percentile", percent_format],
    "J": ["EV/EBITDA", float_format],
    "K": ["EV/EBITDA Percentile", percent_format],
    "L": ["EV/GP", float_format],
    "M": ["EV/GP Percentile", percent_format],
    "N": ["RV Score", percent_format]
}

for column in column_formats.keys():
    writer.sheets["Value Strategy"].set_column(
        f"{column}:{column}", 22, column_formats[column][1])
    writer.sheets["Value Strategy"].write(
        f"{column}1", column_formats[column][0], string_format)

writer.save()
