from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import lxml

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.36"
}


def get_stocks_losers():
    response = requests.get("https://finance.yahoo.com/losers?count=100", headers=HEADERS)
    yahoo_finance_web_page = response.text
    if str(response.status_code)[0] != "2":
        return None
    finance_soup = BeautifulSoup(yahoo_finance_web_page, 'html.parser')
    losers_table = finance_soup.select_one("#scr-res-table table")
    df = pd.read_html(StringIO(str(losers_table)))[0]
    df['% Change'] = pd.to_numeric(df['% Change'].str.replace('%', ''), errors='coerce')
    columns_to_drop = ['Change', 'Volume', 'Avg Vol (3 month)', 'Market Cap', 'PE Ratio (TTM)', '52 Week Range']
    df = df.drop(columns=columns_to_drop)
    df = df[df['% Change'] < -5]
    return df


def get_price_book(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
    response = requests.get(url, headers=HEADERS)
    if str(response.status_code)[0] != "2":
        return None
    stats_page = response.text
    stats_soup = BeautifulSoup(stats_page, 'html.parser')
    price_book = stats_soup.select_one("div:nth-child(1) > div > div > div > div > table > tbody > tr:nth-child(7)")
    price_book = float(price_book.get_text().replace("Price/Book (mrq)", ""))
    print(price_book)
    return price_book


if __name__ == "__main__":
    df_losers = get_stocks_losers()
    pb = get_price_book(df_losers['Symbol'][0])
    print(df_losers)
    print(pb)
