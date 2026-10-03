'''
Builds the static data files used by the web app (web/data/):
  - tickers.json        US-listed tickers from Data/Stock.csv, for autocomplete
  - sample-<TICKER>.json offline snapshots, used when live data can't be fetched

Usage:
	python scripts/build_web_data.py
'''

import csv
import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'web', 'data')
US_EXCHANGES = {'NYQ', 'NMS', 'NGM', 'NCM', 'ASE'}
SAMPLES = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'GOOGL', 'KO']
# Newer / renamed tickers missing from the 2017-era Stock.csv
EXTRA = {
	'META': 'Meta Platforms, Inc.', 'GOOGL': 'Alphabet Inc. Class A', 'GOOG': 'Alphabet Inc. Class C',
	'TSLA': 'Tesla, Inc.', 'NVDA': 'NVIDIA Corporation', 'AMD': 'Advanced Micro Devices, Inc.',
	'NFLX': 'Netflix, Inc.', 'PLTR': 'Palantir Technologies Inc.', 'UBER': 'Uber Technologies, Inc.',
	'ABNB': 'Airbnb, Inc.', 'COIN': 'Coinbase Global, Inc.', 'SNOW': 'Snowflake Inc.',
	'SPY': 'SPDR S&P 500 ETF Trust', 'QQQ': 'Invesco QQQ Trust', 'DIA': 'SPDR Dow Jones Industrial Average ETF',
	'AVGO': 'Broadcom Inc.', 'CRM': 'Salesforce, Inc.', 'SHOP': 'Shopify Inc.', 'RTX': 'RTX Corporation',
}


def build_tickers():
	tickers = {}
	with open(os.path.join(ROOT, 'Data', 'Stock.csv'), newline='', encoding='utf-8', errors='ignore') as f:
		for row in csv.DictReader(f):
			t = (row.get('Ticker') or '').strip().upper()
			if row.get('Exchange') in US_EXCHANGES and t and '.' not in t:
				tickers[t] = (row.get('Name') or '').strip()
	tickers.update(EXTRA)
	rows = sorted([t, n] for t, n in tickers.items())
	with open(os.path.join(OUT, 'tickers.json'), 'w', encoding='utf-8') as f:
		json.dump(rows, f, separators=(',', ':'))
	print('tickers.json:', len(rows), 'tickers')


def build_sample(symbol):
	url = 'https://query1.finance.yahoo.com/v8/finance/chart/%s?range=2y&interval=1d' % symbol
	req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	data = json.load(urllib.request.urlopen(req))['chart']['result'][0]
	q, meta = data['indicators']['quote'][0], data['meta']
	et = timezone(timedelta(hours=-4))
	bars = []
	for i, t in enumerate(data['timestamp']):
		vals = [q['open'][i], q['high'][i], q['low'][i], q['close'][i]]
		if None in vals:
			continue
		bars.append({
			'date': datetime.fromtimestamp(t, et).strftime('%Y-%m-%d'),
			'open': round(vals[0], 4), 'high': round(vals[1], 4), 'low': round(vals[2], 4),
			'close': round(vals[3], 4), 'volume': q['volume'][i] or 0,
		})
	out = {
		'symbol': meta['symbol'], 'name': meta.get('longName') or meta.get('shortName') or symbol,
		'exchange': meta.get('fullExchangeName'), 'currency': meta.get('currency'),
		'marketPrice': meta.get('regularMarketPrice'), 'partial': None, 'bars': bars, 'source': 'snapshot',
	}
	with open(os.path.join(OUT, 'sample-%s.json' % symbol), 'w', encoding='utf-8') as f:
		json.dump(out, f, separators=(',', ':'))
	print('sample-%s.json:' % symbol, len(bars), 'bars, last', bars[-1]['date'])


if __name__ == '__main__':
	os.makedirs(OUT, exist_ok=True)
	build_tickers()
	for s in SAMPLES:
		build_sample(s)
