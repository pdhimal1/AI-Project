"""
Stock Predictor - Modern Sleek User Interface
A beautiful, user-friendly GUI with autocomplete and modern design.

Features:
- Sleek modern design with custom styling
- Autocomplete dropdown for stock tickers
- Real-time search as you type
- Smooth animations and transitions
- Professional color scheme
- Interactive charts
- No Python or finance knowledge required!
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import threading
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import predictor as pred
import get_historical as gh
import normalize as scale
import company_name as cn
import trading_day as trading_cal

# Set matplotlib style
plt.style.use('seaborn-v0_8-darkgrid')


class AutocompleteEntry(ttk.Entry):
    """Custom Entry widget with autocomplete functionality"""
    
    def __init__(self, master=None, completevalues=None, **kwargs):
        super().__init__(master, **kwargs)
        self.completevalues = completevalues or []
        self.var = kwargs.get('textvariable', tk.StringVar())
        self.var.trace('w', self._on_text_change)
        
        # Create listbox for suggestions
        self.listbox = tk.Listbox(master, height=6, font=('Segoe UI', 10))
        self.listbox.bind('<<ListboxSelect>>', self._on_select)
        self.listbox.bind('<FocusOut>', self._hide_listbox)
        
        # Bind events
        self.bind('<KeyRelease>', self._on_keyrelease)
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<Down>', self._on_down)
        
        self._listbox_visible = False
        
    def _on_text_change(self, *args):
        """Called when text changes"""
        current_text = self.var.get().upper()
        if len(current_text) >= 1:
            matches = trading_cal.get_stock_suggestions(current_text)
            if matches:
                self._show_suggestions(matches)
            else:
                self._hide_listbox()
        else:
            self._hide_listbox()
    
    def _show_suggestions(self, matches):
        """Show suggestion listbox"""
        self.listbox.delete(0, tk.END)
        for ticker, name in matches:
            display_text = f"{ticker} - {name}"
            self.listbox.insert(tk.END, display_text)
        
        # Position listbox below entry
        x = self.winfo_x()
        y = self.winfo_y() + self.winfo_height() + 2
        self.listbox.place(in_=self.master, x=x, y=y, width=self.winfo_width())
        self._listbox_visible = True
    
    def _hide_listbox(self, event=None):
        """Hide suggestion listbox"""
        self.listbox.place_forget()
        self._listbox_visible = False
    
    def _on_select(self, event):
        """Handle selection from listbox"""
        selection = self.listbox.curselection()
        if selection:
            selected_text = self.listbox.get(selection[0])
            ticker = selected_text.split(' - ')[0]
            self.var.set(ticker)
            self._hide_listbox()
    
    def _on_keyrelease(self, event):
        """Handle key release"""
        if event.keysym in ('Down', 'Up', 'Return', 'Escape'):
            return
    
    def _on_down(self, event):
        """Handle down arrow key"""
        if self._listbox_visible:
            self.listbox.focus()
            self.listbox.selection_set(0)
    
    def _on_focus_in(self, event):
        """Handle focus in"""
        pass


class StockPredictorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Price Predictor")
        self.root.geometry("1400x900")
        
        # Color scheme - Modern Dark Theme
        self.colors = {
            'bg': '#0f172a',           # Dark navy background
            'card_bg': '#1e293b',       # Card background
            'accent': '#3b82f6',        # Blue accent
            'accent_hover': '#2563eb',  # Blue hover
            'text': '#f1f5f9',          # Light text
            'text_secondary': '#94a3b8', # Secondary text
            'success': '#10b981',       # Green for success
            'warning': '#f59e0b',       # Orange for warnings
            'error': '#ef4444',         # Red for errors
            'border': '#334155',        # Border color
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.root.minsize(1200, 800)
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.create_main_container()
        self.create_header()
        self.create_content()
        self.create_footer()
        
        # Data storage
        self.current_prediction = None
        self.prediction_in_progress = False
        
    def setup_styles(self):
        """Configure custom styles"""
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame styles
        style.configure('Card.TFrame', background=self.colors['card_bg'])
        
        # Label styles
        style.configure('Title.TLabel', 
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 32, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 12))
        
        style.configure('CardTitle.TLabel',
                       background=self.colors['card_bg'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 14, 'bold'))
        
        style.configure('CardText.TLabel',
                       background=self.colors['card_bg'],
                       foreground=self.colors['text_secondary'],
                       font=('Segoe UI', 11))
        
        # Button style
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 12, 'bold'),
                       padding=(20, 10))
        
        style.map('Accent.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent'])])
        
    def create_main_container(self):
        """Create main container"""
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # Configure grid
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)
        
    def create_header(self):
        """Create sleek header"""
        header = tk.Frame(self.main_container, bg=self.colors['bg'])
        header.grid(row=0, column=0, sticky='ew', pady=(0, 30))
        
        # Logo/Title
        title_container = tk.Frame(header, bg=self.colors['bg'])
        title_container.pack()
        
        # App icon (using emoji)
        icon_label = tk.Label(title_container, 
                             text='📈',
                             font=('Segoe UI', 48),
                             bg=self.colors['bg'])
        icon_label.pack()
        
        title = tk.Label(title_container,
                        text='Stock Price Predictor',
                        font=('Segoe UI', 32, 'bold'),
                        bg=self.colors['bg'],
                        fg=self.colors['text'])
        title.pack()
        
        subtitle = tk.Label(title_container,
                           text='Machine Learning Powered Stock Predictions',
                           font=('Segoe UI', 12),
                           bg=self.colors['bg'],
                           fg=self.colors['text_secondary'])
        subtitle.pack(pady=(5, 0))
        
    def create_content(self):
        """Create main content area with cards"""
        content = tk.Frame(self.main_container, bg=self.colors['bg'])
        content.grid(row=1, column=0, sticky='nsew')
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)
        
        # Left panel - Input
        self.create_input_panel(content)
        
        # Right panel - Results
        self.create_results_panel(content)
        
    def create_input_panel(self, parent):
        """Create input panel with card design"""
        # Card container
        card = tk.Frame(parent, bg=self.colors['card_bg'], padx=30, pady=30)
        card.grid(row=0, column=0, sticky='nsew', padx=(0, 20))
        
        # Card title
        title = tk.Label(card,
                        text='Stock Information',
                        font=('Segoe UI', 18, 'bold'),
                        bg=self.colors['card_bg'],
                        fg=self.colors['text'])
        title.pack(anchor='w', pady=(0, 25))
        
        # Stock Ticker Input with Autocomplete
        ticker_frame = tk.Frame(card, bg=self.colors['card_bg'])
        ticker_frame.pack(fill='x', pady=(0, 20))
        
        ticker_label = tk.Label(ticker_frame,
                               text='Stock Ticker Symbol',
                               font=('Segoe UI', 11, 'bold'),
                               bg=self.colors['card_bg'],
                               fg=self.colors['text'])
        ticker_label.pack(anchor='w')
        
        ticker_hint = tk.Label(ticker_frame,
                              text='Start typing to search (e.g., AAPL, MSFT)',
                              font=('Segoe UI', 9),
                              bg=self.colors['card_bg'],
                              fg=self.colors['text_secondary'])
        ticker_hint.pack(anchor='w', pady=(2, 8))
        
        # Custom styled entry for autocomplete
        self.ticker_var = tk.StringVar()
        self.ticker_entry = AutocompleteEntry(ticker_frame, 
                                              textvariable=self.ticker_var,
                                              font=('Segoe UI', 14),
                                              width=25)
        self.ticker_entry.pack(fill='x', ipady=8)
        self.ticker_entry.configure(background='white')
        
        # Training Days
        days_frame = tk.Frame(card, bg=self.colors['card_bg'])
        days_frame.pack(fill='x', pady=(0, 20))
        
        days_label = tk.Label(days_frame,
                             text='Training Period',
                             font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['card_bg'],
                             fg=self.colors['text'])
        days_label.pack(anchor='w')
        
        days_hint = tk.Label(days_frame,
                            text='More days = better accuracy',
                            font=('Segoe UI', 9),
                            bg=self.colors['card_bg'],
                            fg=self.colors['text_secondary'])
        days_hint.pack(anchor='w', pady=(2, 8))
        
        self.days_var = tk.StringVar(value='30')
        days_options = ['10', '20', '30', '60', '90']
        
        self.days_combo = ttk.Combobox(days_frame,
                                      textvariable=self.days_var,
                                      values=days_options,
                                      font=('Segoe UI', 12),
                                      width=23,
                                      state='readonly')
        self.days_combo.pack(fill='x', ipady=5)
        
        # Features
        features_frame = tk.LabelFrame(card,
                                      text=' Features ',
                                      font=('Segoe UI', 11, 'bold'),
                                      bg=self.colors['card_bg'],
                                      fg=self.colors['text'],
                                      padx=15,
                                      pady=15)
        features_frame.pack(fill='x', pady=(0, 25))
        
        self.use_spread = tk.BooleanVar(value=True)
        self.use_volume = tk.BooleanVar(value=False)
        
        spread_cb = tk.Checkbutton(features_frame,
                                  text='Include Price Change',
                                  variable=self.use_spread,
                                  font=('Segoe UI', 10),
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'],
                                  selectcolor=self.colors['accent'])
        spread_cb.pack(anchor='w', pady=3)
        
        volume_cb = tk.Checkbutton(features_frame,
                                  text='Include Trading Volume',
                                  variable=self.use_volume,
                                  font=('Segoe UI', 10),
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['text'],
                                  selectcolor=self.colors['accent'])
        volume_cb.pack(anchor='w', pady=3)
        
        # Predict Button
        self.predict_btn = tk.Button(card,
                                    text='🔮 Predict Price',
                                    font=('Segoe UI', 14, 'bold'),
                                    bg=self.colors['accent'],
                                    fg=self.colors['text'],
                                    activebackground=self.colors['accent_hover'],
                                    activeforeground=self.colors['text'],
                                    cursor='hand2',
                                    relief='flat',
                                    padx=30,
                                    pady=12,
                                    command=self.start_prediction)
        self.predict_btn.pack(fill='x', pady=(0, 15))
        
        # DJIA Button
        self.djia_btn = tk.Button(card,
                                 text='📊 Predict All DJIA',
                                 font=('Segoe UI', 12),
                                 bg=self.colors['card_bg'],
                                 fg=self.colors['text'],
                                 activebackground=self.colors['border'],
                                 activeforeground=self.colors['text'],
                                 cursor='hand2',
                                 relief='solid',
                                 padx=20,
                                 pady=10,
                                 command=self.predict_djia)
        self.djia_btn.pack(fill='x')
        
        # Quick Help Card
        help_card = tk.Frame(card, bg=self.colors['border'], padx=15, pady=15)
        help_card.pack(fill='x', pady=(25, 0))
        
        help_title = tk.Label(help_card,
                             text='💡 Quick Help',
                             font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['border'],
                             fg=self.colors['text'])
        help_title.pack(anchor='w')
        
        help_text = """Popular Tickers:
