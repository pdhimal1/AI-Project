"""
Stock Predictor - Scrollable GUI with Resizable Chart
A clean, user-friendly interface with scrolling and resizable chart.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import predictor as pred
import get_historical as gh
import normalize as scale
import company_name as cn
import trading_day as trading_cal


class ScrollableStockGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Price Predictor")
        self.root.configure(bg='#f0f0f0')
        
        # Colors
        self.colors = {
            'bg': '#f0f0f0',
            'card': '#ffffff',
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'text': '#333333',
            'text_light': '#666666',
            'success': '#4CAF50',
            'border': '#e0e0e0'
        }
        
        self.root.minsize(800, 800)
        
        # Make window resizable
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        self.create_main_layout()
        self.prediction_in_progress = False
        
    def create_main_layout(self):
        """Create scrollable main layout"""
        # Create canvas and scrollbar for main window
        main_canvas = tk.Canvas(self.root, bg=self.colors['bg'])
        main_canvas.grid(row=0, column=0, sticky='nsew')
        
        scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=main_canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create main frame inside canvas
        self.main_frame = tk.Frame(main_canvas, bg=self.colors['bg'])
        canvas_window = main_canvas.create_window((0, 0), window=self.main_frame, anchor='nw')
        
        # Configure canvas scrolling
        def configure_canvas(event):
            main_canvas.configure(scrollregion=main_canvas.bbox('all'))
            main_canvas.itemconfig(canvas_window, width=event.width)
        
        self.main_frame.bind('<Configure>', configure_canvas)
        main_canvas.bind('<Configure>', lambda e: main_canvas.itemconfig(canvas_window, width=e.width))
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
        main_canvas.bind_all('<MouseWheel>', on_mousewheel)
        
        # Create header
        self.create_header()
        
        # Create content area
        self.create_content()
        
    def create_header(self):
        """Create compact header"""
        header = tk.Frame(self.main_frame, bg=self.colors['primary'], height=70)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)
        
        title = tk.Label(header, text='📈 Stock Price Predictor', 
                        font=('Arial', 24, 'bold'),
                        bg=self.colors['primary'], fg='white')
        title.pack(pady=15)
        
    def create_content(self):
        """Create main content area - compact layout"""
        # Content container
        content = tk.Frame(self.main_frame, bg=self.colors['bg'])
        content.pack(fill='both', expand=True, padx=15, pady=5)
        
        # Configure grid
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)
        
        # Left panel - Controls
        left_panel = tk.Frame(content, bg=self.colors['bg'])
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        self.create_instructions_panel(left_panel)
        self.create_input_panel(left_panel)
        self.create_buttons_panel(left_panel)
        
        # Right panel - Results
        right_panel = tk.Frame(content, bg=self.colors['bg'])
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        right_panel.rowconfigure(0, weight=1)
        right_panel.columnconfigure(0, weight=1)
        
        self.create_results_panel(right_panel)
        
    def create_instructions_panel(self, parent):
        """Create compact instructions panel"""
        card = tk.LabelFrame(parent, text=' 📋 How to Use ',
                           font=('Arial', 11, 'bold'),
                           bg=self.colors['card'],
                           fg=self.colors['primary'],
                           padx=10, pady=8)
        card.pack(fill='x', pady=(0, 10))
        
        # Compact steps in 2 columns
        steps_frame = tk.Frame(card, bg=self.colors['card'])
        steps_frame.pack(fill='x')
        
        steps_left = ['1. Enter ticker (e.g., AAPL)', '2. Select period (90/180/360 days)', '3. Choose features']
        steps_right = ['4. Click "Predict Price"', '5. View results →']
        
        left_col = tk.Frame(steps_frame, bg=self.colors['card'])
        left_col.pack(side='left', fill='x', expand=True)
        
        for step in steps_left:
            tk.Label(left_col, text=step, font=('Arial', 9),
                    bg=self.colors['card'], fg=self.colors['text'],
                    anchor='w').pack(fill='x', pady=1)
        
        right_col = tk.Frame(steps_frame, bg=self.colors['card'])
        right_col.pack(side='left', fill='x', expand=True)
        
        for step in steps_right:
            tk.Label(right_col, text=step, font=('Arial', 9),
                    bg=self.colors['card'], fg=self.colors['text'],
                    anchor='w').pack(fill='x', pady=1)
        
        # Compact tips
        tips = tk.Frame(card, bg='#fff3cd', padx=8, pady=5)
        tips.pack(fill='x', pady=(8, 0))
        
        tk.Label(tips, 
                text='💡 Tips: Type for suggestions • Longer periods = more accurate • Enable Technical Indicators',
                font=('Arial', 8), bg='#fff3cd', fg='#856404',
                anchor='w').pack(fill='x')
        
    def create_input_panel(self, parent):
        """Create compact input panel"""
        card = tk.LabelFrame(parent, text=' Stock Information ',
                           font=('Arial', 11, 'bold'),
                           bg=self.colors['card'],
                           fg=self.colors['text'],
                           padx=10, pady=8)
        card.pack(fill='x', pady=(0, 10))
        
        # Ticker input
        tk.Label(card, text='Stock Ticker:', font=('Arial', 10, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(card, textvariable=self.ticker_var,
                                     font=('Arial', 11))
        self.ticker_entry.pack(fill='x', pady=(2, 5))
        self.ticker_entry.bind('<KeyRelease>', self.on_ticker_type)
        
        # Autocomplete dropdown
        self.autocomplete_list = tk.Listbox(card, font=('Arial', 9),
                                           height=4, relief='solid',
                                           borderwidth=1)
        self.autocomplete_list.pack(fill='x', pady=(0, 5))
        self.autocomplete_list.pack_forget()
        self.autocomplete_list.bind('<<ListboxSelect>>', self.on_select_stock)
        
        # Training period
        tk.Label(card, text='Training Period:', font=('Arial', 10, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(5, 2))
        
        self.days_var = tk.StringVar(value='60')
        
        periods_frame = tk.Frame(card, bg=self.colors['card'])
        periods_frame.pack(fill='x')
        
        periods = [
            ('30 days (Quick)', '30'),
            ('60 days', '60'),
            ('90 days (Recommended)', '90'),
            ('180 days (More accurate)', '180'),
            ('360 days (Best accuracy)', '360')
        ]
        
        for text, value in periods:
            rb = tk.Radiobutton(periods_frame, text=text, variable=self.days_var,
                              value=value, font=('Arial', 9),
                              bg=self.colors['card'], fg=self.colors['text'],
                              selectcolor=self.colors['card'])
            rb.pack(anchor='w', pady=0)
        
        # Features
        features_frame = tk.LabelFrame(card, text=' Features ',
                                      font=('Arial', 10, 'bold'),
                                      bg=self.colors['card'],
                                      fg=self.colors['text'],
                                      padx=8, pady=5)
        features_frame.pack(fill='x', pady=(8, 0))
        
        self.use_spread = tk.BooleanVar(value=True)
        self.use_volume = tk.BooleanVar(value=False)
        self.use_tech = tk.BooleanVar(value=True)
        
        tk.Checkbutton(features_frame, text='Price Change',
                      variable=self.use_spread, font=('Arial', 9),
                      bg=self.colors['card']).pack(anchor='w', pady=0)
        
        tk.Checkbutton(features_frame, text='Trading Volume',
                      variable=self.use_volume, font=('Arial', 9),
                      bg=self.colors['card']).pack(anchor='w', pady=0)
        
        tk.Checkbutton(features_frame, text='Technical Indicators (RSI, MACD, SMA, EMA)',
                      variable=self.use_tech, font=('Arial', 9),
                      bg=self.colors['card']).pack(anchor='w', pady=0)
        
        # Popular stocks buttons
        popular_frame = tk.Frame(card, bg=self.colors['card'])
        popular_frame.pack(fill='x', pady=(8, 0))
        
        tk.Label(popular_frame, text='Quick:', font=('Arial', 9, 'bold'),
                bg=self.colors['card']).pack(side='left')
        
        popular = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
        for ticker in popular:
            btn = tk.Button(popular_frame, text=ticker, font=('Arial', 8),
                          bg=self.colors['border'], relief='flat',
                          padx=5, pady=1,
                          command=lambda t=ticker: self.set_ticker(t))
            btn.pack(side='left', padx=1, pady=1)
            
    def create_buttons_panel(self, parent):
        """Create buttons panel - ALWAYS VISIBLE"""
        card = tk.Frame(parent, bg=self.colors['card'], 
                       relief='solid', borderwidth=2, bd=2,
                       padx=15, pady=15)
        card.pack(fill='x', pady=(0, 15))
        
        # Title
        tk.Label(card, text='🎯 Actions', font=('Arial', 14, 'bold'),
                bg=self.colors['card'], fg=self.colors['primary']).pack(pady=(0, 10))
        
        # Predict button
        self.predict_btn = tk.Button(card, text='🔮 PREDICT PRICE',
                                    font=('Arial', 16, 'bold'),
                                    bg=self.colors['primary'],
                                    fg='white',
                                    activebackground=self.colors['primary_dark'],
                                    relief='flat',
                                    padx=20, pady=15,
                                    cursor='hand2',
                                    command=self.start_prediction)
        self.predict_btn.pack(fill='x', pady=(0, 10))
        
        # DJIA button
        self.djia_btn = tk.Button(card, text='📊 Predict DJIA (30 Stocks)',
                                 font=('Arial', 12),
                                 bg=self.colors['card'],
                                 fg=self.colors['text'],
                                 activebackground=self.colors['border'],
                                 relief='solid',
                                 padx=15, pady=10,
                                 cursor='hand2',
                                 command=self.predict_djia)
        self.djia_btn.pack(fill='x')
        
    def create_results_panel(self, parent):
        """Create results panel with resizable chart"""
        card = tk.LabelFrame(parent, text=' Results & Chart ',
                           font=('Arial', 12, 'bold'),
                           bg=self.colors['card'],
                           fg=self.colors['text'],
                           padx=15, pady=15)
        card.pack(fill='both', expand=True)
        card.rowconfigure(2, weight=1)
        card.columnconfigure(0, weight=1)
        
        # Status
        self.status_var = tk.StringVar(value='Ready')
        tk.Label(card, textvariable=self.status_var,
                font=('Arial', 10), bg=self.colors['card'],
                fg=self.colors['text_light']).pack(anchor='w', pady=(0, 10))
        
        # Results text
        self.results_text = scrolledtext.ScrolledText(card, height=8,
                                                     wrap=tk.WORD,
                                                     font=('Consolas', 10),
                                                     bg='#fafafa',
                                                     relief='solid')
        self.results_text.pack(fill='x', pady=(0, 15))
        self.results_text.insert(tk.END, 'Click "PREDICT PRICE" to start...')
        self.results_text.config(state='disabled')
        
        # Chart frame with toolbar
        chart_outer = tk.LabelFrame(card, text=' Price Chart (Zoom & Pan Enabled) ',
                                   font=('Arial', 11, 'bold'),
                                   bg=self.colors['card'],
                                   fg=self.colors['text'],
                                   padx=5, pady=5)
        chart_outer.pack(fill='both', expand=True)
        
        # Create inner frame for grid layout
        chart_container = tk.Frame(chart_outer, bg=self.colors['card'])
        chart_container.pack(fill='both', expand=True)
        chart_container.rowconfigure(0, weight=1)
        chart_container.columnconfigure(0, weight=1)
        
        # Matplotlib figure - RESIZABLE
        self.fig = Figure(figsize=(8, 5), dpi=100)
        self.fig.patch.set_facecolor('white')
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#fafafa')
        
        # Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, chart_container)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Add toolbar in its own frame (using pack internally)
        toolbar_frame = tk.Frame(chart_outer, bg=self.colors['card'])
        toolbar_frame.pack(fill='x', pady=(5, 0))
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.pack(fill='x')
        
        # Placeholder
        self.ax.text(0.5, 0.5, 'Chart will appear here after prediction\n\nUse toolbar above to zoom and pan',
                    ha='center', va='center', transform=self.ax.transAxes,
                    fontsize=11, color='#999999')
        self.canvas.draw()
        
    def on_ticker_type(self, event):
        """Handle ticker autocomplete"""
        query = self.ticker_var.get().upper()
        if len(query) >= 1:
            matches = trading_cal.get_stock_suggestions(query)
            if matches:
                self.autocomplete_list.delete(0, tk.END)
                for ticker, name in matches:
                    self.autocomplete_list.insert(tk.END, f'{ticker} - {name}')
                # Show autocomplete list after the ticker entry
                if not self.autocomplete_list.winfo_viewable():
                    self.autocomplete_list.pack(fill='x', pady=(0, 10))
            else:
                self.autocomplete_list.pack_forget()
        else:
            self.autocomplete_list.pack_forget()
            
    def on_select_stock(self, event):
        """Handle stock selection"""
        selection = self.autocomplete_list.curselection()
        if selection:
            selected = self.autocomplete_list.get(selection[0])
            ticker = selected.split(' - ')[0]
            self.ticker_var.set(ticker)
            self.autocomplete_list.pack_forget()
            
    def set_ticker(self, ticker):
        """Set ticker from button"""
        self.ticker_var.set(ticker)
        
    def start_prediction(self):
        """Start prediction"""
        if self.prediction_in_progress:
            return
            
        ticker = self.ticker_var.get().strip().upper()
        if not ticker:
            messagebox.showwarning('Input Required', 'Please enter a stock ticker')
            return
        
        try:
            days = int(self.days_var.get())
        except ValueError:
            messagebox.showwarning('Invalid Input', 'Please select a training period')
            return
        
        # Disable buttons
        self.prediction_in_progress = True
        self.predict_btn.config(state='disabled', text='⏳ PREDICTING...')
        self.djia_btn.config(state='disabled')
        
        self.status_var.set(f'Fetching {ticker} data...')
        
        thread = threading.Thread(target=self.run_prediction, args=(ticker, days))
        thread.daemon = True
        thread.start()
        
    def run_prediction(self, ticker, days):
        """Run prediction"""
        try:
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            pred.process_company(ticker, days, 
                               self.use_spread.get(), 
                               self.use_volume.get(),
                               self.use_tech.get())
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            self.root.after(0, self.show_results, ticker, output)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
            
    def show_results(self, ticker, output):
        """Show results"""
        self.prediction_in_progress = False
        self.predict_btn.config(state='normal', text='🔮 PREDICT PRICE')
        self.djia_btn.config(state='normal')
        
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        self.results_text.config(state='disabled')
        
        self.status_var.set(f'Complete: {ticker}')
        
        self.update_chart(ticker)
        
    def show_error(self, error_msg):
        """Show error"""
        self.prediction_in_progress = False
        self.predict_btn.config(state='normal', text='🔮 PREDICT PRICE')
        self.djia_btn.config(state='normal')
        
        messagebox.showerror('Error', error_msg)
        self.status_var.set('Error occurred')
        
    def update_chart(self, ticker):
        """Update chart"""
        try:
            import yfinance as yf
            from datetime import datetime, timedelta
            
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            hist = stock.history(start=start_date, end=end_date)
            
            if not hist.empty:
                self.ax.clear()
                
                # Price line
                self.ax.plot(hist.index, hist['Close'], 
                           linewidth=2, color=self.colors['primary'],
                           label='Closing Price')
                self.ax.fill_between(hist.index, hist['Close'], 
                                   alpha=0.3, color=self.colors['primary'])
                
                # Moving average
                if len(hist) >= 20:
                    ma20 = hist['Close'].rolling(window=20).mean()
                    self.ax.plot(hist.index, ma20, 
                               linewidth=1.5, color=self.colors['success'],
                               label='20-Day MA', linestyle='--')
                
                self.ax.set_title(f'{ticker} - 90 Day Price History', 
                                fontsize=12, fontweight='bold')
                self.ax.set_xlabel('Date')
                self.ax.set_ylabel('Price ($)')
                self.ax.legend()
                self.ax.grid(True, alpha=0.3)
                
                plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
                self.fig.tight_layout()
                self.canvas.draw()
                
        except Exception as e:
            print(f'Chart error: {e}')
            
    def predict_djia(self):
        """Predict DJIA"""
        if self.prediction_in_progress:
            return
        
        try:
            days = int(self.days_var.get())
        except ValueError:
            messagebox.showwarning('Invalid Input', 'Select training period')
            return
        
        self.prediction_in_progress = True
        self.predict_btn.config(state='disabled')
        self.djia_btn.config(state='disabled', text='⏳ Predicting DJIA...')
        
        self.status_var.set('Predicting DJIA...')
        
        thread = threading.Thread(target=self.run_djia_prediction, args=(days,))
        thread.daemon = True
        thread.start()
        
    def run_djia_prediction(self, days):
        """Run DJIA predictions"""
        try:
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            tickers = cn.get_djia_list()
            for i, ticker in enumerate(tickers[:5]):
                self.root.after(0, lambda t=ticker, idx=i: 
                    self.status_var.set(f'Predicting {t} ({idx+1}/5)...'))
                pred.process_company(ticker, days, 
                                   self.use_spread.get(), 
                                   self.use_volume.get(),
                                   self.use_tech.get())
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            self.root.after(0, self.show_results, 'DJIA (5)', output)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))


def main():
    root = tk.Tk()
    app = ScrollableStockGUI(root)
    
    root.update_idletasks()
    
    # Get the required size based on all widgets
    root.geometry('')
    root.update_idletasks()
    
    # Get the requested width/height from all widgets
    req_width = root.winfo_reqwidth()
    req_height = root.winfo_reqheight()
    
    # Add more height to fit everything without scrolling
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    width = min(req_width + 50, screen_width - 50)
    height = min(req_height + 200, screen_height - 100)
    
    # Center the window
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == '__main__':
    main()
