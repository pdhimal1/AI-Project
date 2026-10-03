/* app.js - UI for the Stock Predictor web port. Model code lives in model.js. */
(function () {
  "use strict";

  const SAMPLES = ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "KO"];
  const $ = (id) => document.getElementById(id);
  const state = { window: 90, tickers: [], cache: new Map(), chart: null, running: false };

  const fmtMoney = (v, cur = "USD") => new Intl.NumberFormat("en-US", { style: "currency", currency: cur || "USD", minimumFractionDigits: 2 }).format(v);
  const fmtPct = (v) => (v >= 0 ? "+" : "−") + Math.abs(v * 100).toFixed(2) + "%";
  const fmtDate = (iso, opts = { weekday: "short", month: "short", day: "numeric" }) =>
    new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { timeZone: "UTC", ...opts });
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // ---------------- data ----------------
  async function loadHistory(symbol) {
    if (state.cache.has(symbol)) return state.cache.get(symbol);
    let data, liveError;
    try {
      const r = await fetch(`/api/history?symbol=${encodeURIComponent(symbol)}&range=2y`);
      const body = await r.json();
      if (!r.ok) throw Object.assign(new Error(body.error || "Request failed"), { status: r.status });
      data = body;
    } catch (e) {
      liveError = e;
    }
    if (!data && SAMPLES.includes(symbol)) {
      const r = await fetch(`data/sample-${symbol}.json`);
      if (r.ok) data = await r.json();
    }
    if (!data) {
      const msg = liveError && liveError.status === 404
        ? `No price data found for “${symbol}”. Check the ticker symbol.`
        : `Live market data is unavailable right now. Offline snapshots are available for ${SAMPLES.join(", ")}.`;
      throw new Error(msg);
    }
    if (data.bars.length < 60) throw new Error(`Not enough trading history for ${symbol} (${data.bars.length} days).`);
    state.cache.set(symbol, data);
    return data;
  }

  // ---------------- run ----------------
  async function predict() {
    if (state.running) return;
    const symbol = $("ticker").value.trim().toUpperCase();
    if (!symbol) return;
    hideSuggest();
    state.running = true;
    $("go").disabled = true;
    $("go").textContent = "Training…";
    document.querySelector(".results").classList.add("loading");
    showNotice(null);

    try {
      const data = await loadHistory(symbol);
      await new Promise((r) => setTimeout(r, 20)); // let the loading state paint
      const opts = {
        window: state.window,
        useChange: $("useChange").checked,
        useVolume: $("useVolume").checked,
        useTech: $("useTech").checked,
        backtestDays: 20,
      };
      const res = StockModel.run(data.bars, opts);
      render(data, res);
      if (data.source === "snapshot") {
        showNotice(`Live data couldn't be loaded, so this uses a saved snapshot ending ${fmtDate(res.lastBar.date, { month: "long", day: "numeric", year: "numeric" })}.`);
      }
      try { history.replaceState(null, "", `?t=${symbol}&w=${state.window}`); } catch (_) {}
    } catch (e) {
      showNotice(e.message, true);
    } finally {
      state.running = false;
      $("go").disabled = false;
      $("go").textContent = "Predict price";
      document.querySelector(".results").classList.remove("loading");
    }
  }

  function showNotice(msg, isError) {
    const n = $("notice");
    n.hidden = !msg;
    n.className = "notice" + (isError ? " error" : "");
    n.textContent = msg || "";
    if (msg && isError) n.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  // ---------------- render ----------------
  function render(data, res) {
    const cur = data.currency;
    const last = res.lastBar;
    const nextDay = StockModel.nextTradingDay(last.date);
    const move = res.next.price / last.close - 1;

    $("coName").innerHTML = `${esc(data.name)}<span class="tk">${esc(data.symbol)}</span>`;
    $("coMeta").textContent = [data.exchange, cur].filter(Boolean).join(" · ");
    const badge = $("direction");
    badge.className = "badge " + (move >= 0 ? "up" : "down");
    badge.textContent = (move >= 0 ? "▲ Model leans up" : "▼ Model leans down");

    $("predLabel").textContent = `Predicted close · ${fmtDate(nextDay)}`;
    $("predValue").textContent = fmtMoney(res.next.price, cur);
    $("predSub").innerHTML = `<span class="${move >= 0 ? "up" : "down"}">${fmtPct(move)}</span> vs last close`;

    $("lastLabel").textContent = `Last close · ${fmtDate(last.date)}`;
    $("lastValue").textContent = fmtMoney(last.close, cur);
    const prev = data.bars[data.bars.length - 2];
    const dayMove = last.close / prev.close - 1;
    $("lastSub").innerHTML = `<span class="${dayMove >= 0 ? "up" : "down"}">${fmtPct(dayMove)}</span> on the day`;

    $("modelValue").textContent = "SVR · RBF kernel";
    $("modelSub").textContent = `${res.next.samples} training days · ${res.features.length} features · ${res.next.supportVectors} support vectors`;

    renderChart(data, res, nextDay);
    renderBacktest(res, cur);
    renderIndicators(res, cur);
  }

  function renderChart(data, res, nextDay) {
    const show = Math.max(90, Math.min(res.window, 180));
    const bars = data.bars.slice(-show);
    const offset = data.bars.length - show;
    const labels = bars.map((b) => b.date).concat(nextDay);
    const close = bars.map((b) => b.close).concat(null);
    const sma = res.indicators.sma20.slice(offset).concat(null);
    const bt = new Map(res.backtest.map((b) => [b.date, b.predicted]));
    const btPts = labels.map((d) => (bt.has(d) ? bt.get(d) : null));
    const nextPts = labels.map((_, i) => (i === labels.length - 1 ? res.next.price : i === labels.length - 2 ? res.lastBar.close : null));

    const c = { close: css("--chart-close"), sma: css("--chart-sma"), bt: css("--chart-bt"), next: css("--chart-next"), grid: css("--chart-grid"), muted: css("--muted"), surface: css("--surface") };
    const money = (v) => fmtMoney(v, data.currency);

    const cfg = {
      type: "line",
      data: {
        labels,
        datasets: [
          { label: "Close", data: close, borderColor: c.close, borderWidth: 1.8, pointRadius: 0, tension: 0.15 },
          { label: "SMA 20", data: sma, borderColor: c.sma, borderWidth: 1.4, borderDash: [5, 4], pointRadius: 0, tension: 0.2 },
          { label: "Backtest prediction", data: btPts, borderColor: c.bt, backgroundColor: c.bt, showLine: false, pointRadius: 3.5, pointHoverRadius: 5 },
          { label: "Next-day prediction", data: nextPts, borderColor: c.next, backgroundColor: c.next, borderDash: [4, 4], borderWidth: 2,
            pointRadius: (ctx) => (ctx.dataIndex === labels.length - 1 ? 6 : 0), pointBorderColor: c.surface, pointBorderWidth: 2, spanGaps: true },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 350 },
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            filter: (item) => item.raw != null && !(item.datasetIndex === 3 && item.dataIndex !== labels.length - 1),
            callbacks: {
              title: (items) => fmtDate(items[0].label, { weekday: "short", month: "short", day: "numeric", year: "numeric" }),
              label: (item) => ` ${item.dataset.label}: ${money(item.raw)}`,
            },
          },
        },
        scales: {
          x: { grid: { display: false }, border: { display: false },
               ticks: { color: c.muted, maxRotation: 0, autoSkip: true, maxTicksLimit: 7, callback: (_, i) => fmtDate(labels[i], { month: "short", day: "numeric" }) } },
          y: { position: "right", grid: { color: c.grid }, border: { display: false }, ticks: { color: c.muted, maxTicksLimit: 6, callback: (v) => money(v).replace(/\.00$/, "") } },
        },
      },
    };
    if (state.chart) state.chart.destroy();
    state.chart = new Chart($("chart"), cfg);
  }

  function renderBacktest(res, cur) {
    const m = res.metrics;
    if (!m) { $("stats").innerHTML = ""; $("verdict").textContent = "Not enough history for a backtest."; return; }
    const pct = (n) => Math.round((100 * n) / m.days) + "%";
    $("stats").innerHTML = [
      [`${m.directionHits}/${m.days}`, `Direction right (${pct(m.directionHits)})`],
      [fmtMoney(m.modelMAE, cur), "Model avg. error"],
      [fmtMoney(m.naiveMAE, cur), "“No change” avg. error"],
      [`${m.beatNaive}/${m.days}`, "Days closer than “no change”"],
    ].map(([v, l]) => `<div class="stat"><div class="v">${v}</div><div class="l">${l}</div></div>`).join("");

    const ratio = m.modelMAE / m.naiveMAE;
    let verdict;
    if (ratio < 0.95) verdict = `Over this stretch the SVR beat the simple “tomorrow = today” guess. Try other windows and tickers before trusting it, though: small backtests are noisy.`;
    else if (ratio <= 1.05) verdict = `The SVR did about as well as simply guessing “tomorrow's close = today's close.” The 2015 poster reached the same conclusion: roughly a coin flip.`;
    else verdict = `The simple “tomorrow = today” guess beat the SVR here. Daily price moves are mostly noise, and the model overfits to it.`;
    $("verdict").textContent = verdict;

    $("btTable").querySelector("tbody").innerHTML = res.backtest.slice().reverse().map((b) => {
      const err = b.predicted - b.actual;
      return `<tr><td>${fmtDate(b.date)}</td><td>${fmtMoney(b.prev, cur)}</td><td>${fmtMoney(b.predicted, cur)}</td><td>${fmtMoney(b.actual, cur)}</td>` +
        `<td>${err >= 0 ? "+" : "−"}${fmtMoney(Math.abs(err), cur)}</td><td class="${b.hitDirection ? "hit" : "miss"}">${b.hitDirection ? "✓ right" : "✗ wrong"}</td></tr>`;
    }).join("");
  }

  function renderIndicators(res, cur) {
    const L = res.latest, close = res.lastBar.close;
    const rsiNote = L.rsi >= 70 ? "Overbought (≥ 70)" : L.rsi <= 30 ? "Oversold (≤ 30)" : "Neutral (30–70)";
    const vs = (v) => `Price is ${close >= v ? "above" : "below"} (${fmtPct(close / v - 1)})`;
    const macdNote = L.macd >= L.macdSignal ? "Above signal line: bullish momentum" : "Below signal line: bearish momentum";
    $("indicators").innerHTML = `
      <div class="ind"><div class="l">RSI 14</div><div class="v">${L.rsi.toFixed(1)}</div>
        <div class="gauge"><i style="left:${Math.min(100, Math.max(0, L.rsi))}%"></i></div><div class="d">${rsiNote}</div></div>
      <div class="ind"><div class="l">MACD (12, 26)</div><div class="v">${L.macd.toFixed(2)}</div><div class="d">Signal ${L.macdSignal.toFixed(2)}. ${macdNote}</div></div>
      <div class="ind"><div class="l">SMA 20</div><div class="v">${fmtMoney(L.sma20, cur)}</div><div class="d">${vs(L.sma20)}</div></div>
      <div class="ind"><div class="l">EMA 12</div><div class="v">${fmtMoney(L.ema12, cur)}</div><div class="d">${vs(L.ema12)}</div></div>`;
  }

  // ---------------- autocomplete ----------------
  let active = -1;
  function hideSuggest() { $("suggest").hidden = true; active = -1; }
  function suggest() {
    const q = $("ticker").value.trim().toUpperCase();
    const list = $("suggest");
    if (!q || !state.tickers.length) return hideSuggest();
    const starts = [], name = [];
    for (const [t, n] of state.tickers) {
      if (t.startsWith(q)) starts.push([t, n]);
      else if (q.length >= 2 && n.toUpperCase().includes(q)) name.push([t, n]);
      if (starts.length >= 8) break;
    }
    starts.sort((a, b) => a[0].length - b[0].length);
    const items = starts.concat(name).slice(0, 8);
    if (!items.length) return hideSuggest();
    active = -1;
    list.innerHTML = items.map(([t, n]) => `<li role="option" data-t="${esc(t)}"><b>${esc(t)}</b><span>${esc(n)}</span></li>`).join("");
    list.hidden = false;
  }
  function pick(t) { $("ticker").value = t; hideSuggest(); predict(); }

  // ---------------- wiring ----------------
  function init() {
    $("chips").innerHTML = SAMPLES.map((t) => `<button type="button" data-t="${t}">${t}</button>`).join("");
    $("chips").addEventListener("click", (e) => { const t = e.target.dataset.t; if (t) pick(t); });

    $("window").addEventListener("click", (e) => {
      const v = e.target.dataset.v;
      if (!v) return;
      state.window = Number(v);
      [...$("window").children].forEach((b) => { b.classList.toggle("on", b === e.target); b.setAttribute("aria-checked", b === e.target); });
      predict();
    });
    ["useChange", "useVolume", "useTech"].forEach((id) => $(id).addEventListener("change", predict));

    $("controls").addEventListener("submit", (e) => { e.preventDefault(); predict(); });
    $("ticker").addEventListener("input", suggest);
    $("ticker").addEventListener("keydown", (e) => {
      const items = [...$("suggest").children];
      if ($("suggest").hidden || !items.length) return;
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        active = (active + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
        items.forEach((li, i) => li.classList.toggle("active", i === active));
      } else if (e.key === "Enter" && active >= 0) {
        e.preventDefault(); pick(items[active].dataset.t);
      } else if (e.key === "Escape") hideSuggest();
    });
    $("suggest").addEventListener("mousedown", (e) => { const li = e.target.closest("li"); if (li) { e.preventDefault(); pick(li.dataset.t); } });
    $("ticker").addEventListener("blur", () => setTimeout(hideSuggest, 100));

    fetch("data/tickers.json").then((r) => r.json()).then((t) => { state.tickers = t; }).catch(() => {});

    const params = new URLSearchParams(location.search);
    if (params.get("t")) $("ticker").value = params.get("t").toUpperCase();
    const w = Number(params.get("w"));
    if ([30, 60, 90, 180, 360].includes(w)) {
      state.window = w;
      [...$("window").children].forEach((b) => b.classList.toggle("on", Number(b.dataset.v) === w));
    }

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { if (state.chart) predict(); });
    predict();
  }

  init();
})();
