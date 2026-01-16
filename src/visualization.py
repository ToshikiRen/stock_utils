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
    
    # Detect theme based on text color
    text_color = plt.rcParams.get('text.color', 'black')
    is_dark = text_color == 'white' or text_color == '#ffffff'

    # Define colors based on theme
    if is_dark:
        price_color = '#00ffff'  # Cyan for price in dark mode
        ma_colors = ['#ffff00', '#ff00ff', '#00ff00', '#ff9900', '#ffffff']  # Yellow, Magenta, Lime, Orange, White
        grid_color = '#444444'
    else:
        price_color = '#1f77b4'  # Standard Blue
        ma_colors = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']  # Standard palette
        grid_color = '#e5e5e5'

    # Plot main price line
    price_line = ax.plot(df_display.index, df_display["Close"], label="Close", linewidth=2, color=price_color)[0]
    
    # Plot MA lines
    ma_lines = []
    for i, w in enumerate(windows):
        color = ma_colors[i % len(ma_colors)]
        line = ax.plot(df_display.index, df_display[f"MA_{w}"], label=f"MA {w}", linewidth=1.5, color=color)[0]
        ma_lines.append(line)
    
    ax.set_title(f"{ticker} Moving Averages")
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, linestyle='--', alpha=0.6, color=grid_color)
    
    # Enable cursor hover
    cursor = mplcursors.cursor([price_line] + ma_lines, hover=True)
    
    @cursor.connect("add")
    def on_add(sel):
        x, y = sel.target

        date = pd.to_datetime(x, unit='D', origin='1970-01-01').strftime('%Y-%m-%d')
       
        label = sel.artist.get_label()
        sel.annotation.set_text(f'{label}\nDate: {date}\nValue: {y:.2f}')
        
        # Style based on theme (using pre-calculated is_dark)
        if is_dark:
            sel.annotation.get_bbox_patch().set(fc='#333333', alpha=0.9, edgecolor='white')
            sel.annotation.set_color('white')
            sel.annotation.arrow_patch.set(arrowstyle='-', color='white')
        else:
            sel.annotation.get_bbox_patch().set(fc='white', alpha=0.9, edgecolor='black')
            sel.annotation.set_color('black')
            sel.annotation.arrow_patch.set(arrowstyle='-', color='black')
        
    return fig

def plot_prediction(historical_df: pd.DataFrame, prediction_df: pd.DataFrame, ticker: str, model_name: str) -> plt.Figure:
    """Plot historical and predicted stock data.
    
    Args:
        historical_df: DataFrame with historical data.
        prediction_df: DataFrame with predicted data.
        ticker: Stock ticker symbol.
        model_name: Name of the model used for prediction.
        
    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    # Detect theme
    text_color = plt.rcParams.get('text.color', 'black')
    is_dark = text_color == 'white' or text_color == '#ffffff'
    
    if is_dark:
        hist_color = '#00ffff'  # Cyan
        pred_color = '#ff9900'  # Bright Orange
        grid_color = '#444444'
    else:
        hist_color = '#1f77b4'  # Blue
        pred_color = '#ff7f0e'  # Orange
        grid_color = '#e5e5e5'

    hist_line = ax.plot(historical_df.index, historical_df['Close'], label='Historical', color=hist_color)
    pred_line = ax.plot(prediction_df.index, prediction_df['Predicted_Close'], label=f'Prediction ({model_name})', color=pred_color, linestyle='--')
    
    # Connect the last historical point with the first prediction point for visual continuity
    if not historical_df.empty and not prediction_df.empty:
        last_hist_date = historical_df.index[-1]
        last_hist_price = historical_df['Close'].iloc[-1].item()
        
        first_pred_date = prediction_df.index[0]
        first_pred_price = prediction_df['Predicted_Close'].iloc[0]
        # print(last_hist_date, first_pred_date, last_hist_price, first_pred_price)
        ax.plot([last_hist_date, first_pred_date], [last_hist_price, first_pred_price], color=pred_color, linestyle='--')

    ax.set_title(f"{ticker} Price Prediction - {model_name}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle='--', alpha=0.6, color=grid_color)
    ax.legend(frameon=True, fancybox=True, shadow=True)

    # Improve formatting
    fig.autofmt_xdate()
    
    cursor = mplcursors.cursor([hist_line[0], pred_line[0]], hover=True)
    
    @cursor.connect("add")
    def on_add(sel):
        x, y = sel.target

        date = pd.to_datetime(x, unit='D', origin='1970-01-01').strftime('%Y-%m-%d')
       
        label = sel.artist.get_label()
        sel.annotation.set_text(f'{label}\nDate: {date}\nValue: {y:.2f}')
        
        # Style based on theme
        if is_dark:
            sel.annotation.get_bbox_patch().set(fc='#333333', alpha=0.9, edgecolor='white')
            sel.annotation.set_color('white')
            sel.annotation.arrow_patch.set(arrowstyle='-', color='white')
        else:
            sel.annotation.get_bbox_patch().set(fc='white', alpha=0.9, edgecolor='black')
            sel.annotation.set_color('black')
            sel.annotation.arrow_patch.set(arrowstyle='-', color='black')
        
    return fig