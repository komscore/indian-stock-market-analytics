import yfinance as yf
import pandas as pd
import os

# --- Config ---
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "WIPRO.NS",
    "SBIN.NS", "ADANIENT.NS", "ITC.NS", "BAJFINANCE.NS", "TATAMOTORS.NS",
    "MARUTI.NS", "SUNPHARMA.NS", "LTIM.NS", "AXISBANK.NS", "KOTAKBANK.NS",
    "NTPC.NS", "POWERGRID.NS", "ONGC.NS", "BHARTIARTL.NS", "NESTLEIND.NS"
]

# Sector mapping — which company belongs to which sector
SECTOR_MAP = {
    "RELIANCE":   "Energy",
    "TCS":        "IT",
    "HDFCBANK":   "Banking",
    "INFY":       "IT",
    "WIPRO":      "IT",
    "SBIN":       "Banking",
    "ADANIENT":   "Conglomerate",
    "ITC":        "FMCG",
    "BAJFINANCE": "Finance",
    "TATAMOTORS": "Auto",
    "MARUTI":     "Auto",
    "SUNPHARMA":  "Pharma",
    "LTIM":       "IT",
    "AXISBANK":   "Banking",
    "KOTAKBANK":  "Banking",
    "NTPC":       "Energy",
    "POWERGRID":  "Energy",
    "ONGC":       "Energy",
    "BHARTIARTL": "Telecom",
    "NESTLEIND":  "FMCG"
}

def fetch_stock_data():
    os.makedirs("data", exist_ok=True)  # create folder if it doesn't exist
    all_data = []

    for ticker in TICKERS:
        company = ticker.replace(".NS", "")
        print(f"Downloading {company}...")

        try:
            df = yf.download(ticker, period="1y", interval="1d",
                             auto_adjust=True, progress=False)

            if df.empty:
                print(f"  WARNING: No data for {ticker}, skipping.")
                continue

            # Flatten multi-level columns if present (yfinance sometimes does this)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df["Ticker"] = ticker
            df["Company"] = company
            df["Sector"] = SECTOR_MAP.get(company, "Unknown")
            all_data.append(df)
            print(f"  Got {len(df)} rows")

        except Exception as e:
            print(f"  ERROR downloading {ticker}: {e}")

    # Combine everything into one table
    combined = pd.concat(all_data)
    combined.reset_index(inplace=True)
    combined.rename(columns={"index": "Date"}, inplace=True)

    # Save
    output_path = "data/raw_stocks.csv"
    combined.to_csv(output_path, index=False)

    print(f"\n✅ Done! Total rows: {len(combined)}")
    print(f"✅ Saved to: {output_path}")
    print(f"\nPreview:")
    print(combined[["Date", "Company", "Sector", "Open", "Close", "Volume"]].head(10))

    return combined

# --- Run it ---
if __name__ == "__main__":
    df = fetch_stock_data()