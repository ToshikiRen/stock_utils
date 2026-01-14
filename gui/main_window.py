import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from src.data_fetcher import get_stock_data, search_stocks, search_stocks_async
from src.analysis import calculate_moving_averages, get_financial_indicators
from src.visualization import plot_stock_with_mas
from datetime import datetime, timedelta
from tkcalendar import DateEntry  # You'll need to install this package
import pandas as pd
import threading
import sv_ttk

class StockChartApp:
    def __init__(self, root):
        self.root = root
        sv_ttk.set_theme("light")
        self.root.title("Stock Chart Viewer")
        
        # Theme settings
        self.theme_var = tk.BooleanVar(value=False)  # False = Light theme, True = Dark theme
        self.current_theme = "light"
        
        self.setup_menu()
        self.setup_ui()
        self.load_initial_stocks()  # Load stocks when app starts
        
    def setup_menu(self):
        # Create the menu bar
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        
        # Analysis Menu
        analysis_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Analysis", menu=analysis_menu)
        analysis_menu.add_command(label="Moving Average Analysis", command=self.show_main_interface)
        analysis_menu.add_command(label="Financial Indicators", command=self.show_financial_indicators)
        
        # Settings Menu
        settings_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_checkbutton(label="Dark Theme", variable=self.theme_var, command=self.toggle_theme)
    
    def show_loading(self, text="Applying theme..."):
        self.loading = tk.Toplevel(self.root)
        self.loading.overrideredirect(True)
        self.loading.attributes("-topmost", True)

        w, h = 260, 90
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - w // 2
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - h // 2
        self.loading.geometry(f"{w}x{h}+{x}+{y}")

        frame = tk.Frame(self.loading, bg="#1e1e1e", bd=2, relief="ridge")
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text=text,
            fg="white",
            bg="#1e1e1e",
            font=("Segoe UI", 10)
        ).pack(expand=True)

        # Force draw immediately
        self.loading.update_idletasks()

    def hide_loading(self):
        if hasattr(self, "loading"):
            self.loading.destroy()
            del self.loading

    def toggle_theme(self):
        self.show_loading("Switching theme...")

        def apply_theme():
            if self.theme_var.get():  # Dark
                sv_ttk.set_theme("dark")
                plt.style.use("dark_background")
                self.current_theme = "dark"
            else:  # Light
                sv_ttk.set_theme("light")
                plt.style.use("default")
                self.current_theme = "light"
            
             # Refresh any existing chart
            if hasattr(self, 'chart_frame') and len(self.chart_frame.winfo_children()) > 0:
                selected_items = self.stock_list.selection()
                if selected_items:
                    symbol = self.stock_list.item(selected_items[0])['values'][0]
                    self.show_chart(symbol)

            # Hide loading AFTER theme is applied
            self.hide_loading()

        # Let loading screen render first
        self.root.after(1000, apply_theme)

            
       
            
    def show_financial_indicators(self):

        def build_ui():
            # Clear the main container
            for widget in self.main_container.winfo_children():
                widget.destroy()

            # Search frame
            search_frame = ttk.Frame(self.main_container)
            search_frame.pack(pady=10, padx=10, fill='x')

            ttk.Label(search_frame, text="Filter stocks:").pack(side='left', padx=5)

            self.search_var = tk.StringVar()
            self.search_var.trace_add('write', self.on_search_change)
            self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
            self.search_entry.pack(side='left', fill='x', expand=True)

            # Stock list
            self.stock_list = ttk.Treeview(
                self.main_container,
                columns=('Symbol', 'Name', 'Exchange'),
                show='headings',
                height=5
            )
            self.stock_list.heading('Symbol', text='Symbol')
            self.stock_list.heading('Name', text='Name')
            self.stock_list.heading('Exchange', text='Exchange')
            self.stock_list.pack(pady=5, padx=5, fill='x')

            self.stock_list.bind(
                '<<TreeviewSelect>>',
                self.on_stock_select_for_indicators
            )

            # Indicators frame
            self.indicators_frame = ttk.Frame(self.main_container)
            self.indicators_frame.pack(pady=10, padx=10, fill='both', expand=True)

            # Notebook
            self.indicators_notebook = ttk.Notebook(self.indicators_frame)
            self.indicators_notebook.pack(fill='both', expand=True)

            # Tabs
            self.market_tab = ttk.Frame(self.indicators_notebook)
            self.financial_tab = ttk.Frame(self.indicators_notebook)
            self.growth_tab = ttk.Frame(self.indicators_notebook)
            self.technical_tab = ttk.Frame(self.indicators_notebook)

            self.indicators_notebook.add(self.market_tab, text='Market Data')
            self.indicators_notebook.add(self.financial_tab, text='Financial Metrics')
            self.indicators_notebook.add(self.growth_tab, text='Growth Metrics')
            self.indicators_notebook.add(self.technical_tab, text='Technical Indicators')
           
            # Load stock data LAST
            self.load_initial_stocks()

        # Let loading screen render first
        self.root.after(0, build_ui)

        
    def on_stock_select_for_indicators(self, event):
        """Handle stock selection for financial indicators view."""
        selected_items = self.stock_list.selection()
        if not selected_items:
            return
            
        symbol = self.stock_list.item(selected_items[0])['values'][0]
        self.show_financial_data(symbol)
        
    def show_financial_data(self, ticker):
        """Display financial indicators for the selected stock."""
        # Clear previous data
        for tab in [self.market_tab, self.financial_tab, self.growth_tab, self.technical_tab]:
            for widget in tab.winfo_children():
                widget.destroy()
                
        # Create loading labels
        loading_labels = []
        for tab in [self.market_tab, self.financial_tab, self.growth_tab, self.technical_tab]:
            label = ttk.Label(tab, text="Loading data...", anchor='center')
            label.pack(expand=True, fill='both', padx=10, pady=10)
            loading_labels.append(label)
        
        def fetch_and_display():
            # Get financial indicators in background thread
            indicators = get_financial_indicators(ticker)
            
            # Schedule UI update on main thread
            self.root.after(0, lambda: self._update_financial_display(indicators, loading_labels))
        
        # Start background thread
        thread = threading.Thread(target=fetch_and_display)
        thread.daemon = True  # Thread will be terminated when main program exits
        thread.start()
        
    def _update_financial_display(self, indicators, loading_labels):
        """Update the UI with fetched financial data."""
        # Remove loading labels
        for label in loading_labels:
            label.destroy()
                
        # Market Data Tab
        market_data = {
            'Market Cap': indicators.get('Market Cap', 'N/A'),
            'P/E Ratio': indicators.get('P/E Ratio', 'N/A'),
            'Forward P/E': indicators.get('Forward P/E', 'N/A'),
            'PEG Ratio': indicators.get('PEG Ratio', 'N/A'),
            'Price/Book': indicators.get('Price/Book', 'N/A'),
            'Dividend Yield': indicators.get('Dividend Yield', 'N/A'),
        }
        
        # Financial Metrics Tab
        financial_metrics = {
            'Revenue (TTM)': indicators.get('Revenue (TTM)', 'N/A'),
            'Profit Margin': indicators.get('Profit Margin', 'N/A'),
            'Operating Margin': indicators.get('Operating Margin', 'N/A'),
            'ROE': indicators.get('ROE', 'N/A'),
            'ROA': indicators.get('ROA', 'N/A'),
            'Current Ratio': indicators.get('Current Ratio', 'N/A'),
        }
        
        # Growth Metrics Tab
        growth_metrics = {
            'Revenue Growth': indicators.get('Revenue Growth', 'N/A'),
            'Earnings Growth': indicators.get('Earnings Growth', 'N/A'),
        }
        
        # Technical Indicators Tab
        technical_indicators = {
            'Beta': indicators.get('Beta', 'N/A'),
            '52 Week High': indicators.get('52 Week High', 'N/A'),
            '52 Week Low': indicators.get('52 Week Low', 'N/A'),
            '50 Day MA': indicators.get('50 Day MA', 'N/A'),
            '200 Day MA': indicators.get('200 Day MA', 'N/A'),
        }
        
        # Helper function to create indicator display
        def create_indicator_display(parent, data):
            # Create a frame for the grid layout
            grid_frame = ttk.Frame(parent)
            grid_frame.pack(fill='both', expand=True, padx=10, pady=5)

            # Configure grid columns with weights
            grid_frame.grid_columnconfigure(1, weight=1)  # Value column should expand

            # Style for headers
            header_style = {'font': ('TkDefaultFont', 10, 'bold')}
            value_style = {'font': ('TkDefaultFont', 10)}

            for i, (key, value) in enumerate(data.items()):
                # Create indicator frame
                frame = ttk.Frame(grid_frame)
                frame.grid(row=i, column=0, columnspan=2, sticky='ew', pady=2)
                frame.grid_columnconfigure(1, weight=1)

                # Label with key
                label = ttk.Label(frame, text=f"{key}:", anchor='w', **header_style)
                label.grid(row=0, column=0, padx=(5, 10), sticky='w')

                # Value with right alignment
                value_label = ttk.Label(frame, text=str(value), anchor='e', **value_style)
                value_label.grid(row=0, column=1, padx=5, sticky='e')

                # Add separator line
                if i < len(data) - 1:  # Don't add separator after last item
                    separator = ttk.Separator(grid_frame, orient='horizontal')
                    separator.grid(row=i+1, column=0, columnspan=2, sticky='ew', pady=5)
                
        # Create displays for each tab
        create_indicator_display(self.market_tab, market_data)
        create_indicator_display(self.financial_tab, financial_metrics)
        create_indicator_display(self.growth_tab, growth_metrics)
        create_indicator_display(self.technical_tab, technical_indicators)
        
    def setup_ui(self):
        # Main container frame
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True)
        
        # Initially show the MA analysis interface
        self.show_main_interface()
        
    def show_main_interface(self):

        def build_ui():
            # Clear the main container
            for widget in self.main_container.winfo_children():
                widget.destroy()

            # Search frame
            search_frame = ttk.Frame(self.main_container)
            search_frame.pack(pady=10, padx=10, fill='x')

            ttk.Label(search_frame, text="Filter stocks:").pack(side='left', padx=5)

            self.search_var = tk.StringVar()
            self.search_var.trace_add('write', self.on_search_change)
            self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
            self.search_entry.pack(side='left', fill='x', expand=True)

            # Date Selection
            date_frame = ttk.LabelFrame(self.main_container, text="Date Range")
            date_frame.pack(pady=5, padx=10, fill='x')

            # Start date
            start_frame = ttk.Frame(date_frame)
            start_frame.pack(side='left', padx=5, pady=5)
            ttk.Label(start_frame, text="Start Date:").pack(side='left', padx=2)

            self.start_date = DateEntry(
                start_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.date_entries = [self.start_date]
            self.start_date.pack(side='left', padx=2)

            # End date
            end_frame = ttk.Frame(date_frame)
            end_frame.pack(side='left', padx=5, pady=5)
            ttk.Label(end_frame, text="End Date:").pack(side='left', padx=2)

            self.end_date = DateEntry(
                end_frame,
                width=12,
                background='darkblue',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.date_entries.append(self.end_date)
            self.end_date.pack(side='left', padx=2)

            self.end_date.set_date(datetime.now())
            self.start_date.set_date(datetime.now() - timedelta(days=365))

            # MA Config
            ma_frame = ttk.LabelFrame(self.main_container, text="Moving Average Periods")
            ma_frame.pack(pady=5, padx=10, fill='x')

            self.ma_entries = []
            for period in [30, 50, 200]:
                frame = ttk.Frame(ma_frame)
                frame.pack(side='left', padx=5, pady=5)

                entry = ttk.Entry(frame, width=5)
                entry.insert(0, str(period))
                entry.pack(side='left', padx=2)

                ttk.Label(frame, text="days").pack(side='left')
                self.ma_entries.append(entry)

            # Stock list
            self.stock_list = ttk.Treeview(
                self.main_container,
                columns=('Symbol', 'Name', 'Exchange'),
                show='headings',
                height=5
            )
            self.stock_list.heading('Symbol', text='Symbol')
            self.stock_list.heading('Name', text='Name')
            self.stock_list.heading('Exchange', text='Exchange')
            self.stock_list.pack(pady=5, padx=5, fill='both')

            self.stock_list.bind('<Double-1>', self.on_stock_select)

            # Chart frame
            self.chart_frame = ttk.Frame(self.main_container)
            self.chart_frame.pack(pady=10, padx=10, fill='both', expand=True)
            
            # Load data LAST
            self.load_initial_stocks()

        # Let loading screen render first
        self.root.after(0, build_ui)

    
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