import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Email configuration
EMAIL_CONFIG = {
    "sender": os.getenv("EMAIL_SENDER"),
    "password": os.getenv("EMAIL_PASSWORD"),
    "recipient": os.getenv("EMAIL_RECIPIENT"),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

# Stocks to monitor
STOCK_WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA"]

# News sources
NEWS_SOURCES = {
    "Yahoo Finance": "https://finance.yahoo.com/news",
    "Bloomberg Markets": "https://www.bloomberg.com/markets",
    "CNBC Markets": "https://www.cnbc.com/markets/"
}

# Report settings
REPORT_TIME = "08:00"  # Time to send report daily