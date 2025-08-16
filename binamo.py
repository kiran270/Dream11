import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator

# Define crypto symbols
symbols = ['BTC-USD', 'ETH-USD', 'LTC-USD']

# Time window
end_time = datetime.now()
start_time = end_time - timedelta(days=1)

results = []

for symbol in symbols:
    df = yf.download(symbol, start=start_time, end=end_time, interval='15m', progress=False)

    if df.empty or 'Close' not in df.columns:
        print(f"❌ No data for {symbol}")
        continue

    df.reset_index(inplace=True)
    close_series = df['Close'].astype(float)

    # ✅ Calculate EMA and RSI
    df['EMA20'] = close_series.ewm(span=20, adjust=False).mean()

    latest = df.iloc[-1]
    price = latest['Close']
    ema = latest['EMA20']

    results.append({
        'Crypto': symbol,
        'Price': round(price, 2),
        'EMA20': round(ema, 2),
        'Trend': trend
    })

# Show results
df_results = pd.DataFrame(results)
print(df_results)
