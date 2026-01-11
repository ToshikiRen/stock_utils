import matplotlib.pyplot as plt
from typing import List
import pandas as pd
import mplcursors

def plot_stock_with_mas(df: pd.DataFrame, ticker: str, windows: List[int]):
    """Create stock chart with moving averages.
    
    Args:
        df: DataFrame with stock data including lookback period
        ticker: Stock symbol
        windows: List of MA periods to plot
    """
    # Get the original period (excluding lookback) by finding the first non-NaN Close value
    start_idx = df['Close'].first_valid_index()
    df_display = df.loc[start_idx:]
    
    # Create figure with dynamic size based on screen resolution
    fig = plt.figure(figsize=(10, 5))  # Default size, will be adjusted by the resize handler
    ax = fig.add_subplot(111)
    
    # Plot main price line
    price_line = ax.plot(df_display.index, df_display["Close"], label="Close", linewidth=2)[0]
    
    # Plot MA lines
    ma_lines = []
    for w in windows:
        line = ax.plot(df_display.index, df_display[f"MA_{w}"], label=f"MA {w}")[0]
        ma_lines.append(line)
    
    ax.set_title(f"{ticker} Moving Averages")
    ax.legend()
    ax.grid(True)
    
    # Enable cursor hover
    cursor = mplcursors.cursor([price_line] + ma_lines, hover=True)
    
    @cursor.connect("add")
    def on_add(sel):
        x, y = sel.target
        # Convert numeric timestamp to pandas datetime using origin='1970-01-01' and unit='D'
        date = pd.to_datetime(x, unit='D', origin='1970-01-01').strftime('%Y-%m-%d')
        # Get the line label
        label = sel.artist.get_label()
        sel.annotation.set_text(f'{label}\nDate: {date}\nValue: {y:.2f}')
        
    return fig