# 📈 Stock Predictor

A user-friendly stock price prediction application powered by Machine Learning and Technical Analysis.

![Stock Predictor](prediction_10_31.png)

## ✨ What's New in Version 2.1

- 🎯 **Enhanced Predictions** with Technical Indicators (RSI, MACD, SMA, EMA)
- 📅 **Smart Trading Day Detection** - Predicts for next market open (handles weekends & holidays)
- 📊 **Flexible Training Periods** - Choose 90, 180, or 360 days (90 recommended)
- 📋 **Clear Instructions** - Built-in guide on startup
- 🔍 **Smart Autocomplete** - Search stocks as you type
- 📈 **Visual Charts** - Interactive price charts with moving averages

## 🚀 Quick Start

### Windows Users
Double-click: **`Run_Stock_Predictor.bat`**

### Mac/Linux Users
```bash
bash run_stock_predictor.sh
```

### Manual Method
```bash
pip install -r requirements.txt
cd Predictor
python stock_predictor_gui.py
```

## 📋 How to Use (Step-by-Step Guide)

When you start the app, you'll see clear instructions on the left side:

### 1. Enter a Stock Ticker
- Type in the "Stock Ticker Symbol" field
- Watch suggestions appear as you type
- Click on a suggestion or press Enter

**Examples:** AAPL (Apple), MSFT (Microsoft), TSLA (Tesla)

### 2. Select Training Period
Choose how many days of historical data to use:
- **90 days** (Recommended) - Best balance of speed and accuracy
- **180 days** - More accurate, uses more history
- **360 days** - Maximum accuracy, best for stable stocks

### 3. Choose Features
Select which data points to include in the prediction:
- ✅ **Price Change** - Daily price movement (Recommended)
- ☐ **Trading Volume** - Number of shares traded
- ✅ **Technical Indicators** - RSI, MACD, SMA, EMA (Recommended)

### 4. Click "Predict Price"
Wait a few seconds for the prediction.

### 5. View Results
- **Predicted Price** - Closing price for the next trading day
- **Current Price** - Current market price
- **Visual Chart** - 90-day price history with moving average

## 🧠 Technical Indicators Explained

Our prediction engine now uses professional technical analysis indicators:

### RSI (Relative Strength Index)
- Measures momentum and identifies overbought/oversold conditions
- Range: 0-100 (70+ = overbought, 30- = oversold)

### MACD (Moving Average Convergence Divergence)
- Shows trend direction and momentum
- Helps identify buy/sell signals

### SMA (Simple Moving Average)
- 20-day average price
- Shows overall price trend

### EMA (Exponential Moving Average)
- 12-day weighted average
- Responds faster to recent price changes

These indicators help the machine learning algorithm make more accurate predictions by providing additional market context.

## 🎯 Popular Stock Tickers

| Ticker | Company | Sector |
|--------|---------|--------|
| **AAPL** | Apple Inc. | Technology |
| **MSFT** | Microsoft | Technology |
| **GOOGL** | Google | Technology |
| **AMZN** | Amazon | Consumer |
| **TSLA** | Tesla | Automotive |
| **META** | Meta (Facebook) | Technology |
| **NVDA** | NVIDIA | Semiconductors |
| **NFLX** | Netflix | Entertainment |
| **AMD** | AMD | Semiconductors |
| **DIS** | Disney | Entertainment |

**Tip:** Type any ticker to search - we have 100+ stocks in our database!

## 📊 Training Period Guide

### 90 Days (Recommended)
- **Best for:** Most stocks, beginners
- **Pros:** Fast, good accuracy, captures recent trends
- **Cons:** May miss long-term patterns

### 180 Days
- **Best for:** Stable stocks, seasonal patterns
- **Pros:** More accurate, sees medium-term trends
- **Cons:** Slower, may include outdated trends

### 360 Days
- **Best for:** Long-term investments, stable companies
- **Pros:** Maximum accuracy, sees yearly patterns
- **Cons:** Slowest, may be influenced by old data

**Recommendation:** Start with 90 days and experiment with longer periods for better results.

## 🛠️ System Requirements

- **Python 3.8** or higher
- **Internet connection** (for real-time stock data)
- **Any modern computer** (Windows, Mac, or Linux)

## 📦 Installation

### Step 1: Install Python
Download from [python.org](https://python.org)

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `yfinance` - Stock data from Yahoo Finance
- `scikit-learn` - Machine learning algorithms
- `matplotlib` - Chart visualization
- `numpy` - Numerical computations
- `pandas` - Data analysis

### Step 3: Run the App
```bash
cd Predictor
python stock_predictor_gui.py
```

## 🔧 Troubleshooting

### "No module found" Error
```bash
pip install -r requirements.txt
```

### "No data found" Error
- Check internet connection
- Verify ticker symbol on [finance.yahoo.com](https://finance.yahoo.com)
- Market may be closed (weekend/holiday)

### Predictions Seem Wrong
- Try different training periods (90, 180, 360 days)
- Enable more features (Technical Indicators recommended)
- Remember: predictions are probabilistic, not guaranteed

### Charts Not Displaying
```bash
pip install matplotlib
```

## 📈 How It Works

1. **Data Collection** - Fetches historical prices from Yahoo Finance
2. **Technical Analysis** - Calculates RSI, MACD, SMA, EMA indicators
3. **Feature Engineering** - Combines price data with technical indicators
4. **Machine Learning** - SVM algorithm learns patterns from historical data
5. **Prediction** - Forecasts next trading day's closing price
6. **Smart Scheduling** - Automatically skips weekends and market holidays

## 📁 Project Structure

```
AI-Project/
├── Predictor/
│   ├── stock_predictor_gui.py    # Main GUI application
│   ├── predictor.py              # Core ML prediction logic
│   ├── get_historical.py         # Historical data + technical indicators
│   ├── current_trading_day.py    # Current day data processing
│   ├── trading_day.py            # Trading calendar & holidays
│   ├── normalize.py              # Data normalization
│   └── company_name.py           # Company lookups
├── Run_Stock_Predictor.bat       # Windows launcher
├── run_stock_predictor.sh        # Mac/Linux launcher
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 👥 Contributors

- **Prakash Dhimal** ([@pdhimal1](https://github.com/pdhimal1))
- **Kevin Sanford**

## 📝 Version History

### Version 2.1 (Current)
- ✅ Technical indicators (RSI, MACD, SMA, EMA)
- ✅ 90/180/360 day training options
- ✅ Built-in usage instructions
- ✅ Smart next-trading-day detection

### Version 2.0
- ✅ Modern dark UI
- ✅ Autocomplete for stocks
- ✅ Visual charts
- ✅ Easy launcher scripts

### Version 1.0
- ✅ Basic command-line interface
- ✅ Python 2.7 support

## ⚠️ Disclaimer

**This software is for educational purposes only.**

- Stock predictions are **never 100% accurate**
- Past performance doesn't guarantee future results
- Always consult a financial advisor before investing
- The authors are **not responsible** for any financial losses

**Remember:** Never invest money you cannot afford to lose.

---

## 💡 Pro Tips

1. **Start with 90 days** - It's the sweet spot for most stocks
2. **Enable Technical Indicators** - They significantly improve accuracy
3. **Try Popular Stocks First** - AAPL, MSFT, GOOGL have good historical data
4. **Compare Different Periods** - Run predictions with 90, 180, and 360 days
5. **Check the Chart** - Visual trends often tell more than numbers

**Happy Predicting! 📈🚀**
