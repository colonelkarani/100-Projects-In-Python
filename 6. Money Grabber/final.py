import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime

# Initialize MT5 connection
if not mt5.initialize():
    print("Failed to initialize MT5")
    mt5.shutdown()
    exit()

SYMBOL = "GBPUSD"
TIMEFRAME = mt5.TIMEFRAME_M10
LOT_SIZE = 0.02
SWING_WINDOW = 1
WICK_BODY_RATIO = 1.5
LOOK_AHEAD = 3
BUFFER = 0.30  # For XAUUSD, adjust as needed
RISK_REWARD_RATIO = 2

def get_supported_filling_mode(symbol):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        raise ValueError(f"Symbol {symbol} not found")
    
    # Try new attribute first
    try:
        modes = symbol_info.order_filling_modes
        # Prefer IOC, then FOK, then RETURN
        if modes & mt5.ORDER_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        elif modes & mt5.ORDER_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        elif modes & mt5.ORDER_FILLING_RETURN:
            return mt5.ORDER_FILLING_RETURN
    except AttributeError:
        # Fallback: try old attribute 'filling_mode' (single mode)
        try:
            filling_mode = symbol_info.filling_mode
            if filling_mode in [mt5.ORDER_FILLING_IOC, mt5.ORDER_FILLING_FOK, mt5.ORDER_FILLING_RETURN]:
                return filling_mode
        except AttributeError:
            pass
    
    # Default fallback
    print("Warning: Could not detect supported filling modes, defaulting to ORDER_FILLING_IOC")
    return mt5.ORDER_FILLING_IOC

FILLING_MODE = get_supported_filling_mode(SYMBOL)
print(f"Using filling mode: {FILLING_MODE}")

def fetch_data(symbol, timeframe, n=100):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    return df

def detect_liquidity_grabs(df, swing_window=SWING_WINDOW, wick_body_ratio=WICK_BODY_RATIO, look_ahead=LOOK_AHEAD):
    liquidity_grabs = []
    
    highs = df['high']
    lows = df['low']
    opens = df['open']
    closes = df['close']
    
    swing_highs = []
    swing_lows = []
    for i in range(swing_window, len(df) - swing_window):
        if highs.iloc[i] == max(highs.iloc[i - swing_window:i + swing_window + 1]):
            swing_highs.append(i)
        if lows.iloc[i] == min(lows.iloc[i - swing_window:i + swing_window + 1]):
            swing_lows.append(i)
    
    for sl in swing_lows:
        for i in range(sl + 1, min(sl + 1 + look_ahead, len(df))):
            candle_body = abs(opens.iloc[i] - closes.iloc[i])
            lower_wick = min(opens.iloc[i], closes.iloc[i]) - lows.iloc[i]
            if lows.iloc[i] < lows.iloc[sl]:
                if candle_body > 0 and lower_wick > wick_body_ratio * candle_body and closes.iloc[i] > lows.iloc[sl]:
                    liquidity_grabs.append({
                        'time': df.index[i],
                        'type': 'bullish',
                        'price': lows.iloc[sl]
                    })
                    break
    
    for sh in swing_highs:
        for i in range(sh + 1, min(sh + 1 + look_ahead, len(df))):
            candle_body = abs(opens.iloc[i] - closes.iloc[i])
            upper_wick = highs.iloc[i] - max(opens.iloc[i], closes.iloc[i])
            if highs.iloc[i] > highs.iloc[sh]:
                if candle_body > 0 and upper_wick > wick_body_ratio * candle_body and closes.iloc[i] < highs.iloc[sh]:
                    liquidity_grabs.append({
                        'time': df.index[i],
                        'type': 'bearish',
                        'price': highs.iloc[sh]
                    })
                    break
    return liquidity_grabs

