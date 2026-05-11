import pandas as pd
import sqlite3
import random
from datetime import datetime

# ── Generate realistic crypto data ────────────────────
def fetch_crypto_data():
    base_prices = {
        'bitcoin':     81000,
        'ethereum':    2300,
        'binancecoin': 650,
        'solana':      95,
        'cardano':     0.28
    }
    
    rows = []
    for coin, base in base_prices.items():
        # Add small random movement ±3%
        change    = random.uniform(-3, 3)
        price     = base * (1 + change/100)
        market_cap = price * random.uniform(1e7, 1e10)
        
        rows.append({
            'coin':       coin,
            'price_usd':  round(price, 2),
            'change_24h': round(change, 2),
            'market_cap': round(market_cap, 2),
            'timestamp':  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return pd.DataFrame(rows)

# ── Save to SQLite database ────────────────────────────
def save_to_db(df):
    conn = sqlite3.connect('data/crypto.db')
    df.to_sql('prices', conn,
              if_exists='append',
              index=False)
    conn.close()

# ── Load all data from database ────────────────────────
def load_from_db():
    conn = sqlite3.connect('data/crypto.db')
    try:
        df = pd.read_sql('SELECT * FROM prices', conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# ── Price alert function ───────────────────────────────
def check_alerts(df):
    alerts = []
    for _, row in df.iterrows():
        if row['change_24h'] > 2:
            alerts.append(
                f"ALERT: {row['coin'].upper()} up {row['change_24h']:.1f}% in 24h!"
            )
        elif row['change_24h'] < -2:
            alerts.append(
                f"ALERT: {row['coin'].upper()} down {row['change_24h']:.1f}% in 24h!"
            )
    return alerts

# ── Main ───────────────────────────────────────────────
if __name__ == '__main__':
    print("Fetching crypto data...")
    df = fetch_crypto_data()
    print("\nLive prices:")
    print(df)

    print("\nSaving to database...")
    save_to_db(df)
    print("✓ Saved!")

    print("\nLoading from database...")
    df_loaded = load_from_db()
    print(f"✓ Total records in DB: {len(df_loaded)}")

    alerts = check_alerts(df)
    if alerts:
        print("\nPrice Alerts:")
        for alert in alerts:
            print(alert)
    else:
        print("\nNo major price movements detected.")

    print("\n✓ Pipeline working!")