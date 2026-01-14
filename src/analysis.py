from typing import List, Dict
import pandas as pd
import yfinance as yf

def calculate_moving_averages(df: pd.DataFrame, windows: List[int]) -> pd.DataFrame:
    """Calculate moving averages for given windows.
    
    All moving averages will start from the same point where there's enough data
    for the longest moving average window.
    """
    df = df.copy()
    
    # Sort windows to find the longest one
    sorted_windows = sorted(windows)
    max_window = sorted_windows[-1]
    
    # Calculate all MAs
    for w in windows:
        df[f"MA_{w}"] = df["Close"].rolling(window=w).mean()
    
    # Only keep rows where we have data for all MAs
    # This means starting from the point where the longest MA has data
    df = df.dropna()
    
    return df

def get_financial_indicators(ticker: str) -> Dict:
    """Fetch key financial indicators for a given stock ticker.
    
    Returns:
        Dictionary containing financial indicators and their values.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get financial statements
        balance_sheet = stock.balance_sheet
        income_stmt = stock.income_stmt
        cash_flow = stock.cash_flow
        
        indicators = {
            # Market Data
            'Market Cap': info.get('marketCap', 'N/A'),
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'Forward P/E': info.get('forwardPE', 'N/A'),
            'PEG Ratio': info.get('pegRatio', 'N/A'),
            'Price/Book': info.get('priceToBook', 'N/A'),
            'Dividend Yield': info.get('dividendYield', 'N/A') / 100 if isinstance(info.get('dividendYield'), (int, float)) else 'N/A',
            
            # Financial Metrics
            'Revenue (TTM)': info.get('totalRevenue', 'N/A'),
            'Profit Margin': info.get('profitMargins', 'N/A'),
            'Operating Margin': info.get('operatingMargins', 'N/A'),
            'ROE': info.get('returnOnEquity', 'N/A'),
            'ROA': info.get('returnOnAssets', 'N/A'),
            'Current Ratio': info.get('currentRatio', 'N/A'),
            
            # Growth Metrics
            'Revenue Growth': info.get('revenueGrowth', 'N/A'),
            'Earnings Growth': info.get('earningsGrowth', 'N/A'),
            
            # Additional Info
            'Beta': info.get('beta', 'N/A'),
            '52 Week High': info.get('fiftyTwoWeekHigh', 'N/A'),
            '52 Week Low': info.get('fiftyTwoWeekLow', 'N/A'),
            '50 Day MA': info.get('fiftyDayAverage', 'N/A'),
            '200 Day MA': info.get('twoHundredDayAverage', 'N/A'),
        }
        
        # Format numeric values
        for key, value in indicators.items():
            if isinstance(value, float):
                # Format with appropriate units
                if key == 'Dividend Yield' or 'Margin' in key or 'Growth' in key:
                    indicators[key] = f"{value:.2%}"  # Percentage format
                elif 'Ratio' in key:
                    indicators[key] = f"{value:.2f}x"  # Ratio format with 'x'
                elif key in ['ROE', 'ROA']:
                    indicators[key] = f"{value:.2%}"  # Percentage format for returns
                elif key in ['52 Week High', '52 Week Low', '50 Day MA', '200 Day MA']:
                    indicators[key] = f"${value:.2f}"  # Dollar format for prices
                elif key == 'Beta':
                    indicators[key] = f"{value:.2f}β"  # Beta symbol
                else:
                    indicators[key] = f"{value:.2f}"  # Default format
            elif key == 'Market Cap' or key == 'Revenue (TTM)':
                value = float(value)
                print(value)
                if value > 1_000_000_000_000:
                    indicators[key] = f"${value/1_000_000_000_000:.2f} trillions"  # Billions
                elif value > 1_000_000_000:
                    indicators[key] = f"${value/1_000_000_000:.2f} billions"  # Billions
                elif value > 1_000_000:
                    indicators[key] = f"${value/1_000_000:.2f} millions"  # Millions
                else:
                    indicators[key] = f"${value:.2f}"  # Direct dollar amount
                    
        return indicators
    except Exception as e:
        print(f"Error fetching financial indicators for {ticker}: {str(e)}")
        return {}