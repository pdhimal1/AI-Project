"""
Trading Day Calculator Module
Calculates next trading day accounting for weekends and market holidays.
"""
from datetime import datetime, timedelta

# US Stock Market Holidays for 2025-2026 (NYSE & NASDAQ)
# Format: MM-DD
MARKET_HOLIDAYS_2025 = [
    '01-01',  # New Year's Day
    '01-20',  # Martin Luther King Jr. Day
    '02-17',  # Presidents' Day
    '04-18',  # Good Friday
    '05-26',  # Memorial Day
    '06-19',  # Juneteenth
    '07-04',  # Independence Day
    '09-01',  # Labor Day
    '11-27',  # Thanksgiving
    '12-25',  # Christmas Day
]

MARKET_HOLIDAYS_2026 = [
    '01-01',  # New Year's Day
    '01-19',  # Martin Luther King Jr. Day
    '02-16',  # Presidents' Day
    '04-03',  # Good Friday
    '05-25',  # Memorial Day
    '06-19',  # Juneteenth
    '07-03',  # Independence Day (observed)
    '09-07',  # Labor Day
    '11-26',  # Thanksgiving
    '12-25',  # Christmas Day
]

def is_market_holiday(date):
    """Check if a date is a US stock market holiday"""
    date_str = date.strftime('%m-%d')
    year = date.year
    
    if year == 2025 and date_str in MARKET_HOLIDAYS_2025:
        return True
    elif year == 2026 and date_str in MARKET_HOLIDAYS_2026:
        return True
    
    return False

def is_weekend(date):
    """Check if date is Saturday (5) or Sunday (6)"""
    return date.weekday() >= 5

def get_next_trading_day(from_date=None):
    """
    Get the next trading day from a given date (or today if not specified).
    Accounts for weekends and market holidays.
    
    @param from_date: datetime object (defaults to today)
    @return: datetime object of next trading day
    """
    if from_date is None:
        from_date = datetime.now()
    
    # Start with tomorrow
    next_day = from_date + timedelta(days=1)
    
    # Keep adding days until we find a trading day
    while is_weekend(next_day) or is_market_holiday(next_day):
        next_day += timedelta(days=1)
    
    return next_day

def get_trading_day_string(from_date=None, format='%Y-%m-%d'):
    """
    Get the next trading day as a formatted string.
    
    @param from_date: datetime object (defaults to today)
    @param format: date format string
    @return: formatted date string
    """
    trading_day = get_next_trading_day(from_date)
    return trading_day.strftime(format)

def format_trading_day_with_weekday(date):
    """
    Format a date with weekday name for display.
    Example: "Monday, February 17, 2025"
    """
    return date.strftime('%A, %B %d, %Y')

# Common stock tickers for autocomplete
POPULAR_STOCKS = {
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'GOOGL': 'Alphabet Inc. (Google)',
    'GOOG': 'Alphabet Inc. (Google)',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'META': 'Meta Platforms Inc. (Facebook)',
    'NVDA': 'NVIDIA Corporation',
    'NFLX': 'Netflix Inc.',
    'AMD': 'Advanced Micro Devices',
    'INTC': 'Intel Corporation',
    'DIS': 'Walt Disney Co.',
    'V': 'Visa Inc.',
    'MA': 'Mastercard Inc.',
    'JPM': 'JPMorgan Chase & Co.',
    'BAC': 'Bank of America Corp.',
    'WMT': 'Walmart Inc.',
    'KO': 'Coca-Cola Co.',
    'PEP': 'PepsiCo Inc.',
    'PG': 'Procter & Gamble Co.',
    'JNJ': 'Johnson & Johnson',
    'PFE': 'Pfizer Inc.',
    'MRK': 'Merck & Co.',
    'UNH': 'UnitedHealth Group',
    'ABBV': 'AbbVie Inc.',
    'T': 'AT&T Inc.',
    'VZ': 'Verizon Communications',
    'XOM': 'Exxon Mobil Corp.',
    'CVX': 'Chevron Corporation',
    'COP': 'ConocoPhillips',
    'BA': 'Boeing Co.',
    'GE': 'General Electric Co.',
    'MMM': '3M Company',
    'CAT': 'Caterpillar Inc.',
    'HON': 'Honeywell International',
    'RTX': 'Raytheon Technologies',
    'GS': 'Goldman Sachs Group',
    'MS': 'Morgan Stanley',
    'C': 'Citigroup Inc.',
    'WFC': 'Wells Fargo & Co.',
    'IBM': 'International Business Machines',
    'CRM': 'Salesforce Inc.',
    'ORCL': 'Oracle Corporation',
    'ADBE': 'Adobe Inc.',
    'CRM': 'Salesforce Inc.',
    'PYPL': 'PayPal Holdings Inc.',
    'UBER': 'Uber Technologies Inc.',
    'LYFT': 'Lyft Inc.',
    'ABNB': 'Airbnb Inc.',
    'ZM': 'Zoom Video Communications',
    'SHOP': 'Shopify Inc.',
    'SQ': 'Block Inc. (Square)',
    'COIN': 'Coinbase Global Inc.',
    'PLTR': 'Palantir Technologies',
    'RBLX': 'Roblox Corporation',
    'SNOW': 'Snowflake Inc.',
    'ROKU': 'Roku Inc.',
    'TWLO': 'Twilio Inc.',
    'DDOG': 'Datadog Inc.',
    'NET': 'Cloudflare Inc.',
    'CRWD': 'CrowdStrike Holdings',
    'OKTA': 'Okta Inc.',
    'DOCU': 'DocuSign Inc.',
    'FTNT': 'Fortinet Inc.',
    'PANW': 'Palo Alto Networks',
    'ZS': 'Zscaler Inc.',
    'MDB': 'MongoDB Inc.',
    'S': 'SentinelOne Inc.',
    'CSCO': 'Cisco Systems',
    'QCOM': 'Qualcomm Inc.',
    'TXN': 'Texas Instruments',
    'AVGO': 'Broadcom Inc.',
    'MU': 'Micron Technology',
    'LRCX': 'Lam Research',
    'AMAT': 'Applied Materials',
    'KLAC': 'KLA Corporation',
    'SNPS': 'Synopsys Inc.',
    'CDNS': 'Cadence Design Systems',
    'ANSS': 'Ansys Inc.',
    'FTV': 'Fortive Corporation',
    'KEYS': 'Keysight Technologies',
    'TEL': 'TE Connectivity',
    'APH': 'Amphenol Corporation',
    'GLW': 'Corning Inc.',
    'JCI': 'Johnson Controls',
    'TT': 'Trane Technologies',
    'OTIS': 'Otis Worldwide',
    'CARR': 'Carrier Global',
    'GE': 'GE Aerospace',
    'GEV': 'GE Vernova',
}

def get_stock_suggestions(query):
    """
    Get stock suggestions based on partial ticker or company name.
    
    @param query: partial string to search
    @return: list of matching (ticker, company_name) tuples
    """
    query = query.upper()
    suggestions = []
    
    for ticker, name in POPULAR_STOCKS.items():
        if query in ticker or query in name.upper():
            suggestions.append((ticker, name))
    
    return suggestions[:10]  # Limit to 10 suggestions

def get_all_tickers():
    """Get list of all popular stock tickers for dropdown"""
    return list(POPULAR_STOCKS.keys())

