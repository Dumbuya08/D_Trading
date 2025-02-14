import ccxt
import pandas as pd
import time

# ✅ Binance API Keys
API_KEY = "Fhs4lGae2qAi6VNjbJjebUAwXrIChb7mlf372UOICMwdKaNdNBGKtfdeUff2TTTT"
API_SECRET = "54fv3bj65ethr7erf2e6ygheytre"

# ✅ Connect to Binance Exchange
exchange = ccxt.binance({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "options": {"defaultType": "spot"},
})

# ✅ Trading Parameters
SYMBOL = "BTC/USDT"
TIMEFRAME = "5m"
LOT_SIZE = 0.001
STOP_LOSS_PERCENT = 0.98
TAKE_PROFIT_PERCENT = 1.05
FAST_MA = 10   # Optimized Value
SLOW_MA = 40   # Optimized Value

# ✅ Fetch Live Market Data
def fetch_data():
    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=100)
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["fast_ma"] = df["close"].rolling(FAST_MA).mean()
    df["slow_ma"] = df["close"].rolling(SLOW_MA).mean()
    return df

# ✅ Execute Market Order
def place_order(order_type, amount):
    try:
        order = exchange.create_market_order(SYMBOL, order_type, amount)
        print(f"✅ {order_type.upper()} Order Executed: {amount} BTC")
        return order
    except Exception as e:
        print(f"⚠️ Order Failed: {e}")

# ✅ Live Trading Loop
btc_holdings = 0
while True:
    try:
        df = fetch_data()
        latest_price = df["close"].iloc[-1]
        fast = df["fast_ma"].iloc[-1]
        slow = df["slow_ma"].iloc[-1]

        if fast > slow and btc_holdings == 0:  # Buy Condition
            btc_holdings = LOT_SIZE
            place_order("buy", btc_holdings)
            buy_price = latest_price

        elif fast < slow and btc_holdings > 0:  # Sell Condition
            place_order("sell", btc_holdings)
            btc_holdings = 0

        # Stop-Loss & Take-Profit
        if btc_holdings > 0:
            stop_loss = buy_price * STOP_LOSS_PERCENT
            take_profit = buy_price * TAKE_PROFIT_PERCENT

            if latest_price <= stop_loss:
                print("🛑 Stop-Loss Triggered! Selling...")
                place_order("sell", btc_holdings)
                btc_holdings = 0

            elif latest_price >= take_profit:
                print("🚀 Take-Profit Reached! Selling...")
                place_order("sell", btc_holdings)
                btc_holdings = 0

        print(f"📈 Price: {latest_price:.2f}, BTC Holdings: {btc_holdings}")
        time.sleep(60)  # Wait 1 min before next check

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(10)
