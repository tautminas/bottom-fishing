from bs4 import BeautifulSoup
import requests

response = requests.get("https://finance.yahoo.com/losers")

yahoo_finance_web_page = response.text
print(f"Response status code: {response.status_code}")

soup = BeautifulSoup(yahoo_finance_web_page, 'html.parser')
print(f"Title of the page: {soup.title}")

biggest_loser = soup.select_one("#scr-res-table > div.Ovx\(a\).Ovx\(h\)--print.Ovy\(h\).W\(100\%\) > table > tbody > tr:nth-child(1) > td.Va\(m\).Ta\(start\).Pstart\(6px\).Pend\(10px\).Miw\(90px\).Start\(0\).Pend\(10px\).simpTblRow\:h_Bgc\(\$hoverBgColor\).Pos\(st\).Bgc\(\$lv3BgColor\).Z\(1\).Bgc\(\$lv2BgColor\).Ta\(start\)\!.Fz\(s\) > a")
biggest_loser_change_percent = soup.select_one("#scr-res-table > div.Ovx\(a\).Ovx\(h\)--print.Ovy\(h\).W\(100\%\) > table > tbody > tr:nth-child(1) > td:nth-child(5) > fin-streamer > span")
print(f"Biggest loser is {biggest_loser['title']} with {biggest_loser_change_percent.text} change loss.")
