import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.data_fetcher import get_stock_data, search_stocks, search_stocks_async
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
        self.load_initial_stocks()  # Load stocks when app starts
        
    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, padx=10, fill='x')
        
        ttk.Label(search_frame, text="Filter stocks:").pack(side='left', padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.on_search_change)  # Add callback for real-time filtering
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side='left', fill='x', expand=True)
        
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
        default_periods = [30, 50, 200]
        
        for i, period in enumerate(default_periods):
            frame = ttk.Frame(ma_frame)
            frame.pack(side='left', padx=5, pady=5)
            
            entry = ttk.Entry(frame, width=5)
            entry.insert(0, str(period))
            entry.pack(side='left', padx=2)
            
            ttk.Label(frame, text="days").pack(side='left')
            self.ma_entries.append(entry)
        
        # Stock list
        self.stock_list = ttk.Treeview(self.root, columns=('Symbol', 'Name', 'Exchange'), show='headings', height=5)
        self.stock_list.heading('Symbol', text='Symbol')
        self.stock_list.heading('Name', text='Name')
        self.stock_list.heading('Exchange', text='Exchange')
        self.stock_list.pack(pady=5, padx=5, fill='both')
        
        # Bind double-click event
        self.stock_list.bind('<Double-1>', self.on_stock_select)
        
        # Chart frame with proper weight configuration
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(pady=10, padx=10, fill='both', expand=True)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.chart_frame.grid_rowconfigure(0, weight=1)
        self.chart_frame.grid_columnconfigure(0, weight=1)
        
    def load_initial_stocks(self):
        """Load and display the initial list of stocks."""
        self.update_stock_list([])  # Clear the list first
        search_stocks_async("", self.update_stock_list)  # Load asynchronously
        
    def update_stock_list(self, results):
        """Update the stock list with the given results."""
        # Schedule the update on the main thread to avoid threading issues
        self.root.after(0, self._update_stock_list_internal, results)
    
    def _update_stock_list_internal(self, results):
        """Internal method to actually update the stock list."""
        # Clear previous results
        for item in self.stock_list.get_children():
            self.stock_list.delete(item)
            
        # Add new results
        for result in results:
            # Handle both old format (common_stocks) and new format (yf.Search quotes)
            if 'name' in result:
                # Old format from common_stocks
                name = result['name']
                exchange = result['exchange']
                symbol = result['symbol']
            else:
                # New format from yf.Search().quotes
                name = result.get('longname', result.get('shortname', 'Unknown'))
                exchange = result.get('exchDisp', result.get('exchange', 'Unknown'))
                symbol = result.get('symbol', '')
                
            self.stock_list.insert('', 'end', values=(
                symbol,
                name,
                exchange
            ))
            
    def on_search_change(self, *args):
        """Handle real-time filtering as user types."""
        query = self.search_var.get()
        search_stocks_async(query, self.update_stock_list)
        
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
            windows = [30, 50, 200]  # Default if no valid periods
            
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
        
        # Configure canvas to be responsive
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True)
        
        # Make the figure responsive to window resize
        def on_resize(event):
            # Get the current size of the chart frame
            width = self.chart_frame.winfo_width()
            height = self.chart_frame.winfo_height()
            
            # Update figure size (in inches, assuming 100 DPI)
            fig.set_size_inches(width/100, height/100)
            canvas.draw()
        
        # Bind the resize event
        self.chart_frame.bind('<Configure>', on_resize)
        
    def on_stock_select(self, event):
        """Handle stock selection from the list."""
        selected_item = self.stock_list.selection()[0]
        symbol = self.stock_list.item(selected_item)['values'][0]
        self.show_chart(symbol)