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

def predict_stock_prices(df: pd.DataFrame, days_to_predict: int, model_type: str = "Linear Regression") -> pd.DataFrame:
    """Predict stock prices for the next 'days_to_predict' days.
    
    Args:
        df: DataFrame with historical data (must contain "Close" column).
        days_to_predict: Number of days to predict into the future.
        model_type: Type of model to use ("Linear Regression", "ARIMA", "LSTM").
        
    Returns:
        DataFrame with 'Date' and 'Predicted_Close' columns.
    """
    import numpy as np
    from datetime import timedelta
    
    df = df.copy()
    
    # --- ROBUST DATA EXTRACTION START ---
    try:
        if 'Close' not in df.columns:
            # Fallback if Close is missing (should not happen given get_stock_data guarantees)
            print("Error: 'Close' column missing in DataFrame")
            return pd.DataFrame()

        close_data = df['Close']
        
        # Handle case where yfinance returns a DataFrame for 'Close' (MultiIndex columns)
        if isinstance(close_data, pd.DataFrame):
            # Take the first column (assuming it's the ticker we want)
            close_data = close_data.iloc[:, 0]
            
        # Ensure we have a 1D numpy array of floats
        y_values = close_data.to_numpy(dtype=float).flatten()
        
        # Basic validation
        if len(y_values) < 2:
            print("Error: Not enough data points for prediction")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error extracting data: {e}")
        return pd.DataFrame()
    # --- ROBUST DATA EXTRACTION END ---

    # Prepare future dates
    last_date = df.index[-1]
    future_dates = [last_date + timedelta(days=i) for i in range(1, days_to_predict + 1)]
    
    predictions = []
    
    try:
        if model_type == "Linear Regression":
            from sklearn.linear_model import LinearRegression
            
            # Prepare X (Dates)
            # Use 1D array for Ordinal Dates, then reshape for sklearn
            ordinal_dates = df.index.map(pd.Timestamp.toordinal).to_numpy().reshape(-1, 1)
            
            # Train
            model = LinearRegression()
            model.fit(ordinal_dates, y_values)
            
            # Predict
            future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
            predictions = model.predict(future_ordinals).flatten()
            
        elif model_type == "ARIMA":
            from pmdarima import auto_arima
            import warnings
            
            # Suppress warnings
            warnings.filterwarnings("ignore")
            
            # Fit auto_arima model
            # y_values is guaranteed 1D here
            # trace=False to suppress output, error_action='ignore' to skip errors
            model = auto_arima(y_values, start_p=1, start_q=1,
                             max_p=5, max_q=5, m=1,
                             start_P=0, seasonal=False,
                             d=1, D=1, trace=False,
                             error_action='ignore',  
                             suppress_warnings=True, 
                             stepwise=True)
            
            # Predict
            output = model.predict(n_periods=days_to_predict)
            predictions = output if isinstance(output, np.ndarray) else output.values
            predictions = predictions.flatten()
            
        elif model_type == "LSTM":
            import tensorflow as tf
            from sklearn.preprocessing import MinMaxScaler
            import logging
            tf.get_logger().setLevel(logging.ERROR)
            
            # Reproducibility
            tf.random.set_seed(42)
            np.random.seed(42)
            
            # Reshape for scalar (N, 1)
            data = y_values.reshape(-1, 1)
            
            # Normalize
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data)
            
            # Create sequences
            look_back = 60
            if len(scaled_data) <= look_back:
                # Fallback if not enough data
                return predict_stock_prices(df, days_to_predict, "Linear Regression")
                
            X_train, y_train = [], []
            for i in range(look_back, len(scaled_data)):
                X_train.append(scaled_data[i-look_back:i, 0])
                y_train.append(scaled_data[i, 0])
                
            X_train, y_train = np.array(X_train), np.array(y_train)
            X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
            
            # Build simple LSTM model
            model = tf.keras.Sequential([
                tf.keras.layers.Input(shape=(X_train.shape[1], 1)),
                tf.keras.layers.LSTM(units=50, return_sequences=False),
                tf.keras.layers.Dense(1)
            ])
            
            model.compile(optimizer='adam', loss='mean_squared_error')
            
            # Train
            model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=0)
            
            # Predict future
            current_batch = scaled_data[-look_back:].reshape(1, look_back, 1)
            predicted_prices = []
            
            for i in range(days_to_predict):
                pred_result = model.predict(current_batch, verbose=0)
                current_pred = float(pred_result[0, 0]) # Ensure scalar float
                predicted_prices.append(current_pred)
                
                # Update batch
                new_pred_reshaped = np.array([[[current_pred]]])
                current_batch = np.append(current_batch[:, 1:, :], new_pred_reshaped, axis=1)
                
            # Inverse transform
            predictions = scaler.inverse_transform(np.array(predicted_prices).reshape(-1, 1)).flatten()
            
        elif model_type == "Component Ensemble":
            from statsmodels.tsa.seasonal import seasonal_decompose
            from sklearn.linear_model import LinearRegression
            from pmdarima import auto_arima
            import warnings
            warnings.filterwarnings("ignore")
            
            def _detect_period(data):
                """Detect dominant period using FFT."""
                try:
                    # Remove DC component (mean)
                    data_centered = data - np.mean(data)
                    
                    # Compute FFT
                    fft = np.fft.rfft(data_centered)
                    frequencies = np.fft.rfftfreq(len(data_centered))
                    
                    # Magnitude spectrum
                    magnitudes = np.abs(fft)
                    
                    # Ignore zero frequency (already removed mean but good to be safe)
                    magnitudes[0] = 0
                    
                    # Find peak frequency
                    peak_freq_idx = np.argmax(magnitudes)
                    peak_freq = frequencies[peak_freq_idx]
                    
                    if peak_freq == 0:
                        return 5 # Default
                    
                    period = int(round(1 / peak_freq))
                    
                    # Sanity checks
                    if period < 2: return 5
                    if period > len(data) // 2: return 5
                    
                    return period
                except:
                    return 5

            # 1. Decompose
            # Detect period dynamically
            period = _detect_period(y_values)
            # print(f"Detected period: {period}") # Debug
            
            if len(y_values) < 2 * period:
                # Fallback to Linear Regression if series too short
                return predict_stock_prices(df, days_to_predict, "Linear Regression")

            decomposition = seasonal_decompose(y_values, model='additive', period=period)
            
            trend = decomposition.trend
            seasonal = decomposition.seasonal
            resid = decomposition.resid
            
            # 2. Predict Trend (Linear)
            # Remove NaNs generated by decomposition
            valid_idx = ~np.isnan(trend)
            trend_clean = trend[valid_idx]
            
            # Create X indices for trend
            X_indices = np.arange(len(y_values))
            X_trend_train = X_indices[valid_idx].reshape(-1, 1)
            
            trend_model = LinearRegression()
            trend_model.fit(X_trend_train, trend_clean)
            
            # Forecast Trend
            future_indices = np.arange(len(y_values), len(y_values) + days_to_predict).reshape(-1, 1)
            trend_forecast = trend_model.predict(future_indices)
            
            # 3. Predict Seasonal (Repeat cycle)
            last_season = seasonal[-period:] # Grab last cycle
            # Tile it to cover the future days
            repetitions = (days_to_predict // period) + 1
            seasonal_forecast = np.tile(last_season, repetitions)[:days_to_predict]
            
            # 4. Predict Residuals (Auto-ARIMA)
            valid_resid_idx = ~np.isnan(resid)
            resid_clean = resid[valid_resid_idx]
            
            if len(resid_clean) > 10: # Only run ARIMA if enough data
                resid_model = auto_arima(resid_clean, start_p=1, start_q=1,
                                       max_p=3, max_q=3, m=1, # Non-seasonal ARIMA for residuals
                                       d=None, trace=False,
                                       error_action='ignore',
                                       suppress_warnings=True,
                                       stepwise=True)
                resid_forecast = resid_model.predict(n_periods=days_to_predict)
                # handle potential series output
                resid_forecast = resid_forecast if isinstance(resid_forecast, np.ndarray) else resid_forecast.values
            else:
                 resid_forecast = np.zeros(days_to_predict)

            # 5. Combine
            predictions = trend_forecast + seasonal_forecast + resid_forecast
            
        else:
            return pd.DataFrame()
            
        # Create result DataFrame
        pred_df = pd.DataFrame({
            'Predicted_Close': predictions
        }, index=future_dates)
        
        return pred_df
        
    except Exception as e:
        print(f"Error in prediction ({model_type}): {str(e)}")
        # Return empty on error
        return pd.DataFrame()