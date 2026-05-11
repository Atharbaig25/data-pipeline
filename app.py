import random
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import requests
from datetime import datetime

# ── Page config ────────────────────────────────────────
st.set_page_config(
    page_title="Crypto Live Dashboard",
    page_icon="📈",
    layout="wide"
)

# ── Functions ──────────────────────────────────────────
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

def save_to_db(df):
    conn = sqlite3.connect('data/crypto.db')
    df.to_sql('prices', conn, if_exists='append', index=False)
    conn.close()

def load_from_db():
    conn = sqlite3.connect('data/crypto.db')
    try:
        df = pd.read_sql('SELECT * FROM prices', conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df

# ── Header ─────────────────────────────────────────────
st.title("Live Crypto Price Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ── Fetch and save latest data ─────────────────────────
df_live = fetch_crypto_data()
save_to_db(df_live)

# ── Metric cards ───────────────────────────────────────
st.subheader("Live Prices")
cols = st.columns(5)

for i, row in df_live.iterrows():
    change = row['change_24h']
    delta  = f"{change:.2f}%"
    cols[i].metric(
        label=row['coin'].upper(),
        value=f"${row['price_usd']:,.2f}",
        delta=delta
    )

st.divider()

# ── Price bar chart ────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Current Prices (USD)")
    fig1 = px.bar(
        df_live,
        x='coin',
        y='price_usd',
        color='coin',
        title='Price Comparison',
        text='price_usd'
    )
    fig1.update_traces(
        texttemplate='$%{text:,.0f}',
        textposition='outside'
    )
    fig1.update_layout(showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("24h Price Change (%)")
    colors = ['green' if x > 0 else 'red' 
              for x in df_live['change_24h']]
    fig2 = px.bar(
        df_live,
        x='coin',
        y='change_24h',
        color='change_24h',
        color_continuous_scale='RdYlGn',
        title='24h Change %'
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ── Historical data from DB ────────────────────────────
st.subheader("Historical Price Trends")
df_history = load_from_db()

if len(df_history) > 5:
    fig3 = px.line(
        df_history,
        x='timestamp',
        y='price_usd',
        color='coin',
        title='Price History Over Time',
        markers=True
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Run the dashboard a few times to see historical trends!")

st.divider()

# ── Market cap table ───────────────────────────────────
st.subheader("Market Cap Overview")
df_display = df_live[['coin','price_usd',
                       'change_24h','market_cap']].copy()
df_display['market_cap'] = df_display['market_cap'].apply(
    lambda x: f"${x/1e9:.2f}B")
df_display['price_usd']  = df_display['price_usd'].apply(
    lambda x: f"${x:,.2f}")
df_display['change_24h'] = df_display['change_24h'].apply(
    lambda x: f"{x:.2f}%")
df_display.columns = ['Coin','Price','24h Change','Market Cap']
st.dataframe(df_display, use_container_width=True)

# ── Auto refresh ───────────────────────────────────────
st.divider()
if st.button("Refresh Data"):
    st.rerun()

st.caption("Click Refresh Data to fetch latest prices")