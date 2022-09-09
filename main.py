from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import finplot as fplt

PAIRS = ["EURUSD", "AUDUSD", "GBPUSD", "EURJPY", "USDJPY", "USDCAD"]


class Scraper:

    def __init__(self, pair: str):

        self.pair = pair.strip().lower()
        # Specify URL
        self.url = f"https://www.marketwatch.com/investing/currency/{pair}/download-data?mod=mw_quote_tab"

        # Get HTML from the URL
        self.page = requests.get(self.url).text

        # Parse the HTML using BeautifulSoup
        self.soup = bs(self.page, 'html.parser')

        # Remove duplicates from the soup
        [div.decompose() for div in self.soup.find_all("div", {'class': 'fixed--cell'})]

        # Get Symbol's name
        # self.name = self.soup.find(name="span", class_="company__ticker").string

        # Get current price
        # self.price_now = self.soup.find(name="bg-quote", class_="value", field="Last").string

        # Get table with history quotes
        self.price_history_table = self.soup.find_all(name="div", class_="download-data")

        # Convert the previous table to Pandas DataFrame
        self.df = pd.read_html(str(self.price_history_table))[0]

        # Convert the Date column to datetime format
        self.df['Date'] = pd.to_datetime(self.df['Date'])

        # Set the Date column as index
        self.df = self.df.set_index("Date")

        # Reverse the DataFrame
        self.df = self.df.iloc[::-1]

        # Drop currency symbols (first position)
        self.df["Open"] = self.df["Open"].str[1:]
        self.df["High"] = self.df["High"].str[1:]
        self.df["Low"] = self.df["Low"].str[1:]
        self.df["Close"] = self.df["Close"].str[1:]

        # Convert the columns to float
        self.df = self.df.astype(float)

    # Save the resulting DataFrame to CSV file
    def save(self):
        self.df.to_csv(f"data/{self.pair}.csv")

    # Plot the data
    def plot(self):
        fplt.candlestick_ochl(self.df[['Open', 'Close', 'High', 'Low']])

        # Add Rolling Average Close Price with a period of 5
        mean_close = self.df.Close.rolling(5).mean()
        fplt.plot(mean_close, legend="Average Close Price", color="blue")

        fplt.show()


if __name__ == "__main__":
    for p in PAIRS:
        currency = Scraper(p)
        currency.save()
        currency.plot()