• AAPL - Apple
• MSFT - Microsoft  
• GOOGL - Google
• TSLA - Tesla
• AMZN - Amazon"""
        
        help_content = tk.Label(help_card,
                               text=help_text,
                               font=('Segoe UI', 10),
                               bg=self.colors['border'],
                               fg=self.colors['text_secondary'],
                               justify='left')
        help_content.pack(anchor='w', pady=(8, 0))
        
    def create_results_panel(self, parent):
        """Create results panel with chart"""
        # Card container
        card = tk.Frame(parent, bg=self.colors['card_bg'], padx=30, pady=30)
        card.grid(row=0, column=1, sticky='nsew')
        card.columnconfigure(0, weight=1)
        card.rowconfigure(2, weight=1)
        
        # Card title
        title = tk.Label(card,
                        text='Prediction Results',
                        font=('Segoe UI', 18, 'bold'),
                        bg=self.colors['card_bg'],
                        fg=self.colors['text'])
        title.grid(row=0, column=0, sticky='w', pady=(0, 20))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(card,
                                                     height=6,
                                                     wrap=tk.WORD,
                                                     font=('Consolas', 11),
                                                     bg=self.colors['bg'],
                                                     fg=self.colors['text'],
                                                     insertbackground=self.colors['text'],
                                                     relief='flat',
                                                     padx=15,
                                                     pady=15)
        self.results_text.grid(row=1, column=0, sticky='ew', pady=(0, 20))
        self.results_text.insert(tk.END, 'Enter a stock ticker and click "Predict Price" to see results...')
        self.results_text.config(state=tk.DISABLED)
        
        # Chart frame
        chart_frame = tk.Frame(card, bg=self.colors['bg'])
        chart_frame.grid(row=2, column=0, sticky='nsew')
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure with dark theme
        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor=self.colors['card_bg'])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.colors['card_bg'])
        
        # Style the chart
        self.ax.tick_params(colors=self.colors['text_secondary'])
        self.ax.xaxis.label.set_color(self.colors['text_secondary'])
        self.ax.yaxis.label.set_color(self.colors['text_secondary'])
        self.ax.title.set_color(self.colors['text'])
        self.ax.spines['bottom'].set_color(self.colors['border'])
        self.ax.spines['top'].set_color(self.colors['border'])
        self.ax.spines['left'].set_color(self.colors['border'])
        self.ax.spines['right'].set_color(self.colors['border'])
        
        # Embed chart
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        
        # Initial placeholder
        self.ax.text(0.5, 0.5, 'Chart will appear here after prediction',
                    ha='center', va='center',
                    transform=self.ax.transAxes,
                    fontsize=14, color=self.colors['text_secondary'])
        self.canvas.draw()
        
    def create_footer(self):
        """Create footer with status bar"""
        footer = tk.Frame(self.main_container, bg=self.colors['bg'])
        footer.grid(row=2, column=0, sticky='ew', pady=(20, 0))
        
        # Status label
        self.status_var = tk.StringVar(value='Ready')
        self.status_label = tk.Label(footer,
                                    textvariable=self.status_var,
                                    font=('Segoe UI', 10),
                                    bg=self.colors['bg'],
                                    fg=self.colors['text_secondary'])
        self.status_label.pack(side='left')
        
        # Progress bar
        self.progress = ttk.Progressbar(footer,
                                       mode='indeterminate',
                                       length=200)
        self.progress.pack(side='right')
        self.progress.pack_forget()
        
    def start_prediction(self):
        """Start prediction process"""
        if self.prediction_in_progress:
            return
            
        ticker = self.ticker_var.get().strip().upper()
        
        if not ticker:
            messagebox.showwarning('Input Required',
                                 'Please enter a stock ticker symbol')
            return
        
        try:
            days = int(self.days_var.get())
            if days < 1:
                raise ValueError()
        except ValueError:
            messagebox.showwarning('Invalid Input',
                                 'Please select a valid number of training days')
            return
        
        # Disable UI
        self.prediction_in_progress = True
        self.predict_btn.config(state='disabled', text='⏳ Predicting...')
        self.djia_btn.config(state='disabled')
        self.ticker_entry.config(state='disabled')
        self.days_combo.config(state='disabled')
        
        self.status_var.set(f'Fetching data for {ticker}...')
        self.progress.pack(side='right')
        self.progress.start()
        
        # Run in thread
        thread = threading.Thread(target=self.run_prediction, args=(ticker, days))
        thread.daemon = True
        thread.start()
        
    def run_prediction(self, ticker, days):
        """Run the prediction"""
        try:
            import io
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            
            pred.process_company(ticker, days, 
                               self.use_spread.get(), 
                               self.use_volume.get())
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            self.root.after(0, self.show_results, ticker, output)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
            
    def show_results(self, ticker, output):
        """Display results"""
        self.progress.stop()
        self.progress.pack_forget()
        
        # Re-enable UI
        self.prediction_in_progress = False
        self.predict_btn.config(state='normal', text='🔮 Predict Price')
        self.djia_btn.config(state='normal')
        self.ticker_entry.config(state='normal')
        self.days_combo.config(state='readonly')
        
        # Update results
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, output)
        self.results_text.config(state='disabled')
        
        self.status_var.set(f'Prediction complete for {ticker}')
        
        # Update chart
        self.update_chart(ticker)
        
    def show_error(self, error_msg):
        """Show error message"""
        self.progress.stop()
        self.progress.pack_forget()
        
        # Re-enable UI
        self.prediction_in_progress = False
        self.predict_btn.config(state='normal', text='🔮 Predict Price')
        self.djia_btn.config(state='normal')
        self.ticker_entry.config(state='normal')
        self.days_combo.config(state='readonly')
        
        # User-friendly errors
        friendly_errors = {
            'Not connected': 'Unable to connect to the internet.',
            'ticker': 'Could not find stock ticker. Please check the symbol.',
            'historical': 'Could not fetch data. The market may be closed.',
        }
        
        friendly_msg = error_msg
        for key, msg in friendly_errors.items():
            if key.lower() in error_msg.lower():
                friendly_msg = msg
                break
        
        messagebox.showerror('Prediction Error', friendly_msg)
        self.status_var.set('Error occurred')
        
    def update_chart(self, ticker):
        """Update price chart"""
        try:
            import yfinance as yf
            from datetime import datetime, timedelta
            
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            hist = stock.history(start=start_date, end=end_date)
            
            if not hist.empty:
                self.ax.clear()
                
                # Style the chart again after clear
                self.ax.set_facecolor(self.colors['card_bg'])
                self.ax.tick_params(colors=self.colors['text_secondary'])
                self.ax.xaxis.label.set_color(self.colors['text_secondary'])
                self.ax.yaxis.label.set_color(self.colors['text_secondary'])
                self.ax.title.set_color(self.colors['text'])
                for spine in self.ax.spines.values():
                    spine.set_color(self.colors['border'])
                
                # Plot
                self.ax.plot(hist.index, hist['Close'], 
                           linewidth=2.5, color=self.colors['accent'],
                           label='Closing Price')
                self.ax.fill_between(hist.index, hist['Close'], 
                                   alpha=0.2, color=self.colors['accent'])
                
                # Moving average
                if len(hist) >= 20:
                    ma20 = hist['Close'].rolling(window=20).mean()
                    self.ax.plot(hist.index, ma20, 
                               linewidth=2, color=self.colors['success'],
                               label='20-Day MA', linestyle='--')
                
                self.ax.set_title(f'{ticker} - 90 Day Price History',
                                fontsize=16, fontweight='bold', pad=20)
                self.ax.set_xlabel('Date', fontsize=12, fontweight='bold')
                self.ax.set_ylabel('Price ($)', fontsize=12, fontweight='bold')
                self.ax.legend(loc='best', fontsize=11)
                self.ax.grid(True, alpha=0.3, color=self.colors['border'])
                
                plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
                self.fig.tight_layout()
                self.canvas.draw()
                
        except Exception as e:
            print(f'Could not update chart: {e}')
            
    def predict_djia(self):
        """Predict DJIA stocks"""
        if self.prediction_in_progress:
            return
            
        try:
            days = int(self.days_var.get())
        except ValueError:
            messagebox.showwarning('Invalid Input',
                                 'Please select a valid number of training days')
            return
        
        # Disable UI
        self.prediction_in_progress = True
        self.predict_btn.config(state='disabled')
        self.djia_btn.config(state='disabled', text='⏳ Predicting DJIA...')
        self.ticker_entry.config(state='disabled')
        self.days_combo.config(state='disabled')
        
        self.status_var.set('Predicting DJIA stocks... This may take a minute.')
        self.progress.pack(side='right')
        self.progress.start()
        
        # Run in thread
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
            for i, ticker in enumerate(tickers[:10]):  # First 10 for demo
                self.root.after(0, lambda t=ticker: 
                    self.status_var.set(f'Predicting {t}... ({i+1}/10)'))
                pred.process_company(ticker, days, 
                                   self.use_spread.get(), 
                                   self.use_volume.get())
            
            output = buffer.getvalue()
            sys.stdout = old_stdout
            
            self.root.after(0, self.show_results, 'DJIA (Top 10)', output)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set DPI awareness for sharper text on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    
    app = StockPredictorGUI(root)
    
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
