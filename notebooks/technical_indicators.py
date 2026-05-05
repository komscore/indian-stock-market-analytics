import pandas as pd
import numpy as np
import os

# --- Paths ---
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "cleaned_data", "cleaned_stocks.csv")
OUT_PATH   = os.path.join(BASE_DIR, "indicators", "stock_indicators.csv")
os.makedirs(os.path.join(BASE_DIR, "indicators"), exist_ok=True)

# ── 1. RSI ──────────────────────────────────────────────────────────────────
def compute_rsi(series, period=14):
    """
    RSI tells us if a stock is overbought or oversold.
    period=14 means we look at the last 14 days.
    """
    delta = series.diff()                        # daily price change
    gain  = delta.clip(lower=0)                  # only positive changes
    loss  = -delta.clip(upper=0)                 # only negative changes (made positive)

    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()

    rs  = avg_gain / avg_loss                    # ratio of gains to losses
    rsi = 100 - (100 / (1 + rs))                # scale to 0-100
    return rsi

# ── 2. MACD ─────────────────────────────────────────────────────────────────
def compute_macd(series, fast=12, slow=26, signal=9):
    """
    MACD detects momentum shifts.
    fast=12  → 12-day moving average
    slow=26  → 26-day moving average
    MACD line = fast EMA - slow EMA
    Signal    = 9-day EMA of MACD line
    Histogram = MACD - Signal (shows strength of momentum)
    """
    ema_fast    = series.ewm(span=fast,   adjust=False).mean()
    ema_slow    = series.ewm(span=slow,   adjust=False).mean()
    macd_line   = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram   = macd_line - signal_line
    return macd_line, signal_line, histogram

# ── 3. Moving Averages ───────────────────────────────────────────────────────
def compute_moving_averages(series):
    """
    MA20  = average of last 20 days  (short-term trend)
    MA50  = average of last 50 days  (medium-term trend)
    MA200 = average of last 200 days (long-term trend)
    """
    ma20  = series.rolling(window=20).mean()
    ma50  = series.rolling(window=50).mean()
    ma200 = series.rolling(window=200).mean()
    return ma20, ma50, ma200

# ── 4. Bollinger Bands ───────────────────────────────────────────────────────
def compute_bollinger_bands(series, window=20):
    """
    Bollinger Bands show volatility.
    Middle band = MA20
    Upper band  = MA20 + 2 standard deviations
    Lower band  = MA20 - 2 standard deviations
    Price touching upper band = overbought
    Price touching lower band = oversold
    """
    ma20       = series.rolling(window=window).mean()
    std        = series.rolling(window=window).std()
    upper_band = ma20 + (2 * std)
    lower_band = ma20 - (2 * std)
    return upper_band, ma20, lower_band

# ── 5. Trading Signals ───────────────────────────────────────────────────────
def compute_signals(df):
    """
    Generate simple buy/sell/hold signals based on RSI and MACD.
    This is what traders actually use to make decisions.
    """
    conditions = [
        (df["RSI"] < 30) & (df["MACD"] > df["MACD_Signal"]),  # oversold + momentum up
        (df["RSI"] > 70) & (df["MACD"] < df["MACD_Signal"]),  # overbought + momentum down
    ]
    signals = ["BUY", "SELL"]
    df["Signal"] = np.select(conditions, signals, default="HOLD")
    return df

# ── Main ─────────────────────────────────────────────────────────────────────
def compute_all_indicators():
    print("Loading cleaned data...")
    df = pd.read_csv(CLEAN_PATH, parse_dates=["Date"])
    df.sort_values(["Ticker", "Date"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    results = []

    tickers = df["Ticker"].unique()
    print(f"Computing indicators for {len(tickers)} stocks...\n")

    for ticker in tickers:
        stock = df[df["Ticker"] == ticker].copy()
        close = stock["Close"]

        # RSI
        stock["RSI"] = compute_rsi(close)

        # MACD
        stock["MACD"], stock["MACD_Signal"], stock["MACD_Hist"] = compute_macd(close)

        # Moving averages
        stock["MA20"], stock["MA50"], stock["MA200"] = compute_moving_averages(close)

        # Bollinger Bands
        stock["BB_Upper"], stock["BB_Mid"], stock["BB_Lower"] = compute_bollinger_bands(close)

        # Signals
        stock = compute_signals(stock)

        # MA crossover signal (Golden Cross / Death Cross)
        # Golden Cross = MA20 crosses above MA50 → bullish
        # Death Cross  = MA20 crosses below MA50 → bearish
        stock["MA_Cross"] = np.where(
            stock["MA20"] > stock["MA50"], "Golden", "Death"
        )

        results.append(stock)
        print(f"  ✅ {ticker.replace('.NS','')} — RSI: {stock['RSI'].iloc[-1]:.1f} | "
              f"Signal: {stock['Signal'].iloc[-1]} | "
              f"MA Cross: {stock['MA_Cross'].iloc[-1]}")

    final = pd.concat(results).reset_index(drop=True)

    # Summary
    print(f"\n{'─'*45}")
    print(f"Total rows with indicators: {len(final)}")
    print(f"\nSignal breakdown:")
    print(final['Signal'].value_counts().to_string())
    print(f"\nMA Cross breakdown:")
    print(final['MA_Cross'].value_counts().to_string())

    final.to_csv(OUT_PATH, index=False)
    print(f"\n✅ Saved to: {OUT_PATH}")
    return final

if __name__ == "__main__":
    df = compute_all_indicators()