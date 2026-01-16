import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(ticker: str, period: str = None, lookback_days: int = 0, start_date=None, end_date=None) -> pd.DataFrame:
    """Fetch stock data from Yahoo Finance.
    
    Args:
        ticker: Stock symbol
        period: Time period to fetch (e.g. "1y" for 1 year)
        lookback_days: Additional days to fetch before the period start for MA calculation
        start_date: Start date for data fetching (datetime object)
        end_date: End date for data fetching (datetime object)
    """
    if start_date and end_date:
        # Use date range if provided

        if lookback_days > 0:
            # Calculate the start date with lookback
            start_date = df.index[0] - timedelta(days=lookback_days)
            end_date = df.index[-1]
            
        # Fetch extended data
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    else:
        # First get the regular period data to determine start date
        df = yf.download(ticker, period=period or "1y", auto_adjust=True)
        
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    
    return df

def get_common_stocks() -> list:
    """Get a list of common stocks to display."""
    # This is a basic list of some common stocks. In a real application,
    # you might want to fetch this from an API or database
    common_stocks = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'exchange': 'NASDAQ'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'exchange': 'NASDAQ'},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase & Co.', 'exchange': 'NYSE'},
        {'symbol': 'BAC', 'name': 'Bank of America Corp.', 'exchange': 'NYSE'},
        {'symbol': 'WMT', 'name': 'Walmart Inc.', 'exchange': 'NYSE'},
        {'symbol': 'DIS', 'name': 'The Walt Disney Company', 'exchange': 'NYSE'},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'INTC', 'name': 'Intel Corporation', 'exchange': 'NASDAQ'},
        {'symbol': 'AMD', 'name': 'Advanced Micro Devices Inc.', 'exchange': 'NASDAQ'},
        {'symbol': 'GE', 'name': 'General Electric Company', 'exchange': 'NYSE'},
    ]
    return common_stocks

from threading import Thread
from queue import Queue
import time

def search_stocks_async(query: str, callback) -> None:
    """Asynchronous version of search_stocks that runs in a separate thread.
    
    Args:
        query: The search query string
        callback: Function to call with results when search is complete
    """
    def _search():
        results = search_stocks(query)
        callback(results)
    
    thread = Thread(target=_search)
    thread.daemon = True
    thread.start()

def search_stocks(query: str) -> list:
    """Search for stock tickers matching the query.
    Returns a list of quote dictionaries containing detailed stock information."""
    if not query:
        return get_common_stocks()
        
    # First search in common stocks for exact matches
    stocks = get_common_stocks()
    filtered_stocks = [
        stock for stock in stocks
        if query.upper() in stock['symbol'].upper() or query.upper() in stock['name'].upper()
    ]
    
    # Use the new yf.Search() method to get comprehensive results
    if len(query) >= 1:
        try:
            search_results = yf.Search(query)
            if hasattr(search_results, 'quotes') and search_results.quotes:
                # Return the quotes directly as they contain all needed information
                return search_results.quotes
        except Exception:
            pass
            
    # Fall back to common stocks if Yahoo Finance search fails
    return filtered_stocks