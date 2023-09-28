# Bottom Fishing Script

## Most important thing
This script is not a financial advice! Do not use it for real money trading. It was written for educational and entertainment purposes only. It is recommended trying it out with stock market simulators with virtual money to explore Bottom fishing investment strategy.

## About the script

Note: Since this script involves web scraping, its functionality may be impacted by changes in the structure of the scraped websites.

This script gives stock recommendations for further analysis for learning Bottom fishing investment strategy. Script does it by scraping the web to get the biggest stocks losers at the current time and by performing data filtering on the fetched data.

Script also has additional options (please refer to [setup chapter](#setup-for-the-usage-of-additional-options) for information of usage):
- Getting up to three news articles related to the strongest stock recommendation using the [News API](https://newsapi.org/).
- Sending an email with the stock recommendations using [smtplib](https://docs.python.org/3/library/smtplib.html).
- Sending the SMS with the symbols of recommended stocks using [Twilio API](https://www.twilio.com/docs/usage/api).

Web scraping is performed on various pages of the [Yahoo Finance](https://finance.yahoo.com/).

Filtering is done according to these conditions:
- Percentage change is less than -5%. This filter helps to analyse only the biggest losers of the day.
- Price/Book (mrq) value is larger than the price (intraday) value. This condition indicates that a Price-to-Book (P/B) ratio is less than 1. A P/B ratio below 1 typically suggests that the stock may be undervalued, as the market is valuing the company's stock at a price lower than its book value per share.
- The analysts' recommendation rating is below 2.5, indicating a preference for buying the stock over selling it.

## Requirements

It is necessary for the functionality of the script to have Google Chrome web browser installed. It is needed for the Selenium package.

## Setup for the usage of additional options

All of the additional options use private data for the functionality. This data should be stored in the environment variables due to security reasons.

Setting up environment variables:
- On Windows:
```bash
setx MY_VARIABLE "variable_value"
```
- On macOS and Linux:
```bash
export MY_VARIABLE="variable_value"
```

Windows has GUI option for setting the environment variable as well.

### News
Login to [News API](https://newsapi.org/) and store tha API key to environment variable called "NEWS_API_KEY"

### Email
Login to Gmail -> Click on your user photo -> "Manage your Google Account" -> "Security" -> Turn on your 2-Step Verification if none is set -> "App passwords" -> Type: "Other" -> "Generate" -> Copy the shown password.

Afterwards set these variables:
- MY_EMAIL
- MY_EMAIL_PASSWORD

Do not forget to check the spam folder in case the email is not found.

### SMS
Login to [Twilio API](https://www.twilio.com/docs/usage/api) and store the data to these variables:
- TWILIO_ACCOUNT_SID
- TWILIO_ACCOUNT_AUTH_TOKEN
- FROM_NUMBER
- TO_NUMBER

## Running the script

Create virtual environment
```bash
python -m venv bottom-fishing
```

Activate the virtual environment based on the operating system:
- On Windows:
```bash
bottom-fishing\Scripts\activate
```
- On macOS and Linux:
```bash
source bottom-fishing/bin/activate
```

Install the required packages:
```bash
pip install -r requirements.txt
```

Run the script:
```bash
python main.py
```

You can explore the additional options using the script in help mode:
```bash
python main.py --help
```

After you are done using the script leave the virtual environment:
```bash
deactivate
```

## About Bottom fishing investment strategy
The bottom fishing investment strategy, often referred to as 'Catching a Falling Knife,' involves actively seeking out stocks that have experienced significant price declines in the hope of buying them at a low point before they potentially rebound. It can be a profitable strategy, but it's also risky because there's no guarantee that a stock will recover after a price decline. Therefore, successful implementation of this strategy demands rigorous analysis of the asset's underlying fundamentals, careful consideration of market conditions, and a thorough understanding of the specific stock in question.