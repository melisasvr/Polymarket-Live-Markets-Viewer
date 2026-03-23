# 🎯 Polymarket Live Markets Viewer
- A Python terminal tool + live website that fetches and displays real-time prediction market data from [Polymarket](https://polymarket.com) using their free public Gamma API, no API key required.

Prices reflect crowd-sourced probability estimates. A Yes price of `0.72` means the market currently prices a **72% chance** of Yes happening.

---

## 📸 Preview

### Terminal (Python)
```
════════════════════════════════════════════════════════════════
  🎯 Polymarket — Active Markets Viewer
  Fetched at: 2026-03-22 12:52:58
════════════════════════════════════════════════════════════════

Sort by:
  [1] Volume (highest first)
  [2] End date (soonest first)
  [3] Default (API order)

Enter choice (1, 2, or 3): 1

Sorted by: Volume ↓ — 20 markets
────────────────────────────────────────────────────────────────

#01  Netanyahu out by March 31?
  Resolves: Mar 31, 2026  (8d left)   Volume: $57.91M   24h Vol: $3.47M   Liquidity: $2.01M
  Outcomes: 2
  Yes          0.011    1.1%  ░░░░░░░░░░░░░░░░░░░░
  No           0.989   98.9%  ████████████████████
────────────────────────────────────────────────────────────────

#09  Will Bitcoin reach $150,000 in March?
  Resolves: Apr 01, 2026  (9d left)   Volume: $20.78M   24h Vol: $852.7K   Liquidity: $2.58M
  Outcomes: 2
  Yes          0.002    0.1%  ░░░░░░░░░░░░░░░░░░░░
  No           0.999   99.9%  ████████████████████
```

---

## ✨ Features

### Python Script (`polymarket_markets.py`)
- Fetches **20 live active markets** from Polymarket's Gamma API
- Filters out dead/resolved markets automatically
- Displays for each market:
  - Question text
  - Resolution date + days remaining (color-coded)
  - Total volume, 24h volume, liquidity
  - All outcome prices with ASCII probability bars
  - Handles binary **and** multi-outcome markets
- **Color-coded terminal output** (green/yellow/red by probability)
- **Sort** by volume, end date, or default
- **Export to CSV** with a timestamped filename
- Input validation — won't accept invalid sort choices
- No deprecated warnings, timezone-aware datetime handling

### Website (`index.html`)
- Same live data in a polished dark-themed UI
- Stats bar: total markets, combined volume, 24h volume, avg Yes probability, soonest close
- Animated probability bars per outcome
- Sort buttons (Default / Volume ↓ / End Date ↑)
- Days remaining badge per card (green/yellow/red urgency)
- CSV export directly from the browser
- Refresh button
- Zero dependencies — pure HTML, CSS, JavaScript
- Deployable to GitHub Pages in one step

---

## 🚀 Getting Started

### Python Script

**Requirements:** Python 3.8+ and the `requests` library.

```bash
pip install requests
```

**Run:**
```bash
python polymarket_markets.py
```

You'll be prompted to choose a sort order, then the markets display. At the end you can export to CSV.

### Website

Just open `index.html` in any modern browser — no server needed.

```bash
# Option 1: double-click index.html in your file explorer
# Option 2: open from terminal
open index.html        # macOS
start index.html       # Windows
xdg-open index.html    # Linux
```

To deploy on **GitHub Pages**:
1. Push the repo to GitHub
2. Go to **Settings → Pages → Source: main branch**
3. Your live URL: `https://yourusername.github.io/your-repo-name`

---

## 📁 Project Structure

```
polymarket-live/
├── polymarket_markets.py   # Python terminal viewer
├── index.html              # Browser-based live dashboard
├── README.md               # This file
└── data/                   # CSV exports saved here
    └── polymarket_markets_YYYYMMDD_HHMMSS.csv
```

> **Note:** The `data/` folder is created automatically when you export from the Python script. To keep exports organised, move the generated CSV files into this folder manually, or update the script's export path to `data/polymarket_markets_....csv`.

---

## 🔌 API

Data is sourced from Polymarket's free public **Gamma API** — no authentication or API key required.

```
GET https://gamma-api.polymarket.com/markets
    ?closed=false
    &active=true
    &order=volume24hr
    &ascending=false
    &liquidity_num_min=100
    &limit=50
```

Key fields used:

| Field | Description |
|---|---|
| `question` | The market question |
| `outcomePrices` | JSON string of outcome prices (e.g. `["0.65","0.35"]`) |
| `outcomes` | JSON string of outcome labels (e.g. `["Yes","No"]`) |
| `volume` | Total all-time trading volume in USD |
| `volume24hr` | Trading volume in the last 24 hours |
| `liquidity` | Current liquidity in USD |
| `endDate` | ISO 8601 resolution date |

---

## 🛠 Built With

- **Python 3** — `requests`, `json`, `csv`, `datetime` (all stdlib except requests)
- **HTML / CSS / JavaScript** — zero frameworks, zero dependencies
- **Polymarket Gamma API** — free, public, no key needed
- **corsproxy.io** — CORS proxy for browser-side API calls

---

## 🤝 Contributing

Contributions are welcome! Here's how to get involved:

1. **Fork** the repository
2. **Create a branch** for your feature
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** and commit them
   ```bash
   git commit -m "Add: your feature description"
   ```
4. **Push** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** — describe what you changed and why

### Ideas for contributions
- Add more sort options (e.g. by liquidity or days remaining)
- Add a keyword search/filter to the Python script
- Add category tags (crypto / politics / sports) auto-detected from the question text
- Improve the website with auto-refresh every N seconds
- Add dark/light theme toggle to the website

Please keep code clean and consistent with the existing style. If you find a bug, feel free to open an issue too.

---

## 📄 License

```
MIT License

Copyright (c) 2026 Melisa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including, without limitation, the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
