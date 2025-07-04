import MetaTrader5 as mt5
import pandas as pd
import numpy as np

if not mt5.initialize():
    print("Error connecting to mt5")

mt5_data = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 1, 100)

rates = np.array(mt5_data, dtype=[('time', 'i8'), ('open', 'f8'), ('high', 'f8'), ('low', 'f8'), ('close', 'f8'), ('tick_volume', 'i8'), ('spread', 'i8'), ('real_volume', 'i8')])

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

def find_swing_highs_lows(df, window=3):
    highs = df['high']
    lows = df['low']
    swing_highs = []
    swing_lows = []
    
    for i in range(window, len(df) - window):
        if highs.iloc[i] == max(highs.iloc[i - window:i + window + 1]):
            swing_highs.append(df.index[i])
        if lows.iloc[i] == min(lows.iloc[i - window:i + window + 1]):
            swing_lows.append(df.index[i])
    
    return swing_highs, swing_lows

swing_highs, swing_lows = find_swing_highs_lows(df)
#print("Swing Highs:", swing_highs)
#print("Swing Lows:", swing_lows)

def detect_liquidity_grabs(df, swing_window=1, wick_body_ratio=1.5, look_ahead=3):
    liquidity_grabs = []
    
    highs = df['high']
    lows = df['low']
    opens = df['open']
    closes = df['close']
    
    # Detect swing highs and lows
    swing_highs = []
    swing_lows = []
    for i in range(swing_window, len(df) - swing_window):
        if highs.iloc[i] == max(highs.iloc[i - swing_window:i + swing_window + 1]):
            swing_highs.append(i)
        if lows.iloc[i] == min(lows.iloc[i - swing_window:i + swing_window + 1]):
            swing_lows.append(i)
    
    # Debug: print number of swings found
    print(f"Swing highs found: {len(swing_highs)}, Swing lows found: {len(swing_lows)}")
    
    for sl in swing_lows:
        for i in range(sl + 1, min(sl + 1 + look_ahead, len(df))):
            candle_body = abs(opens.iloc[i] - closes.iloc[i])
            lower_wick = min(opens.iloc[i], closes.iloc[i]) - lows.iloc[i]
            if lows.iloc[i] < lows.iloc[sl]:  # wick pierces swing low
                if candle_body > 0 and lower_wick > wick_body_ratio * candle_body and closes.iloc[i] > lows.iloc[sl]:
                    liquidity_grabs.append({
                        'time': df.index[i],
                        'type': 'bullish',
                        'price': lows.iloc[sl]
                    })
                    # Once detected, break to avoid duplicates for same swing low
                    break
    
    for sh in swing_highs:
        for i in range(sh + 1, min(sh + 1 + look_ahead, len(df))):
            candle_body = abs(opens.iloc[i] - closes.iloc[i])
            upper_wick = highs.iloc[i] - max(opens.iloc[i], closes.iloc[i])
            if highs.iloc[i] > highs.iloc[sh]:  # wick pierces swing high
                if candle_body > 0 and upper_wick > wick_body_ratio * candle_body and closes.iloc[i] < highs.iloc[sh]:
                    liquidity_grabs.append({
                        'time': df.index[i],
                        'type': 'bearish',
                        'price': highs.iloc[sh]
                    })
                    break
    
    return liquidity_grabs

liquidity_grabs = detect_liquidity_grabs(df)

# if liquidity_grabs:
#     for grab in liquidity_grabs:
#         print(f"{grab['type'].capitalize()} liquidity grab at {grab['time']} around price {grab['price']}")
# else:
#     print("No liquidity grabs detected.")

#df.to_excel("data.xlsx")

def calculate_stop_loss(entry_price, trade_type, liquidity_grab_price, swing_price, buffer=0.0005):
    """
    Calculate stop loss price for a trade.
    
    Parameters:
    - entry_price: float, your entry price
    - trade_type: 'long' or 'short'
    - liquidity_grab_price: float, price level of liquidity grab (low for long, high for short)
    - swing_price: float, recent swing low (for long) or swing high (for short)
    - buffer: float, small price buffer to avoid noise (default 0.0005, adjust per instrument)
    
    Returns:
    - stop_loss_price: float
    """
    if trade_type.lower() == 'long':
        # Stop loss below the lower of liquidity grab or swing low minus buffer
        stop_loss = min(liquidity_grab_price, swing_price) - buffer
        if stop_loss >= entry_price:
            # Ensure stop loss is below entry price
            stop_loss = entry_price - buffer
    elif trade_type.lower() == 'short':
        # Stop loss above the higher of liquidity grab or swing high plus buffer
        stop_loss = max(liquidity_grab_price, swing_price) + buffer
        if stop_loss <= entry_price:
            # Ensure stop loss is above entry price
            stop_loss = entry_price + buffer
    else:
        raise ValueError("trade_type must be 'long' or 'short'")
    
    return stop_loss
def calculate_take_profit(entry_price, stop_loss_price, trade_type, risk_reward_ratio=2):
    """
    Calculate take profit price based on risk-reward ratio.
    
    Parameters:
    - entry_price: float, your entry price
    - stop_loss_price: float, your stop loss price
    - trade_type: 'long' or 'short'
    - risk_reward_ratio: float, desired reward-to-risk ratio (default 2)
    
    Returns:
    - take_profit_price: float
    """
    if trade_type.lower() == 'long':
        risk = entry_price - stop_loss_price
        take_profit = entry_price + risk * risk_reward_ratio
        if take_profit <= entry_price:
            # Ensure TP is above entry price for long trades
            take_profit = entry_price + abs(risk) * risk_reward_ratio
    elif trade_type.lower() == 'short':
        risk = stop_loss_price - entry_price
        take_profit = entry_price - risk * risk_reward_ratio
        if take_profit >= entry_price:
            # Ensure TP is below entry price for short trades
            take_profit = entry_price - abs(risk) * risk_reward_ratio
    else:
        raise ValueError("trade_type must be 'long' or 'short'")
    
    return take_profit


# Use the first detected liquidity grab as an example, if available
if liquidity_grabs:
    grab = liquidity_grabs[0]
    entry_price = grab['price']  # Assume entry at liquidity grab price
    trade_type = 'long' if grab['type'] == 'bullish' else 'short'
    # Find the corresponding swing price
    if trade_type == 'long':
        # Find the most recent swing low before the grab
        swing_lows_indices = [i for i, t in enumerate(df.index) if t <= grab['time']]
        swing_price = df['low'].iloc[swing_lows_indices[-1]] if swing_lows_indices else grab['price']
    else:
        # Find the most recent swing high before the grab
        swing_highs_indices = [i for i, t in enumerate(df.index) if t <= grab['time']]
        swing_price = df['high'].iloc[swing_highs_indices[-1]] if swing_highs_indices else grab['price']
    buffer = 0.30  # For XAUUSD, adjust as needed (e.g., 30 cents)
    stop_loss = calculate_stop_loss(entry_price, trade_type, grab['price'], swing_price, buffer)
    take_profit = calculate_take_profit(entry_price, stop_loss, trade_type, risk_reward_ratio=2)
    print(f"Take profit for {trade_type} trade at {grab['time']}: {take_profit:.2f}")
    print(f"Stop loss for {trade_type} trade at {grab['time']}: {stop_loss:.2f}")
else:
    print("No liquidity grabs detected, so no stop loss calculated.")


