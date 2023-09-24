from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

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
    return df


def get_price_book(symbol):
    url = f"https://finance.yahoo.com/quote/{symbol}/key-statistics?p={symbol}"
    response = requests.get(url, headers=HEADERS)
    if str(response.status_code)[0] != "2":
        return None
    stats_page = response.text
    stats_soup = BeautifulSoup(stats_page, 'html.parser')
    price_book = stats_soup.select_one("div:nth-child(1) > div > div > div > div > table > tbody > tr:nth-child(7)")
    price_book = price_book.get_text().replace("Price/Book (mrq)", "")
    if price_book == "N/A":
        return None
    price_book = float(price_book)
    return price_book


def get_recommendation_rating(symbol):
    options = Options()
    # options.add_experimental_option('detach', True) # Uncomment this line for avoiding window closure
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    url = f"https://finance.yahoo.com/quote/{symbol}/analysis?p={symbol}"
    driver.get(url)
    time.sleep(1)
    down = driver.find_element(By.ID, "scroll-down-btn")
    down.click()
    time.sleep(1)
    reject = driver.find_element(By.CLASS_NAME, "reject-all")
    reject.click()
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    recommendation_rating = soup.find("div", {"data-test": "rec-rating-txt"})
    if recommendation_rating is None:
        return None
    recommendation_rating = float(recommendation_rating.get_text())
    return recommendation_rating


if __name__ == "__main__":
    df_losers = get_stocks_losers()
    df_losers = df_losers[df_losers['% Change'] < -5]
    df_losers['Price/Book'] = df_losers['Symbol'].apply(get_price_book)
    print("Frame has scraped P/B values.")
    df_losers = df_losers[df_losers["Price/Book"] > df_losers["Price (Intraday)"]]
    df_losers['Recommendation'] = df_losers['Symbol'].apply(get_recommendation_rating)
    print("Frame has scraped rating values.")
    df_losers = df_losers.sort_values(by='Recommendation', ascending=True, na_position='last')
    pd.set_option('display.max_columns', None)
    print(df_losers)
