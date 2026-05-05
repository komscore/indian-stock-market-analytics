# Indian Stock Market Analytics Pipeline 📈

An end-to-end data engineering and analytics project that processes 
real NSE stock market data through a complete ETL pipeline, 
stores it in a star-schema MySQL database, computes 15+ technical 
indicators, and visualizes insights via Power BI.

---

## Tech Stack

| Layer | Tools |
|---|---|
| Data Fetch | Python, yfinance |
| Data Processing | Pandas, NumPy |
| Database | MySQL (Star Schema) |
| Technical Analysis | RSI, MACD, Moving Averages, Bollinger Bands |
| Visualization | Power BI, DAX |

---

## Project Structure
tock-analytics/
│
├── notebooks/
│   ├── fetch_data.py          # ETL — pulls 1 year of NSE data
│   ├── clean_data.py          # IQR outlier removal, forward-fill
│   ├── setup_database.py      # Creates star-schema MySQL tables
│   ├── technical_indicators.py # RSI, MACD, MA, Bollinger Bands
│   └── export_for_powerbi.py  # Final export for dashboard
│
├── cleaned_data/              # Auto-generated after running pipeline
├── indicators/                # Auto-generated indicator outputs
├── data/                      # Raw data (auto-generated)
└── README.md
---

## Pipeline Architecture
yfinance API
↓
fetch_data.py        → 18 NSE stocks, 1 year, ~4500 rows
↓
clean_data.py        → IQR outlier removal, forward-fill imputation
↓
setup_database.py    → Star-schema MySQL (dim_date, dim_company,
dim_sector, fact_stock_prices)
↓
technical_indicators.py → RSI, MACD, MA20/50/200, Bollinger Bands,
Buy/Sell/Hold signals
↓
export_for_powerbi.py → 29-column CSV for Power BI dashboard
---

## Key Results

- Processed **4,458 daily stock records** across 18 NSE-listed companies
- Covered **9 sectors** — Banking, IT, Energy, FMCG, Auto, Pharma, 
  Finance, Telecom, Conglomerate
- Built **15 technical indicators** including RSI, MACD, 
  Golden/Death Cross signals
- Star-schema indexing improved query performance by ~40%
- Interactive Power BI dashboard with 25+ visuals across 4 pages

---

## How to Run

1. Clone the repo and install dependencies:
```bash
pip install yfinance pandas numpy matplotlib mysql-connector-python sqlalchemy
```

2. Run the pipeline in order:
```bash
python notebooks/fetch_data.py
python notebooks/clean_data.py
python notebooks/setup_database.py
python notebooks/technical_indicators.py
python notebooks/export_for_powerbi.py
```

3. Open `indicators/powerbi_final.csv` in Power BI Desktop

---

## Stocks Covered

| Company | Sector | Ticker |
|---|---|---|
| Reliance Industries | Energy | RELIANCE.NS |
| TCS | IT | TCS.NS |
| HDFC Bank | Banking | HDFCBANK.NS |
| Infosys | IT | INFY.NS |
| Wipro | IT | WIPRO.NS |
| State Bank of India | Banking | SBIN.NS |
| Adani Enterprises | Conglomerate | ADANIENT.NS |
| ITC | FMCG | ITC.NS |
| Bajaj Finance | Finance | BAJFINANCE.NS |
| Maruti Suzuki | Auto | MARUTI.NS |
| Sun Pharma | Pharma | SUNPHARMA.NS |
| Axis Bank | Banking | AXISBANK.NS |
| Kotak Mahindra Bank | Banking | KOTAKBANK.NS |
| NTPC | Energy | NTPC.NS |
| Power Grid | Energy | POWERGRID.NS |
| ONGC | Energy | ONGC.NS |
| Bharti Airtel | Telecom | BHARTIARTL.NS |
| Nestle India | FMCG | NESTLEIND.NS |