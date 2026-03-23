# ============================================================
#  Polymarket Active Markets Viewer
#  Fetches live prediction market data from the Gamma API.
#
#  Prices reflect crowd-sourced probability estimates:
#    e.g. Yes price of 0.72 → market prices a 72% chance of Yes
#
#  Features:
#    - Fetches top 20 active markets
#    - Displays Yes/No prices + implied probabilities
#    - Handles binary AND multi-outcome markets
#    - Shows volume, liquidity, and resolution date
#    - Color-coded terminal output
#    - Sort by volume or end date
#    - Export results to CSV
# ============================================================

import requests
import json
import csv
from datetime import datetime, timezone

# ── API ──────────────────────────────────────────────────────
# Fetch extra markets upfront to ensure 20 remain after filtering out expired ones
# Use closed=false + order by 24hr volume — the correct way to get live markets
# active=true alone returns legacy/unclosed old markets
API_URL = "https://gamma-api.polymarket.com/markets?closed=false&active=true&order=volume24hr&ascending=false&liquidity_num_min=100&limit=50"

# ── ANSI colors ──────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    MAGENTA = "\033[95m"
    GREY    = "\033[90m"
    WHITE   = "\033[97m"

SEP  = C.GREY + "─" * 64 + C.RESET
SEP2 = C.CYAN + "═" * 64 + C.RESET


# ── Helpers ──────────────────────────────────────────────────

def parse_prices(raw):
    """Return list of floats from the outcomePrices JSON string."""
    return [float(p) for p in json.loads(raw)]


def parse_outcomes(raw):
    """Return list of outcome label strings from the outcomes JSON string."""
    return json.loads(raw)


def fmt_volume(val):
    """Format dollar volume with K/M suffix."""
    try:
        v = float(val)
        if v >= 1_000_000:
            return f"${v / 1_000_000:.2f}M"
        if v >= 1_000:
            return f"${v / 1_000:.1f}K"
        return f"${v:.0f}"
    except (TypeError, ValueError):
        return "N/A"


def fmt_date(raw):
    """Parse ISO date string and return a readable format."""
    if not raw:
        return "N/A"
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%b %d, %Y")
        except ValueError:
            continue
    return raw[:10]


def days_remaining(raw):
    """Return number of days until resolution, or None."""
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
        try:
            end = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            return (end - now).days
        except ValueError:
            continue
    return None


def price_bar(prob, width=20):
    """Render a simple ASCII probability bar."""
    filled = round(prob * width)
    return "█" * filled + "░" * (width - filled)


def sort_markets(markets, sort_by):
    """Sort market list by 'volume' or 'endDate'."""
    if sort_by == "volume":
        def key(m):
            try:
                return float(m.get("volume", 0) or 0)
            except ValueError:
                return 0
        return sorted(markets, key=key, reverse=True)
    elif sort_by == "endDate":
        def key(m):
            raw = m.get("endDate") or ""
            for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
                try:
                    return datetime.strptime(raw, fmt)
                except ValueError:
                    continue
            return datetime.max
        return sorted(markets, key=key)
    return markets


# ── Display ──────────────────────────────────────────────────

def display_market(idx, market):
    question  = market.get("question", "No question text available")
    volume    = fmt_volume(market.get("volume"))
    volume24h = fmt_volume(market.get("volume24hr"))
    liquidity = fmt_volume(market.get("liquidity"))
    end_date  = fmt_date(market.get("endDate"))
    days_left = days_remaining(market.get("endDate"))
    raw_prices = market.get("outcomePrices")
    raw_labels = market.get("outcomes")

    # Header
    print(f"\n{C.BOLD}{C.WHITE}#{idx:02d}  {question}{C.RESET}")

    # Meta row
    days_str = ""
    if days_left is not None:
        color = C.GREEN if days_left > 30 else (C.YELLOW if days_left > 7 else C.RED)
        days_str = f"  {color}({days_left}d left){C.RESET}"

    print(
        f"  {C.GREY}Resolves:{C.RESET} {C.CYAN}{end_date}{C.RESET}{days_str}   "
        f"{C.GREY}Volume:{C.RESET} {C.MAGENTA}{volume}{C.RESET}   "
        f"{C.GREY}24h Vol:{C.RESET} {C.MAGENTA}{volume24h}{C.RESET}   "
        f"{C.GREY}Liquidity:{C.RESET} {C.MAGENTA}{liquidity}{C.RESET}"
    )

    # Prices
    if not raw_prices:
        print(f"  {C.YELLOW}Prices unavailable{C.RESET}")
        return

    try:
        prices = parse_prices(raw_prices)
        labels = parse_outcomes(raw_labels) if raw_labels else [f"Outcome {i+1}" for i in range(len(prices))]

        print(f"  {C.GREY}Outcomes: {len(prices)}{C.RESET}")

        for label, price in zip(labels, prices):
            pct = price * 100
            pct_color = C.GREEN if pct >= 70 else (C.YELLOW if pct >= 40 else C.RED)
            bar = price_bar(price)
            print(
                f"  {C.BOLD}{label:<12}{C.RESET} "
                f"{C.WHITE}{price:.3f}{C.RESET}  "
                f"{pct_color}{pct:5.1f}%{C.RESET}  "
                f"{C.GREY}{bar}{C.RESET}"
            )

    except (json.JSONDecodeError, ValueError, IndexError):
        print(f"  {C.YELLOW}Prices unavailable (parse error){C.RESET}")


