from typing import List
import pandas as pd

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