# Stock Chart Viewer

A Python-based desktop application for analyzing stock market data, visualizing price trends with Moving Averages, and predicting future stock prices using various machine learning models. Built with Tkinter and modern UI themes.

## Features

- **Interactive Stock Charts**: Visualize historical stock data with customizable moving average (MA) periods (e.g., 30, 50, 200 days).
- **Price Prediction Models**:
  - **Linear Regression**: Simple trend forecasting.
  - **ARIMA**: Auto-Regressive Integrated Moving Average for time series forecasting.
  - **LSTM**: Long Short-Term Memory neural networks for deep learning-based prediction.
  - **Component Ensemble**: A sophisticated model decomposing data into trend, seasonality, and residuals.
- **Financial Indicators**: View key metrics including Market Cap, P/E Ratio, Revenue Growth, Margins, and more.
- **Modern UI**: Clean interface using `sv-ttk` with support for Light and Dark themes.
- **Asynchronous Data Loading**: smooth user experience with background data fetching.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd stock_utils
    ```

2.  **Create and activate a virtual environment (optional but recommended):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/Mac
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```

2.  **Navigate the Interface:**
    - **Analysis**: Search for a stock symbol (e.g., AAPL, MSFT), set date ranges, and view price charts with Moving Averages.
    - **Prediction**: Switch to the Prediction interface to forecast future prices using different models.
    - **Financial Indicators**: View detailed fundamental data for selected stocks.
    - **Settings**: Toggle between Dark and Light themes.

## Project Structure

```
stock_utils/
├── gui/
│   └── main_window.py    # Main GUI implementation with Tkinter
├── src/
│   ├── analysis.py       # Logic for MAs, predictions, and indicators
│   ├── data_fetcher.py   # Stock data fetching via yfinance
│   └── visualization.py  # Matplotlib plotting functions
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Dependencies

- **yfinance**: Market data downloader.
- **pandas & numpy**: Data manipulation and analysis.
- **matplotlib**: Data visualization.
- **scikit-learn**: Linear regression and preprocessing.
- **tensorflow**: LSTM model implementation.
- **statsmodels & pmdarima**: Time series analysis (ARIMA, decomposition).
- **sv-ttk**: Modern Sun Valley theme for Tkinter.
- **tkcalendar**: Date selection widgets.

## License

[MIT License](LICENSE)
