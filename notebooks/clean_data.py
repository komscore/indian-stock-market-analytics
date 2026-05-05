import pandas as pd
import numpy as np
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw_stocks.csv")
CLEAN_PATH = os.path.join(BASE_DIR, "cleaned_data", "cleaned_stocks.csv")
os.makedirs(os.path.join(BASE_DIR, "cleaned_data"), exist_ok=True)

def clean_data():
    print("Loading raw data...")
    df = pd.read_csv(RAW_PATH)
    print(f"Raw shape: {df.shape}")  # shape = (rows, columns)

    # ADD THE TWO NEW LINES RIGHT HERE ↓
    print("Columns found:", df.columns.tolist())
    df.columns = df.columns.str.strip()

    # ------------------------------------------------
    # Step 1 — Fix data types
    # ------------------------------------------------
    # Step 1 — Fix data types
    # ------------------------------------------------
    print("\n Step 1: Fixing data types...")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # text → proper date
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")     # text → numbers

    print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")

    # ------------------------------------------------
    # Step 2 — Remove duplicates
    # ------------------------------------------------
    print("\n Step 2: Removing duplicates...")
    before = len(df)
    df.drop_duplicates(subset=["Date", "Ticker"], inplace=True)
    after = len(df)
    print(f"  Removed {before - after} duplicate rows")

    # ------------------------------------------------
    # Step 3 — Forward-fill missing values (per stock)
    # ------------------------------------------------
    print("\n Step 3: Filling missing values...")
    df.sort_values(["Ticker", "Date"], inplace=True)

    missing_before = df[["Open", "High", "Low", "Close", "Volume"]].isnull().sum().sum()

    # Forward fill within each stock separately
    df[["Open", "High", "Low", "Close", "Volume"]] = (
        df.groupby("Ticker")[["Open", "High", "Low", "Close", "Volume"]]
        .transform(lambda x: x.ffill())
    )

    missing_after = df[["Open", "High", "Low", "Close", "Volume"]].isnull().sum().sum()
    print(f"  Missing values: {missing_before} → {missing_after}")

    # ------------------------------------------------
    # Step 4 — IQR outlier removal (per stock, on Close price)
    # ------------------------------------------------
    print("\n Step 4: Removing outliers using IQR...")

    before = len(df)

    def remove_outliers_iqr(group):
        Q1 = group["Close"].quantile(0.25)
        Q3 = group["Close"].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 3 * IQR
        upper = Q3 + 3 * IQR
        return group[(group["Close"] >= lower) & (group["Close"] <= upper)]

    cleaned_groups = []
    for ticker, group in df.groupby("Ticker"):
        cleaned_groups.append(remove_outliers_iqr(group))

    df = pd.concat(cleaned_groups).reset_index(drop=True)
    after = len(df)
    print(f"  Removed {before - after} outlier rows")

    # ------------------------------------------------
    # Step 5 — Add helper columns
    # ------------------------------------------------
    print("\n Step 5: Adding helper columns...")
    df["Daily_Return"] = df.groupby("Ticker")["Close"].pct_change() * 100
    # pct_change = how much % did the price change from yesterday?
    # e.g. Close went from 100 → 105, Daily_Return = 5%

    df["Price_Range"] = df["High"] - df["Low"]
    # How much did the price swing within that day?

    df["Year"]  = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")  # Jan, Feb, Mar...

    # ------------------------------------------------
    # Final summary
    # ------------------------------------------------
    print(f"\n Cleaned shape: {df.shape}")
    print(f" Stocks: {df['Ticker'].nunique()}")
    print(f" Sectors: {df['Sector'].unique()}")
    print(f"\nPreview:")
    print(df[["Date", "Company", "Sector", "Close",
              "Daily_Return", "Price_Range"]].head(10))

    df.to_csv(CLEAN_PATH, index=False)
    print(f"\n✅ Cleaned data saved to: {CLEAN_PATH}")
    return df

if __name__ == "__main__":
    df = clean_data()