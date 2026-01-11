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
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    else:
        # First get the regular period data to determine start date
        df = yf.download(ticker, period=period or "1y", auto_adjust=True)
        
    if df.empty:
        raise ValueError(f"No data found for ticker {ticker}")
    
    if lookback_days > 0 and not start_date:
        # Calculate the start date with lookback
        start_date = df.index[0] - timedelta(days=lookback_days)
        end_date = df.index[-1]
        
        # Fetch extended data
        df = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)
    
    return df

def search_stocks(query: str) -> list:
    """Search for stock tickers matching the query."""
    ticker = yf.Ticker(query)
    try:
        info = ticker.info
        return [{
            'symbol': query,
            'name': info.get('longName', ''),
            'exchange': info.get('exchange', '')
        }]
    except:
        return []