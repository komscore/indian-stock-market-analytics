import mysql.connector
import pandas as pd
import os

# --- Config ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Stock@123",        # leave blank if no password was set
    "database": "stock_analytics"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "cleaned_data", "cleaned_stocks.csv")

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    print("Creating tables...")

    # --- Dimension table: sectors ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_sector (
            sector_id   INT AUTO_INCREMENT PRIMARY KEY,
            sector_name VARCHAR(50) NOT NULL UNIQUE
        )
    """)

    # --- Dimension table: companies ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_company (
            company_id   INT AUTO_INCREMENT PRIMARY KEY,
            ticker       VARCHAR(20) NOT NULL UNIQUE,
            company_name VARCHAR(100) NOT NULL,
            sector_id    INT,
            FOREIGN KEY (sector_id) REFERENCES dim_sector(sector_id)
        )
    """)

    # --- Dimension table: dates ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dim_date (
            date_id    INT AUTO_INCREMENT PRIMARY KEY,
            full_date  DATE NOT NULL UNIQUE,
            year       INT,
            month      INT,
            month_name VARCHAR(10),
            quarter    INT,
            day_of_week VARCHAR(10)
        )
    """)

    # --- Fact table: daily stock prices ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fact_stock_prices (
            price_id     INT AUTO_INCREMENT PRIMARY KEY,
            date_id      INT,
            company_id   INT,
            open_price   DECIMAL(10,2),
            high_price   DECIMAL(10,2),
            low_price    DECIMAL(10,2),
            close_price  DECIMAL(10,2),
            volume       BIGINT,
            daily_return DECIMAL(8,4),
            price_range  DECIMAL(10,2),
            FOREIGN KEY (date_id)    REFERENCES dim_date(date_id),
            FOREIGN KEY (company_id) REFERENCES dim_company(company_id),
            INDEX idx_date    (date_id),
            INDEX idx_company (company_id)
        )
    """)

    conn.commit()
    print("✅ All tables created!")
    cursor.close()
    conn.close()

def load_data():
    print("\nLoading cleaned data...")
    df = pd.read_csv(CLEAN_PATH)
    df["Date"] = pd.to_datetime(df["Date"])

    conn = get_connection()
    cursor = conn.cursor()

    # --- Insert sectors ---
    print("Inserting sectors...")
    sectors = df["Sector"].unique()
    for sector in sectors:
        cursor.execute("""
            INSERT IGNORE INTO dim_sector (sector_name)
            VALUES (%s)
        """, (sector,))

    # --- Insert companies ---
    print("Inserting companies...")
    companies = df[["Ticker", "Company", "Sector"]].drop_duplicates()
    for _, row in companies.iterrows():
        cursor.execute(
            "SELECT sector_id FROM dim_sector WHERE sector_name = %s",
            (row["Sector"],)
        )
        sector_id = cursor.fetchone()[0]
        cursor.execute("""
            INSERT IGNORE INTO dim_company (ticker, company_name, sector_id)
            VALUES (%s, %s, %s)
        """, (row["Ticker"], row["Company"], sector_id))

    # --- Insert dates ---
    print("Inserting dates...")
    dates = df["Date"].drop_duplicates()
    for date in dates:
        cursor.execute("""
            INSERT IGNORE INTO dim_date
                (full_date, year, month, month_name, quarter, day_of_week)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            date.date(),
            date.year,
            date.month,
            date.strftime("%b"),
            (date.month - 1) // 3 + 1,
            date.strftime("%A")
        ))

    # --- Insert fact rows ---
    print("Inserting stock prices (this may take a moment)...")
    inserted = 0
    for _, row in df.iterrows():
        cursor.execute(
            "SELECT date_id FROM dim_date WHERE full_date = %s",
            (row["Date"].date(),)
        )
        date_id = cursor.fetchone()[0]

        cursor.execute(
            "SELECT company_id FROM dim_company WHERE ticker = %s",
            (row["Ticker"],)
        )
        company_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO fact_stock_prices
                (date_id, company_id, open_price, high_price, low_price,
                 close_price, volume, daily_return, price_range)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            date_id, company_id,
            round(float(row["Open"]),  2),
            round(float(row["High"]),  2),
            round(float(row["Low"]),   2),
            round(float(row["Close"]), 2),
            int(row["Volume"]),
            round(float(row["Daily_Return"]) if pd.notna(row["Daily_Return"]) else 0, 4),
            round(float(row["Price_Range"]), 2)
        ))
        inserted += 1

    conn.commit()
    print(f"✅ Inserted {inserted} rows into fact_stock_prices")
    cursor.close()
    conn.close()

def verify():
    print("\nVerifying data...")
    conn = get_connection()
    cursor = conn.cursor()

    queries = {
        "Sectors"  : "SELECT COUNT(*) FROM dim_sector",
        "Companies": "SELECT COUNT(*) FROM dim_company",
        "Dates"    : "SELECT COUNT(*) FROM dim_date",
        "Price rows": "SELECT COUNT(*) FROM fact_stock_prices"
    }

    for label, query in queries.items():
        cursor.execute(query)
        print(f"  {label}: {cursor.fetchone()[0]}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_tables()
    load_data()
    verify()
    print("\n✅ Phase 3 Complete — Database is ready!")