from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import StringIO
import lxml

response = requests.get("https://finance.yahoo.com/losers?count=100")

yahoo_finance_web_page = response.text
print(f"Response status code: {response.status_code}")

soup = BeautifulSoup(yahoo_finance_web_page, 'html.parser')

losers_table = soup.select_one("#scr-res-table table")
df_losers = pd.read_html(StringIO(str(losers_table)))[0]
df_losers['% Change'] = pd.to_numeric(df_losers['% Change'].str.replace('%', ''), errors='coerce')
# Filtering
df_losers = df_losers[df_losers['% Change'] < -10]

print(df_losers)

for index, row in df_losers.iterrows():
    print(row['Symbol'], row['% Change'])