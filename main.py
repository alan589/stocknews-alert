import os
import smtplib
import requests
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc."

STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
MY_EMAIL = os.environ.get("MY_EMAIL")
APP_EMAIL_PASS = os.environ.get("APP_EMAIL_PASS")


SMTP = "smtp.gmail.com"

STOCK_END_POINT = 'https://www.alphavantage.co/query'
NEW_END_POINT = "https://newsapi.org/v2/everything"

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

news_parameters = {
    "q": COMPANY_NAME,
    "searchIn": "title",
    "sortBy": "publishedAt",
    "apikey": NEWS_API_KEY
}

response = requests.get(STOCK_END_POINT, params=stock_parameters)
response.raise_for_status()
data = response.json()

daily_data = data["Time Series (Daily)"]
dates = list(daily_data)[:2]

yesterday_close = float(daily_data[dates[0]]["4. close"])
before_yesterday_close = float(daily_data[dates[1]]["4. close"])

difference = (yesterday_close - before_yesterday_close)
average = (yesterday_close + before_yesterday_close) / 2
percentual_difference = difference / average * 100
percentual_difference = abs(round(percentual_difference, 2))


if percentual_difference >= 5:
    response = requests.get(url=NEW_END_POINT, params=news_parameters)
    response.raise_for_status()
    data = response.json()
    articles = data["articles"][:3]

    if difference < 0:
        arrow = "🔻"
    else:
        arrow = "🔺"

    body = ""
    for article in articles:
        body += f"{STOCK}: {arrow}{percentual_difference}%\nHeadline: {article["title"]}\nBrief: {article["description"]}\n{article["url"]}\n\n"

    msg = MIMEMultipart()
    msg["From"] = MY_EMAIL
    msg["To"] = MY_EMAIL
    msg["Subject"] = "Stock News!"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP(SMTP) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, APP_EMAIL_PASS)

        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg=msg.as_string()
        )