# ── CSV Export ───────────────────────────────────────────────

def export_csv(markets, filename):
    """Write market data to a CSV file."""
    rows = []
    for m in markets:
        prices, labels = [], []
        try:
            if m.get("outcomePrices"):
                prices = parse_prices(m["outcomePrices"])
            if m.get("outcomes"):
                labels = parse_outcomes(m["outcomes"])
            else:
                labels = [f"Outcome {i+1}" for i in range(len(prices))]
        except (json.JSONDecodeError, ValueError):
            pass

        row = {
            "question":     m.get("question", ""),
            "end_date":     fmt_date(m.get("endDate")),
            "volume":       m.get("volume", ""),
            "liquidity":    m.get("liquidity", ""),
            "num_outcomes": len(prices),
        }
        for label, price in zip(labels, prices):
            safe = label.replace(" ", "_").lower()
            row[f"price_{safe}"] = f"{price:.4f}"
            row[f"prob_{safe}"]  = f"{price * 100:.1f}%"

        rows.append(row)

    if not rows:
        print(f"{C.YELLOW}No data to export.{C.RESET}")
        return

    fieldnames = list(dict.fromkeys(k for row in rows for k in row))

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"\n{C.GREEN}✔ Exported {len(rows)} markets → {C.BOLD}{filename}{C.RESET}")


# ── Main ─────────────────────────────────────────────────────

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(SEP2)
    print(f"{C.BOLD}{C.CYAN}  🎯 Polymarket — Active Markets Viewer{C.RESET}")
    print(f"{C.GREY}  Fetched at: {now}{C.RESET}")
    print(SEP2)

    # Fetch
    try:
        response = requests.get(API_URL, timeout=10)
    except requests.exceptions.ConnectionError as e:
        print(f"{C.RED}Error: Could not connect to Polymarket API.\n  {e}{C.RESET}")
        return
    except requests.exceptions.Timeout:
        print(f"{C.RED}Error: Request timed out.{C.RESET}")
        return

    if response.status_code != 200:
        print(f"{C.RED}Error: API returned status {response.status_code}{C.RESET}")
        return

    markets = response.json()
    if not markets:
        print(f"{C.YELLOW}No active markets returned.{C.RESET}")
        return

    # ── Filter safety net (API should handle most of this now) ──
    now_utc = datetime.now(timezone.utc)

    def is_live(m):
        # Drop markets whose endDate is in the past
        raw = m.get("endDate")
        if raw:
            for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
                try:
                    end = datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc)
                    if end <= now_utc:
                        return False
                    break
                except ValueError:
                    continue

        # Drop markets where every price is 0.0 (fully resolved)
        try:
            prices = [float(p) for p in json.loads(m.get("outcomePrices") or "[]")]
            if prices and all(p == 0.0 for p in prices):
                return False
        except (json.JSONDecodeError, ValueError):
            pass

        return True

    markets = [m for m in markets if is_live(m)][:20]

    if not markets:
        print(f"{C.YELLOW}No live active markets found.{C.RESET}")
        return

    # Sort prompt
    print(f"\n{C.BOLD}Sort by:{C.RESET}")
    print(f"  {C.CYAN}[1]{C.RESET} Volume (highest first)")
    print(f"  {C.CYAN}[2]{C.RESET} End date (soonest first)")
    print(f"  {C.CYAN}[3]{C.RESET} Default (API order)")

    choice = ""
    while choice not in ("1", "2", "3"):
        try:
            choice = input(f"\n{C.BOLD}Enter choice (1, 2, or 3): {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            choice = "3"
            break
        if choice not in ("1", "2", "3"):
            print(f"  {C.YELLOW}Please enter 1, 2, or 3.{C.RESET}")

    sort_map   = {"1": "volume", "2": "endDate", "3": "none"}
    sort_by    = sort_map.get(choice, "none")
    markets    = sort_markets(markets, sort_by)
    sort_label = {"volume": "Volume ↓", "endDate": "End Date ↑", "none": "Default"}.get(sort_by, "Default")

    print(f"\n{C.GREY}Sorted by: {sort_label} — {len(markets)} markets{C.RESET}")

    # Display
    for i, market in enumerate(markets):
        print(SEP)
        display_market(i + 1, market)

    print(f"\n{SEP2}")
    print(f"{C.BOLD}{C.WHITE}  {len(markets)} active market(s) displayed.{C.RESET}")
    print(SEP2)

    # Export prompt
    try:
        export = input(f"\n{C.BOLD}Export to CSV? (y/n): {C.RESET}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        export = "n"

    if export == "y":
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_csv(markets, f"polymarket_markets_{timestamp}.csv")


if __name__ == "__main__":
    main()