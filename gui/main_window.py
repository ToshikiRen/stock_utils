import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.data_fetcher import get_stock_data, search_stocks
from src.analysis import calculate_moving_averages
from src.visualization import plot_stock_with_mas
from datetime import datetime, timedelta
from tkcalendar import DateEntry  # You'll need to install this package
import pandas as pd


class StockChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Chart Viewer")
        self.setup_ui()
        
    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, padx=10, fill='x')
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side='left', fill='x', expand=True)
        
        search_button = ttk.Button(search_frame, text="Search", command=self.search_stock)
        search_button.pack(side='right', padx=5)
        
        # Date Selection frame
        date_frame = ttk.LabelFrame(self.root, text="Date Range")
        date_frame.pack(pady=5, padx=10, fill='x')
        
        # Start date
        start_frame = ttk.Frame(date_frame)
        start_frame.pack(side='left', padx=5, pady=5)
        ttk.Label(start_frame, text="Start Date:").pack(side='left', padx=2)
        self.start_date = DateEntry(start_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='yyyy-mm-dd')
        self.start_date.pack(side='left', padx=2)
        
        # End date
        end_frame = ttk.Frame(date_frame)
        end_frame.pack(side='left', padx=5, pady=5)
        ttk.Label(end_frame, text="End Date:").pack(side='left', padx=2)
        self.end_date = DateEntry(end_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2,
                                date_pattern='yyyy-mm-dd')
        self.end_date.pack(side='left', padx=2)
        
        # Set default dates
        self.end_date.set_date(datetime.now())
        self.start_date.set_date(datetime.now() - timedelta(days=365))
        
        # MA Configuration frame
        ma_frame = ttk.LabelFrame(self.root, text="Moving Average Periods")
        ma_frame.pack(pady=5, padx=10, fill='x')
        
        # Default MA periods
        self.ma_entries = []
        default_periods = [20, 50, 200]
        
        for i, period in enumerate(default_periods):
            frame = ttk.Frame(ma_frame)
            frame.pack(side='left', padx=5, pady=5)
            
            entry = ttk.Entry(frame, width=5)
            entry.insert(0, str(period))
            entry.pack(side='left', padx=2)
            
            ttk.Label(frame, text="days").pack(side='left')
            self.ma_entries.append(entry)
        
        # Stock list
        self.stock_list = ttk.Treeview(self.root, columns=('Symbol', 'Name', 'Exchange'), show='headings')
        self.stock_list.heading('Symbol', text='Symbol')
        self.stock_list.heading('Name', text='Name')
        self.stock_list.heading('Exchange', text='Exchange')
        self.stock_list.pack(pady=10, padx=10, fill='both')
        
        # Bind double-click event
        self.stock_list.bind('<Double-1>', self.on_stock_select)
        
        # Chart frame
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
    def search_stock(self):
        query = self.search_var.get()
        results = search_stocks(query)
        
        # Clear previous results
        for item in self.stock_list.get_children():
            self.stock_list.delete(item)
            
        # Add new results
        for result in results:
            self.stock_list.insert('', 'end', values=(
                result['symbol'],
                result['name'],
                result['exchange']
            ))
            
    def show_chart(self, ticker):
        # Get MA periods from entries
        windows = []
        for entry in self.ma_entries:
            try:
                period = int(entry.get())
                if period > 0:
                    windows.append(period)
            except ValueError:
                continue
        
        if not windows:
            windows = [20, 50, 200]  # Default if no valid periods
            
        # Get maximum MA period for historical data
        max_period = max(windows)
        
        # Get selected dates
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()
        
        # Add lookback period to start date to ensure we have enough data for MA calculation
        lookback_start = start_date - timedelta(days=max_period * 2)  # * 2 to account for weekends/holidays
        
        # Get stock data with the extended date range
        df = get_stock_data(ticker, start_date=lookback_start, end_date=end_date)
        
        # Calculate MAs
        df = calculate_moving_averages(df, windows)
        
        # Filter to selected date range after MA calculation
        # Convert datetime.date to pandas Timestamp for comparison
        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)
        df = df[df.index >= start_ts]
        df = df[df.index <= end_ts]
        
        fig = plot_stock_with_mas(df, ticker, windows)
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
            
        # Show new chart
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.chart_frame)
        toolbar.update()
        
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def on_stock_select(self, event):
        """Handle stock selection from the list."""
        selected_item = self.stock_list.selection()[0]
        symbol = self.stock_list.item(selected_item)['values'][0]
        self.show_chart(symbol)