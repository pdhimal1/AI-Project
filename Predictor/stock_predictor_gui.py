"""
Stock Predictor - Simple GUI with Instructions
A clean, easy-to-use interface with clear guidance.

Features:
- Clear instructions on startup
- Simple input with autocomplete
- 90/180/360 day training options (90 default)
- Enhanced predictions with technical indicators
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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


class SimpleStockGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Price Predictor")
        self.root.geometry("1100x800")
        self.root.configure(bg='#f5f5f5')
        
        # Colors
        self.colors = {
            'bg': '#f5f5f5',
            'card': '#ffffff',
            'primary': '#2196F3',
            'primary_dark': '#1976D2',
            'text': '#333333',
            'text_light': '#666666',
            'success': '#4CAF50',
            'border': '#e0e0e0'
        }
        
        self.root.minsize(1000, 700)
        
        # Main container
        self.create_layout()
        self.create_instructions()
        self.create_input_section()
        self.create_results_section()
        
        self.prediction_in_progress = False
        
    def create_layout(self):
        """Create main layout"""
        # Header
        header = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        title = tk.Label(header, text='📈 Stock Price Predictor', 
                        font=('Arial', 24, 'bold'),
                        bg=self.colors['primary'], fg='white')
        title.pack(pady=20)
        
        # Main content
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Two columns
        self.left_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        self.left_frame.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        self.right_frame = tk.Frame(self.main_frame, bg=self.colors['bg'])
        self.right_frame.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
    def create_instructions(self):
        """Create instructions panel"""
        card = tk.Frame(self.left_frame, bg=self.colors['card'], 
                       relief='solid', borderwidth=1, bd=1)
        card.pack(fill='x', pady=(0, 15))
        
        # Instructions header
        header = tk.Frame(card, bg=self.colors['primary_dark'])
        header.pack(fill='x')
        
        tk.Label(header, text='📋 How to Use This App', 
                font=('Arial', 14, 'bold'),
                bg=self.colors['primary_dark'], fg='white').pack(pady=10)
        
        # Instructions content
        content = tk.Frame(card, bg=self.colors['card'], padx=15, pady=15)
        content.pack(fill='x')
        
        instructions = [
            "1. Enter a stock ticker (e.g., AAPL, MSFT, TSLA)",
            "2. Select training period (90, 180, or 360 days)",
            "3. Choose which features to include",
            "4. Click 'Predict Price' button",
            "5. View results and chart on the right"
        ]
        
        for i, text in enumerate(instructions):
            tk.Label(content, text=text, font=('Arial', 11),
                    bg=self.colors['card'], fg=self.colors['text'],
                    anchor='w').pack(fill='x', pady=3)
        
        # Tips section
        tips_frame = tk.Frame(card, bg='#fff3cd', padx=15, pady=10)
        tips_frame.pack(fill='x')
        
        tk.Label(tips_frame, text='💡 Tips:', 
                font=('Arial', 11, 'bold'),
                bg='#fff3cd', fg='#856404').pack(anchor='w')
        
        tk.Label(tips_frame, 
                text='• Start typing to see stock suggestions\n• Longer training periods (180-360 days) = more accurate predictions\n• Technical indicators improve prediction quality',
                font=('Arial', 10),
                bg='#fff3cd', fg='#856404',
                justify='left').pack(anchor='w', pady=(5, 0))
        
    def create_input_section(self):
        """Create input section"""
        # Input card
        card = tk.LabelFrame(self.left_frame, text=' Stock Information ',
                           font=('Arial', 12, 'bold'),
                           bg=self.colors['card'],
                           fg=self.colors['text'],
                           padx=15, pady=15)
        card.pack(fill='x', pady=(0, 15))
        
        # Stock ticker
        tk.Label(card, text='Stock Ticker Symbol:', 
                font=('Arial', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w')
        
        tk.Label(card, text='Type to search (e.g., AAPL, MSFT, TSLA)',
                font=('Arial', 9),
                bg=self.colors['card'], fg=self.colors['text_light']).pack(anchor='w', pady=(2, 8))
        
        self.ticker_var = tk.StringVar()
        self.ticker_entry = ttk.Entry(card, textvariable=self.ticker_var,
                                     font=('Arial', 13), width=25)
        self.ticker_entry.pack(fill='x', pady=(0, 15))
        self.ticker_entry.bind('<KeyRelease>', self.on_ticker_type)
        
        # Autocomplete listbox
        self.autocomplete_frame = tk.Frame(card, bg=self.colors['card'])
        self.autocomplete_list = tk.Listbox(self.autocomplete_frame, 
                                           font=('Arial', 10),
                                           height=5, width=40)
        self.autocomplete_list.pack(side='left', fill='both', expand=True)
        self.autocomplete_list.bind('<<ListboxSelect>>', self.on_select_stock)
        
        scrollbar = ttk.Scrollbar(self.autocomplete_frame, orient='vertical',
                                 command=self.autocomplete_list.yview)
        scrollbar.pack(side='right', fill='y')
        self.autocomplete_list.config(yscrollcommand=scrollbar.set)
        
        # Training days
        tk.Label(card, text='Training Period:', 
                font=('Arial', 11, 'bold'),
                bg=self.colors['card'], fg=self.colors['text']).pack(anchor='w', pady=(10, 5))
        
        tk.Label(card, text='More days = better accuracy but slower',
                font=('Arial', 9),
                bg=self.colors['card'], fg=self.colors['text_light']).pack(anchor='w', pady=(0, 8))
        
        self.days_var = tk.StringVar(value='90')
        days_frame = tk.Frame(card, bg=self.colors['card'])
        days_frame.pack(fill='x')
        
        days_options = [
            ('90 days (Recommended)', '90'),
            ('180 days (More accurate)', '180'),
            ('360 days (Best accuracy)', '360')
        ]
        
        for text, value in days_options:
            rb = tk.Radiobutton(days_frame, text=text, variable=self.days_var,
                              value=value, font=('Arial', 10),
                              bg=self.colors['card'], fg=self.colors['text'],
                              selectcolor=self.colors['card'])
            rb.pack(anchor='w', pady=2)
        
        # Features
        features_frame = tk.LabelFrame(card, text=' Features ',
                                      font=('Arial', 11, 'bold'),
                                      bg=self.colors['card'],
                                      fg=self.colors['text'],
                                      padx=10, pady=10)
        features_frame.pack(fill='x', pady=(15, 0))
        
        self.use_spread = tk.BooleanVar(value=True)
        self.use_volume = tk.BooleanVar(value=False)
        self.use_tech = tk.BooleanVar(value=True)
        
        tk.Checkbutton(features_frame, text='Price Change (Recommended)',
                      variable=self.use_spread, font=('Arial', 10),
                      bg=self.colors['card'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack(anchor='w', pady=2)
        
        tk.Checkbutton(features_frame, text='Trading Volume',
                      variable=self.use_volume, font=('Arial', 10),
                      bg=self.colors['card'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack(anchor='w', pady=2)
        
        tk.Checkbutton(features_frame, text='Technical Indicators (RSI, MACD, SMA, EMA)',
                      variable=self.use_tech, font=('Arial', 10),
                      bg=self.colors['card'], fg=self.colors['text'],
                      selectcolor=self.colors['card']).pack(anchor='w', pady=2)
        
        # Buttons
        btn_frame = tk.Frame(self.left_frame, bg=self.colors['bg'])
        btn_frame.pack(fill='x', pady=(0, 15))
        
        self.predict_btn = tk.Button(btn_frame, text='🔮 Predict Price',
                                    font=('Arial', 14, 'bold'),
                                    bg=self.colors['primary'],
                                    fg='white',
                                    activebackground=self.colors['primary_dark'],
                                    activeforeground='white',
                                    relief='flat',
                                    padx=30, pady=12,
                                    cursor='hand2',
                                    command=self.start_prediction)
        self.predict_btn.pack(fill='x', pady=(0, 10))
        
        self.djia_btn = tk.Button(btn_frame, text='📊 Predict DJIA (30 Stocks)',
                                 font=('Arial', 12),
                                 bg=self.colors['card'],
                                 fg=self.colors['text'],
                                 activebackground=self.colors['border'],
                                 relief='solid',
                                 padx=20, pady=10,
                                 cursor='hand2',
                                 command=self.predict_djia)
        self.djia_btn.pack(fill='x')
        
        # Popular stocks
        popular_frame = tk.LabelFrame(self.left_frame, text=' Popular Stocks ',
                                     font=('Arial', 11, 'bold'),
                                     bg=self.colors['card'],
                                     fg=self.colors['text'],
                                     padx=10, pady=10)
        popular_frame.pack(fill='x')
        
        popular_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']
        btn_frame = tk.Frame(popular_frame, bg=self.colors['card'])
        btn_frame.pack()
        
        for i, ticker in enumerate(popular_stocks):
            btn = tk.Button(btn_frame, text=ticker, font=('Arial', 9),
                          bg=self.colors['border'], fg=self.colors['text'],
                          relief='flat', padx=8, pady=4,
                          command=lambda t=ticker: self.set_ticker(t))
            btn.pack(side='left', padx=2, pady=2)
            
    def create_results_section(self):
        """Create results section"""
        # Results card
        card = tk.LabelFrame(self.right_frame, text=' Results ',
                           font=('Arial', 12, 'bold'),
                           bg=self.colors['card'],
                           fg=self.colors['text'],
                           padx=15, pady=15)
        card.pack(fill='both', expand=True)
        
        # Status label
        self.status_var = tk.StringVar(value='Ready to predict')
        tk.Label(card, textvariable=self.status_var,
                font=('Arial', 10),
                bg=self.colors['card'], fg=self.colors['text_light']).pack(anchor='w', pady=(0, 10))
        
        # Results text
        self.results_text = scrolledtext.ScrolledText(card, height=10,
                                                     wrap=tk.WORD,
                                                     font=('Consolas', 10),
                                                     bg='#fafafa',
                                                     fg=self.colors['text'],
                                                     relief='solid',
                                                     borderwidth=1)
        self.results_text.pack(fill='x', pady=(0, 15))
        self.results_text.insert(tk.END, 'Enter a stock ticker and click "Predict Price" to see results...')
        self.results_text.config(state='disabled')
        
        # Chart
        chart_frame = tk.LabelFrame(card, text=' Price Chart ',
                                   font=('Arial', 11, 'bold'),
                                   bg=self.colors['card'],
                                   fg=self.colors['text'],
                                   padx=10, pady=10)
        chart_frame.pack(fill='both', expand=True)
        
        # Matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(8, 5), dpi=100)
        self.fig.patch.set_facecolor('white')
        self.ax.set_facecolor('#fafafa')
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Placeholder text
        self.ax.text(0.5, 0.5, 'Chart will appear here',
                    ha='center', va='center',
                    transform=self.ax.transAxes,
                    fontsize=12, color='#999999')
        self.canvas.draw()
        
    def on_ticker_type(self, event):
        """Handle ticker typing for autocomplete"""
        query = self.ticker_var.get().upper()
        if len(query) >= 1:
            matches = trading_cal.get_stock_suggestions(query)
            if matches:
                self.autocomplete_list.delete(0, tk.END)
                for ticker, name in matches:
                    self.autocomplete_list.insert(tk.END, f'{ticker} - {name}')
                self.autocomplete_frame.pack(fill='x', pady=(0, 10))
            else:
                self.autocomplete_frame.pack_forget()
        else:
            self.autocomplete_frame.pack_forget()
            
    def on_select_stock(self, event):
        """Handle stock selection from autocomplete"""
        selection = self.autocomplete_list.curselection()
        if selection:
            selected = self.autocomplete_list.get(selection[0])
            ticker = selected.split(' - ')[0]
            self.ticker_var.set(ticker)
            self.autocomplete_frame.pack_forget()
            
    def set_ticker(self, ticker):
        """Set ticker from popular button"""
        self.ticker_var.set(ticker)
        
    def start_prediction(self):
        """Start prediction"""
        if self.prediction_in_progress:
            return
            
        ticker = self.ticker_var.get().strip().upper()
        if not ticker:
            messagebox.showwarning('Input Required', 'Please enter a stock ticker symbol')
            return
        
        try:
            days = int(self.days_var.get())
        except ValueError:
            messagebox.showwarning('Invalid Input', 'Please select a training period')
            return
        
        # Disable UI
        self.prediction_in_progress = True
        self.predict_btn.config(state='disabled', text='⏳ Predicting...')
        self.djia_btn.config(state='disabled')
        
        self.status_var.set(f'Fetching data for {ticker}...')
        
        # Run in thread
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
        """Display results"""
        self.prediction_in_progress = False
        self.predict_btn.config(state='normal', text='🔮 Predict Price')
        self.djia_btn.config(state='normal')
        
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        self.results_text.config(state='disabled')
        
        self.status_var.set(f'Prediction complete for {ticker}')
        
        self.update_chart(ticker)
        
    def show_error(self, error_msg):
        """Show error"""
        self.prediction_in_progress = False
        self.predict_btn.config(state='normal', text='🔮 Predict Price')
        self.djia_btn.config(state='normal')
        
        messagebox.showerror('Error', f'An error occurred: {error_msg}')
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
                
                self.ax.plot(hist.index, hist['Close'], 
                           linewidth=2, color=self.colors['primary'],
                           label='Price')
                self.ax.fill_between(hist.index, hist['Close'], 
                                   alpha=0.3, color=self.colors['primary'])
                
                if len(hist) >= 20:
                    ma20 = hist['Close'].rolling(window=20).mean()
                    self.ax.plot(hist.index, ma20, 
                               linewidth=1.5, color=self.colors['success'],
                               label='20-Day MA', linestyle='--')
                
                self.ax.set_title(f'{ticker} - 90 Day History', fontsize=12, fontweight='bold')
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
            messagebox.showwarning('Invalid Input', 'Please select a training period')
            return
        
        self.prediction_in_progress = True
        self.predict_btn.config(state='disabled')
        self.djia_btn.config(state='disabled', text='⏳ Predicting DJIA...')
        
        self.status_var.set('Predicting DJIA stocks...')
        
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
            
            self.root.after(0, self.show_results, 'DJIA (5 stocks)', output)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))


def main():
    root = tk.Tk()
    app = SimpleStockGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == '__main__':
    main()
