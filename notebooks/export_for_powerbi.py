import pandas as pd
import os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IND_PATH    = os.path.join(BASE_DIR, "indicators", "stock_indicators.csv")
OUT_PATH    = os.path.join(BASE_DIR, "indicators", "powerbi_final.csv")

def export():
    print("Loading indicators data...")
    df = pd.read_csv(IND_PATH, parse_dates=["Date"])

    # Round all decimal columns neatly for Power BI
    decimal_cols = ["Open", "High", "Low", "Close", "Daily_Return",
                    "Price_Range", "RSI", "MACD", "MACD_Signal",
                    "MACD_Hist", "MA20", "MA50", "MA200",
                    "BB_Upper", "BB_Mid", "BB_Lower"]

    for col in decimal_cols:
        if col in df.columns:
            df[col] = df[col].round(2)

    # Add a readable month-year column for Power BI time axis
    df["Month_Year"] = df["Date"].dt.strftime("%b %Y")  # e.g. "May 2025"

    # Add RSI zone labels (useful for Power BI slicers)
    df["RSI_Zone"] = pd.cut(
        df["RSI"],
        bins=[0, 30, 50, 70, 100],
        labels=["Oversold", "Neutral-Low", "Neutral-High", "Overbought"]
    )

    # Add return category
    df["Return_Category"] = pd.cut(
        df["Daily_Return"],
        bins=[-100, -2, -0.5, 0.5, 2, 100],
        labels=["Big Loss", "Small Loss", "Flat", "Small Gain", "Big Gain"]
    )

    df.to_csv(OUT_PATH, index=False)
    print(f"✅ Exported {len(df)} rows to: {OUT_PATH}")
    print(f"\nColumns for Power BI ({len(df.columns)} total):")
    print(df.columns.tolist())
    print(f"\nPreview:")
    print(df[["Date", "Company", "Sector", "Close",
              "RSI", "RSI_Zone", "Signal", "MA_Cross"]].head(8))

if __name__ == "__main__":
    export()