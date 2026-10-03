/*
 * model.js - browser port of the Predictor/ pipeline.
 *
 *   get_historical.py   -> sma / ema / rsi / macd, buildRows
 *   normalize.py        -> MinMax scaling to [-1, 1]
 *   predictor.py        -> epsilon-SVR with an RBF kernel (trainSVR)
 *   trading_day.py      -> nextTradingDay
 *
 * Differences from the 2017 Python version, on purpose:
 *   - each feature gets its own scaler (the original scaled volume and RSI with the opening-price scaler)
 *   - the target is the next day's close, built from today's finished bar (no same-day leakage)
 *   - the SVR learns the next-day *return*, so an RBF kernel isn't asked to extrapolate to new price highs
 */
(function (root) {
  "use strict";

  // ---------- technical indicators (same definitions as get_historical.py) ----------
  const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;

  function sma(data, w) {
    return data.map((_, i) => mean(data.slice(Math.max(0, i - w + 1), i + 1)));
  }

  function ema(data, w) {
    if (data.length < w) return data.map(() => mean(data));
    const k = 2 / (w + 1);
    const out = new Array(w - 1).fill(0);
    let prev = mean(data.slice(0, w));
    out.push(prev);
    for (let i = w; i < data.length; i++) { prev = (data[i] - prev) * k + prev; out.push(prev); }
    for (let i = 0; i < w - 1; i++) out[i] = out[w - 1];
    return out;
  }

  function rsi(data, w = 14) {
    if (data.length < w + 1) return data.map(() => 50);
    const gains = [0], losses = [0];
    for (let i = 1; i < data.length; i++) {
      const d = data[i] - data[i - 1];
      gains.push(Math.max(0, d)); losses.push(Math.max(0, -d));
    }
    let ag = mean(gains.slice(1, w + 1)), al = mean(losses.slice(1, w + 1));
    const out = new Array(w).fill(50);
    for (let i = w; i < data.length; i++) {
      ag = (ag * (w - 1) + gains[i]) / w;
      al = (al * (w - 1) + losses[i]) / w;
      out.push(al === 0 ? 100 : 100 - 100 / (1 + ag / al));
    }
    return out;
  }

  function macd(data, fast = 12, slow = 26, signal = 9) {
    if (data.length < slow) return { line: data.map(() => 0), signal: data.map(() => 0) };
    const f = ema(data, fast), s = ema(data, slow);
    const line = f.map((v, i) => v - s[i]);
    return { line, signal: ema(line, signal) };
  }

  function indicators(bars) {
    const close = bars.map((b) => b.close);
    const m = macd(close);
    return { sma20: sma(close, 20), ema12: ema(close, 12), rsi14: rsi(close, 14), macd: m.line, macdSignal: m.signal };
  }

  // ---------- feature rows ----------
  // One row per day: [open, high, low, close, (change), (volume), (sma20, ema12, rsi14, macd)]
  function buildRows(bars, ind, opts) {
    return bars.map((b, i) => {
      const row = [b.open, b.high, b.low, b.close];
      if (opts.useChange) row.push(i ? b.close - bars[i - 1].close : 0);
      if (opts.useVolume) row.push(b.volume);
      if (opts.useTech) row.push(ind.sma20[i], ind.ema12[i], ind.rsi14[i], ind.macd[i]);
      return row;
    });
  }

  function featureNames(opts) {
    const n = ["Open", "High", "Low", "Close"];
    if (opts.useChange) n.push("Price change");
    if (opts.useVolume) n.push("Volume");
    if (opts.useTech) n.push("SMA 20", "EMA 12", "RSI 14", "MACD");
    return n;
  }

  // ---------- MinMax scaler to [-1, 1], one per column ----------
  function fitScaler(rows) {
    const d = rows[0].length, lo = new Array(d).fill(Infinity), hi = new Array(d).fill(-Infinity);
    rows.forEach((r) => r.forEach((v, j) => { if (v < lo[j]) lo[j] = v; if (v > hi[j]) hi[j] = v; }));
    return (r) => r.map((v, j) => (hi[j] === lo[j] ? 0 : (2 * (v - lo[j])) / (hi[j] - lo[j]) - 1));
  }

  // ---------- epsilon-SVR, RBF kernel ----------
  // Dual coordinate descent on  min 1/2 b'Kb - y'b + eps*|b|_1,  -C <= b_i <= C,
  // with the bias folded into the kernel (K + 1). Small n (<= 360), so this converges fast.
  function trainSVR(X, y, { C = 1, eps = 0.1, gamma = 0.1, maxSweeps = 400, tol = 1e-6 } = {}) {
    const n = X.length;
    const kern = (a, b) => { let s = 0; for (let j = 0; j < a.length; j++) { const d = a[j] - b[j]; s += d * d; } return Math.exp(-gamma * s) + 1; };
    const K = Array.from({ length: n }, () => new Float64Array(n));
    for (let i = 0; i < n; i++) for (let j = i; j < n; j++) K[i][j] = K[j][i] = kern(X[i], X[j]);

    const beta = new Float64Array(n), g = Float64Array.from(y, (v) => -v);
    const order = [...Array(n).keys()];
    for (let sweep = 0; sweep < maxSweeps; sweep++) {
      for (let i = n - 1; i > 0; i--) { const j = (i * 7919 + sweep) % (i + 1); [order[i], order[j]] = [order[j], order[i]]; }
      let maxDelta = 0;
      for (const i of order) {
        const z = beta[i] - g[i] / K[i][i];
        let nb = Math.sign(z) * Math.max(Math.abs(z) - eps / K[i][i], 0);
        nb = Math.min(C, Math.max(-C, nb));
        const d = nb - beta[i];
        if (d !== 0) {
          beta[i] = nb;
          const Ki = K[i];
          for (let k = 0; k < n; k++) g[k] += d * Ki[k];
          if (Math.abs(d) > maxDelta) maxDelta = Math.abs(d);
        }
      }
      if (maxDelta < tol) break;
    }
    const support = [];
    for (let i = 0; i < n; i++) if (beta[i] !== 0) support.push(i);
    return {
      predict: (x) => support.reduce((s, i) => s + beta[i] * kern(X[i], x), 0),
      supportVectors: support.length,
    };
  }

  // ---------- one prediction: train on `window` days ending at index `end`, predict close[end + 1] ----------
  function predictAt(bars, rows, end, window) {
    const start = Math.max(1, end - window);           // sample t uses row t -> return from close[t] to close[t+1]
    const idx = [];
    for (let t = start; t < end; t++) idx.push(t);
    const scale = fitScaler(idx.map((t) => rows[t]).concat([rows[end]]));
    const X = idx.map((t) => scale(rows[t]));
    const ret = idx.map((t) => bars[t + 1].close / bars[t].close - 1);
    const sd = Math.sqrt(mean(ret.map((r) => r * r))) || 1e-4;
    const model = trainSVR(X, ret.map((r) => r / sd), { C: 1, eps: 0.1, gamma: 1 / X[0].length });
    const r = model.predict(scale(rows[end])) * sd;
    return { price: bars[end].close * (1 + r), ret: r, supportVectors: model.supportVectors, samples: X.length };
  }

  function run(bars, opts) {
    const ind = indicators(bars);
    const rows = buildRows(bars, ind, opts);
    const last = bars.length - 1;
    const window = Math.min(opts.window, last - 1);

    const next = predictAt(bars, rows, last, window);

    // Walk-forward backtest: for each of the last N days, train only on what was known the day before.
    const N = Math.min(opts.backtestDays || 20, last - window - 1);
    const backtest = [];
    for (let d = last - N + 1; d <= last; d++) {
      const p = predictAt(bars, rows, d - 1, window);
      const prev = bars[d - 1].close, actual = bars[d].close;
      backtest.push({
        date: bars[d].date, prev, actual, predicted: p.price,
        hitDirection: Math.sign(p.price - prev) === Math.sign(actual - prev),
      });
    }
    const mae = (f) => mean(backtest.map(f));
    const metrics = backtest.length ? {
      modelMAE: mae((b) => Math.abs(b.predicted - b.actual)),
      naiveMAE: mae((b) => Math.abs(b.prev - b.actual)),
      directionHits: backtest.filter((b) => b.hitDirection).length,
      beatNaive: backtest.filter((b) => Math.abs(b.predicted - b.actual) < Math.abs(b.prev - b.actual)).length,
      days: backtest.length,
    } : null;

    return {
      next, backtest, metrics, indicators: ind,
      lastBar: bars[last], features: featureNames(opts), window,
      latest: { rsi: ind.rsi14[last], macd: ind.macd[last], macdSignal: ind.macdSignal[last], sma20: ind.sma20[last], ema12: ind.ema12[last] },
    };
  }

  // ---------- trading calendar (NYSE full-day closures) ----------
  const HOLIDAYS = new Set([
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
  ]);

  function nextTradingDay(isoDate) {
    const d = new Date(isoDate + "T12:00:00Z");
    do { d.setUTCDate(d.getUTCDate() + 1); } while (d.getUTCDay() === 0 || d.getUTCDay() === 6 || HOLIDAYS.has(d.toISOString().slice(0, 10)));
    return d.toISOString().slice(0, 10);
  }

  const api = { sma, ema, rsi, macd, indicators, trainSVR, run, nextTradingDay, featureNames };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.StockModel = api;
})(this);
