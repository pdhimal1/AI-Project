// Vercel serverless function: daily OHLCV history for one ticker.
// Proxies Yahoo Finance's chart endpoint (browsers can't call it directly - no CORS)
// and returns a compact JSON shape the web app understands.
//
//   GET /api/history?symbol=AAPL&range=2y

const RANGES = new Set(["6mo", "1y", "2y", "5y"]);

function etParts(epochSeconds) {
  const fmt = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/New_York",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", hour12: false,
  });
  const p = Object.fromEntries(fmt.formatToParts(new Date(epochSeconds * 1000)).map((x) => [x.type, x.value]));
  return { date: `${p.year}-${p.month}-${p.day}`, hour: Number(p.hour) % 24 };
}

module.exports = async (req, res) => {
  const symbol = String(req.query.symbol || "").trim().toUpperCase();
  const range = RANGES.has(req.query.range) ? req.query.range : "2y";

  if (!/^[A-Z0-9.\-^=]{1,15}$/.test(symbol)) {
    res.status(400).json({ error: "Invalid ticker symbol." });
    return;
  }

  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?range=${range}&interval=1d&includePrePost=false`;

  try {
    const r = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0 (stock-predictor; educational)" } });
    const body = await r.json().catch(() => null);
    const result = body && body.chart && body.chart.result && body.chart.result[0];

    if (!r.ok || !result || !result.timestamp) {
      const msg = (body && body.chart && body.chart.error && body.chart.error.description) || `No data found for ${symbol}.`;
      res.status(r.status === 404 || !result ? 404 : 502).json({ error: msg });
      return;
    }

    const q = result.indicators.quote[0];
    const meta = result.meta;
    const now = etParts(Date.now() / 1000);
    const bars = [];

    result.timestamp.forEach((t, i) => {
      if ([q.open[i], q.high[i], q.low[i], q.close[i]].some((v) => v == null)) return;
      bars.push({
        date: etParts(t).date,
        open: q.open[i], high: q.high[i], low: q.low[i], close: q.close[i],
        volume: q.volume[i] || 0,
      });
    });

    // Drop today's bar while the market is still open - it isn't a finished day yet.
    let partial = null;
    const last = bars[bars.length - 1];
    if (last && last.date === now.date && now.hour < 16) partial = bars.pop();

    res.setHeader("Cache-Control", "s-maxage=900, stale-while-revalidate=3600");
    res.status(200).json({
      symbol: meta.symbol,
      name: meta.longName || meta.shortName || meta.symbol,
      exchange: meta.fullExchangeName || meta.exchangeName,
      currency: meta.currency,
      marketPrice: meta.regularMarketPrice,
      partial,
      bars,
      source: "live",
    });
  } catch (err) {
    res.status(502).json({ error: "Couldn't reach the market data provider." });
  }
};
