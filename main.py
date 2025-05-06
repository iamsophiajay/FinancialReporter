import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import schedule
import time
from datetime import datetime
import yfinance as yf
from config import EMAIL_CONFIG, STOCK_WATCHLIST, NEWS_SOURCES, REPORT_TIME

def get_stock_prices(tickers):
    """Fetch current stock prices using yfinance"""
    data = yf.download(tickers, period="1d", group_by='ticker')
    prices = []
    
    for ticker in tickers:
        try:
            close_price = data[ticker]['Close'][0]
            prices.append({
                'Ticker': ticker,
                'Price': f"${close_price:.2f}",
                'Change': f"{(close_price - data[ticker]['Open'][0]) / data[ticker]['Open'][0] * 100:.2f}%"
            })
        except:
            prices.append({
                'Ticker': ticker,
                'Price': "N/A",
                'Change': "N/A"
            })
            
    return pd.DataFrame(prices)

def scrape_financial_news():
    """Scrape headlines from configured news sources"""
    news_items = []
    
    for source, url in NEWS_SOURCES.items():
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Example for Yahoo Finance - adjust selectors per site
            if "yahoo" in url.lower():
                headlines = soup.select('h3 a')[:5]  # Get first 5 headlines
                for headline in headlines:
                    news_items.append({
                        'Source': source,
                        'Headline': headline.text.strip(),
                        'Link': headline['href'] if 'href' in headline.attrs else url
                    })
            
            # Add similar blocks for other news sources
            
        except Exception as e:
            print(f"Error scraping {source}: {e}")
            
    return pd.DataFrame(news_items)    

def generate_report(stock_df, news_df):
    """Generate a formatted report"""
    report = MIMEMultipart()
    report['Subject'] = f"Daily Financial Report - {datetime.now().strftime('%Y-%m-%d')}"
    
    # HTML content
    html = f"""
    <html>
        <body>
            <h1>Daily Financial Report</h1>
            <h2>Stock Prices as of {datetime.now().strftime('%Y-%m-%d %H:%M')}</h2>
            {stock_df.to_html(index=False)}
            
            <h2>Top Financial News</h2>
            {news_df.to_html(index=False)}
            
            <p>Report generated automatically.</p>
        </body>
    </html>
    """
    
    report.attach(MIMEText(html, 'html'))
    
    # Attach CSV versions
    stock_csv = MIMEApplication(stock_df.to_csv())
    stock_csv.add_header('Content-Disposition', 'attachment', filename='stock_prices.csv')
    report.attach(stock_csv)
    
    news_csv = MIMEApplication(news_df.to_csv())
    news_csv.add_header('Content-Disposition', 'attachment', filename='financial_news.csv')
    report.attach(news_csv)
    
    return report    
def send_email(report):
    """Send the generated report via email"""
    try:
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
            server.sendmail(
                EMAIL_CONFIG['sender'],
                EMAIL_CONFIG['recipient'],
                report.as_string()
            )
        print("Report sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}") 

def daily_report_job():
    print(f"Generating report at {datetime.now()}...")
    try:
        # Get data
        stock_data = get_stock_prices(STOCK_WATCHLIST)
        news_data = scrape_financial_news()
        
        # Generate and send report
        report = generate_report(stock_data, news_data)
        send_email(report)
    except Exception as e:
        print(f"Error generating report: {e}")

# Schedule the job
schedule.every().day.at(REPORT_TIME).do(daily_report_job)

# Main loop
print(f"Financial Reporter started. Will send reports daily at {REPORT_TIME}.")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute           
    