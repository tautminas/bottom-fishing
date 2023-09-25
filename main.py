from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import lxml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
import argparse
import smtplib
from twilio.rest import Client

parser = argparse.ArgumentParser(description='A script for getting information for "bottom fishing" investment strategy.')
parser.add_argument('--news', action='store_true', help='Get up to three news related to the strongest recommendation of the script. Keep in mind that "NEWS_API_KEY" has to be defined as an environment variable. To get the API key go to https://newsapi.org and create an account.')
parser.add_argument('--email', action='store_true', help='Get email with recommendations.')
parser.add_argument('--sms', action='store_true', help='Get SMS with recommendations.')
args = parser.parse_args()

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
MY_EMAIL = os.environ.get("MY_EMAIL")
MY_EMAIL_PASSWORD = os.environ.get("MY_EMAIL_PASSWORD")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_ACCOUNT_AUTH_TOKEN = os.environ.get("TWILIO_ACCOUNT_AUTH_TOKEN")
FROM_NUMBER = os.environ.get("FROM_NUMBER")
TO_NUMBER = os.environ.get("TO_NUMBER")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.36"
}


def get_stocks_losers() -> pd.DataFrame | None:
    """
        Fetches the list of top stock losers from Yahoo Finance and returns the data as a pandas DataFrame.

        Returns:
            pd.DataFrame | None: A DataFrame containing information about the top stock losers.
                Columns include 'Symbol', 'Name', 'Price (Intraday)', and '% Change'.
                The '% Change' column is converted to numeric values without the '%' sign.
                Returns None if there was an issue with the web request or if the data is not available.

        Note:
            This function scrapes the Yahoo Finance website, so its functionality
            may be affected if the website structure changes.
    """
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


def get_price_book(symbol: str) -> float | None:
    """
        Fetches the price-to-book (P/B) ratio for a specified stock symbol from Yahoo Finance.

        Args:
            symbol (str): The stock symbol for which to retrieve the P/B ratio.

        Returns:
            float | None: The price-to-book (P/B) ratio of the specified stock symbol.
                Returns None if the ratio is not available or if there was an issue with the request.

        Note:
            This function scrapes Yahoo Finance's key statistics page for the P/B ratio.
            It may return None if the P/B ratio is not available or if the website structure changes.
    """
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


def get_recommendation_rating(symbol: str) -> float | None:
    """
        Retrieves the recommendation rating for a specified stock symbol from Yahoo Finance.

        Args:
            symbol (str): The stock symbol for which to retrieve the recommendation rating.

        Returns:
            float | None: The recommendation rating of the specified stock symbol.
                Returns None if the rating is not available or if there was an issue with the web scraping.

        Note:
            This function uses a headless web browser (Chrome) to access Yahoo Finance's analysis page for the rating.
            It may return None if the rating is not found or if there are changes in the website structure.
    """
    options = Options()
    # options.add_experimental_option('detach', True) # Uncomment this line for avoiding window closure
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(options=options, )
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


def get_news(name: str) -> list[str]:
    """
    Get the top three news articles containing the specified keyword in the title.

    Args:
        name (str): The keyword to search for in news article titles.

    Returns:
        list[str]: A list of formatted news articles containing headline and brief.

    Raises:
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
        ValueError: If the API key or endpoint is not properly configured.
    """
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": name,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    three_articles = news_response.json()["articles"][:3]
    formatted_articles = [f"Headline: {article['title']}\n"
                          f"Brief: {article['description']}" for article in three_articles]
    return formatted_articles


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

    if args.news:
        main_recommendation_name = df_losers['Name'].iloc[0]
        print(main_recommendation_name)
        news = get_news(main_recommendation_name)
        for news_item in news:
            print(news_item)

    if args.email:
        recommended_symbols = df_losers['Symbol'].tolist()
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(MY_EMAIL, MY_EMAIL_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=MY_EMAIL,
                msg=f"Subject:Recommendations for further investigation\n\nSymbols: {', '.join(recommended_symbols)}"
            )

    if args.sms:
        recommended_symbols = df_losers['Symbol'].tolist()
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_ACCOUNT_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Recommendations for further investigation: {', '.join(recommended_symbols)}",
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )
        print(message.status)