def calculate_stop_loss(entry_price, trade_type, liquidity_grab_price, swing_price, buffer_pct=0.005, atr=None):
    """
    Calculate stop loss price for long or short trades using swing points, liquidity grab, and a buffer.
    
    Parameters:
    - entry_price (float): The price at which the trade was entered.
    - trade_type (str): 'long' or 'short'.
    - liquidity_grab_price (float): Price level representing liquidity grab.
    - swing_price (float): Recent swing low (for longs) or swing high (for shorts).
    - buffer_pct (float): Buffer as a percentage of entry price (default 0.5%).
    - atr (float or None): Average True Range for dynamic buffer adjustment (optional).
    
    Returns:
    - stop_loss (float): Calculated stop loss price.
    """
    if trade_type.lower() not in ['long', 'short']:
        raise ValueError("trade_type must be 'long' or 'short'")

    # Determine buffer amount in price terms
    if atr is not None:
        buffer = atr * buffer_pct  # buffer scaled by volatility
    else:
        buffer = entry_price * buffer_pct  # fixed percentage buffer

    if trade_type.lower() == 'long':
        # Stop loss below the lower of liquidity grab or swing low minus buffer
        base_stop = min(liquidity_grab_price, swing_price)
        stop_loss = base_stop - buffer
        # Ensure stop loss is below entry price
        if stop_loss >= entry_price:
            stop_loss = entry_price - buffer
    else:  # short
        # Stop loss above the higher of liquidity grab or swing high plus buffer
        base_stop = max(liquidity_grab_price, swing_price)
        stop_loss = base_stop + buffer
        # Ensure stop loss is above entry price
        if stop_loss <= entry_price:
            stop_loss = entry_price + buffer

    return stop_loss

def calculate_take_profit(entry_price, stop_loss_price, trade_type, risk_reward_ratio=RISK_REWARD_RATIO):
    if trade_type.lower() == 'long':
        risk = entry_price - stop_loss_price
        take_profit = entry_price + risk * risk_reward_ratio
        if take_profit <= entry_price:
            take_profit = entry_price + abs(risk) * risk_reward_ratio
    elif trade_type.lower() == 'short':
        risk = stop_loss_price - entry_price
        take_profit = entry_price - risk * risk_reward_ratio
        if take_profit >= entry_price:
            take_profit = entry_price - abs(risk) * risk_reward_ratio
    else:
        raise ValueError("trade_type must be 'long' or 'short'")
    return take_profit

def place_order(symbol, trade_type, volume, price, sl, tp):
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": mt5.ORDER_TYPE_BUY if trade_type == 'long' else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 234000,
        "comment": "Liquidity Grab Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    result = mt5.order_send(request)
    return result

def find_recent_swing_price(df, grab_time, trade_type):
    idx = df.index.get_loc(grab_time)
    if trade_type == 'long':
        lows = df['low'][:idx]
        if not lows.empty:
            return lows.min()
        else:
            return df['low'].iloc[idx]
    else:
        highs = df['high'][:idx]
        if not highs.empty:
            return highs.max()
        else:
            return df['high'].iloc[idx]

def main_loop():
    print("Starting market monitoring for liquidity grabs...")
    traded_times = set()
    
    while True:
        df = fetch_data(SYMBOL, TIMEFRAME, 100)
        liquidity_grabs = detect_liquidity_grabs(df)
        
        if liquidity_grabs:
            for grab in liquidity_grabs:
                if grab['time'] in traded_times:
                    continue
                
                entry_price = grab['price']
                trade_type = 'long' if grab['type'] == 'bullish' else 'short'
                swing_price = find_recent_swing_price(df, grab['time'], trade_type)
                
                sl = calculate_stop_loss(entry_price, trade_type, grab['price'], swing_price)
                tp = calculate_take_profit(entry_price, sl, trade_type)
                
                price = mt5.symbol_info_tick(SYMBOL).ask if trade_type == 'long' else mt5.symbol_info_tick(SYMBOL).bid
                
                print(f"Placing {trade_type} order at {price:.2f} with SL {sl:.2f} and TP {tp:.2f} (detected at {grab['time']})")
                
                result = place_order(SYMBOL, trade_type, LOT_SIZE, price, sl, tp)
                if result.retcode != mt5.TRADE_RETCODE_DONE:
                    print(f"Order failed: {result.comment}")
                else:
                    print(f"Order placed successfully: {result}")
                    traded_times.add(grab['time'])
        else:
            print(f"{datetime.now()} - No liquidity grabs detected.")
        
        time.sleep(3600)  # Wait for next bar (1 hour)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")
    finally:
        mt5.shutdown()
