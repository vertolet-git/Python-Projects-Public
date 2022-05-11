from statistics import mean
import numpy as np
import pandas as pd
import requests
import math
from scipy.stats import percentileofscore as score
import xlsxwriter

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
/stats?token={IEX_CLOUD_API_TOKEN}"

data = requests.get(api_url).json()
# data.status_code
# data

"""Batch API Calls"""

data["year1ChangePercent"]


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


symbol_groups = list(chunks(stocks["Symbol"], 100))
symbol_strings = []
# symbol_groups
for i in range(0, len(symbol_groups)):
    symbol_strings.append(",".join(symbol_groups[i]))
#  print(symbol_strings[i])
"""for symbol_string in symbol_strings:
    print(symbol_string)"""

my_columns = [
    "Ticker",
    "Stock Price",
    "One-Year Price Return",
    "Number of Shares to Buy"]

final_dataframe = pd.DataFrame(columns=my_columns)
# final_dataframe

for symbol_string in symbol_strings:
    batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?symbols={symbol_string}&types=stats,quote,price&token={IEX_CLOUD_API_TOKEN}"  # noqa
    data = requests.get(batch_api_call_url).json()
    # print(data["AAPL"]["price"])
    # print(symbol_string.split(","))
    for symbol in symbol_string.split(","):
        final_dataframe = final_dataframe.append(
            pd.Series([
                symbol,
                data[symbol]["price"],
                data[symbol]["stats"]["year1ChangePercent"],
                "N/A"
            ],
                index=my_columns
            ),
            ignore_index=True
        )
# final_dataframe

"""Removing Low-Momentum Stocks"""
final_dataframe.sort_values("One-Year Price Return", ascending=False,
                            inplace=True)
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace=True)
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
# print(position_size)
for i in range(0, len(final_dataframe)):
    final_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(
        position_size / final_dataframe.loc[i, "Stock Price"])

# final_dataframe

"""Building a Better (and more realistic) Momentum Strategy - High Quality Momentum (hqm)"""  # noqa

hqm_columns = [
    "Ticker",
    "Price",
    "Number of Shares to Buy",
    "One-Year Price Return",
    "One-Year Return Percentile",
    "Six-Month Price Return",
    "Six-Month Return Percentile",
    "Three-Month Price Return",
    "Three-Month Return Percentile",
    "One-Month Price Return",
    "One-Month Return Percentile",
    "HQM Score"
]

hqm_dataframe = pd.DataFrame(columns=hqm_columns)
# hqm_dataframe

for symbol_string in symbol_strings:
    batch_api_call_url = f"https://sandbox.iexapis.com/stable/stock/market/batch/?symbols={symbol_string}&types=stats,quote,price&token={IEX_CLOUD_API_TOKEN}"  # noqa
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(","):
        hqm_dataframe = hqm_dataframe.append(
            pd.Series(
                [
                    symbol,
                    data[symbol]["price"],
                    "Number of Shares to Buy",
                    data[symbol]["stats"]["year1ChangePercent"],
                    "N/A",
                    data[symbol]["stats"]["month6ChangePercent"],
                    "N/A",
                    data[symbol]["stats"]["month3ChangePercent"],
                    "N/A",
                    data[symbol]["stats"]["month1ChangePercent"],
                    "N/A",
                    "N/A"
                ], index=hqm_columns,
            ), ignore_index=True
        )

# hqm_dataframe

time_periods = [
    "One-Year",
    "Six-Month",
    "Three-Month",
    "One-Month"
]
# Explanation at 2:29
for row in hqm_dataframe.index:
    for time_period in time_periods:
        change_col = f"{time_period} Price Return"
        percentile_col = f"{time_period} Return Percentile"
        hqm_dataframe.loc[row, percentile_col] = score(hqm_dataframe[change_col], hqm_dataframe.loc[row, change_col]) / 100  # noqa


# hqm_dataframe

"""Calculating the HQM Score"""
# Explanation at 2:35

for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[
            row,
            f"{time_period} Return Percentile"
        ])
        hqm_dataframe.loc[row, "HQM Score"] = mean(momentum_percentiles)

# hqm_dataframe

"""Selecting the 50 Best Momentum Stocks"""

hqm_dataframe.sort_values("HQM Score", ascending=False, inplace=True)
hqm_dataframe = hqm_dataframe[:50]
hqm_dataframe.reset_index(inplace=True, drop=True)
# hqm_dataframe

"""Calculating Number of Shares to Buy"""

portfolio_input()

position_size = float(portfolio_size) / len(hqm_dataframe.index)
for i in hqm_dataframe.index:
    hqm_dataframe.loc[i, "Number of Shares to Buy"] = math.floor(
        position_size / hqm_dataframe.loc[i, "Price"])

# hqm_dataframe

"""Formatting Excel Output"""
writer = pd.ExcelWriter("momentum_strategy.xlsx", engine="xlsxwriter")
hqm_dataframe.to_excel(writer, sheet_name="Momentum Strategy", index=False)

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
    "D": ["One-Year Price Return", percent_format],
    "E": ["One-Year Return Percentile", percent_format],
    "F": ["Six-Month Price Return", percent_format],
    "G": ["Six-Month Return Percentile", percent_format],
    "H": ["Three-Month Price Return", percent_format],
    "I": ["Three-Month Return Percentile", percent_format],
    "J": ["One-Month Price Return", percent_format],
    "K": ["One-Month Return Percentile", percent_format],
    "L": ["HQM Score", percent_format]
}

for column in column_formats.keys():
    writer.sheets["Momentum Strategy"].set_column(
        f"{column}:{column}", 22, column_formats[column][1])
    writer.sheets["Momentum Strategy"].write(
        f"{column}1", column_formats[column][0], string_format)

writer.save()
