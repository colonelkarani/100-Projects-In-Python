import MetaTrader5 as mt5
import pandas as pd
import numpy as np

# Parameters (adjust as needed)
SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_H1
LOT_SIZE = 0.01
SWING_WINDOW = 1
WICK_BODY_RATIO = 1.5
LOOK_AHEAD = 3
BUFFER_PCT = 0.005
RISK_REWARD_RATIO = 2
START_POS = 0
N_BARS = 1000  # Number of historical bars to backtest

# Initialize MT5 connection
if not mt5.initialize():
    print("Failed to initialize MT5")
    mt5.shutdown()
    exit()

def fetch_data(symbol, timeframe, n=1000):
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
                        'index': i,
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
                        'index': i,
                        'time': df.index[i],
                        'type': 'bearish',
                        'price': highs.iloc[sh]
                    })
                    break
    return liquidity_grabs

def calculate_stop_loss(entry_price, trade_type, liquidity_grab_price, swing_price, buffer_pct=BUFFER_PCT):
    if trade_type.lower() not in ['long', 'short']:
        raise ValueError("trade_type must be 'long' or 'short'")

    buffer = entry_price * buffer_pct

    if trade_type.lower() == 'long':
        base_stop = min(liquidity_grab_price, swing_price)
        stop_loss = base_stop - buffer
        if stop_loss >= entry_price:
            stop_loss = entry_price - buffer
    else:
        base_stop = max(liquidity_grab_price, swing_price)
        stop_loss = base_stop + buffer
        if stop_loss <= entry_price:
            stop_loss = entry_price + buffer

    return stop_loss

def calculate_take_profit(entry_price, stop_loss_price, trade_type, risk_reward_ratio=RISK_REWARD_RATIO):
    if trade_type.lower() == 'long':
        risk = entry_price - stop_loss_price
        take_profit = entry_price + abs(risk) * risk_reward_ratio
        if take_profit <= entry_price:
            take_profit = entry_price + abs(risk) * risk_reward_ratio
    elif trade_type.lower() == 'short':
        risk = stop_loss_price - entry_price
        take_profit = entry_price - abs(risk) * risk_reward_ratio
        if take_profit >= entry_price:
            take_profit = entry_price - abs(risk) * risk_reward_ratio
    else:
        raise ValueError("trade_type must be 'long' or 'short'")
    return take_profit

def find_recent_swing_price(df, grab_index, trade_type):
    if trade_type == 'long':
        lows = df['low'][:grab_index]
        if not lows.empty:
            return lows.min()
        else:
            return df['low'].iloc[grab_index]
    else:
        highs = df['high'][:grab_index]
        if not highs.empty:
            return highs.max()
        else:
            return df['high'].iloc[grab_index]

def backtest(df):
    liquidity_grabs = detect_liquidity_grabs(df)
    
    trades = []
    for grab in liquidity_grabs:
        i = grab['index']
        trade_type = 'long' if grab['type'] == 'bullish' else 'short'
        entry_price = grab['price']
        swing_price = find_recent_swing_price(df, i, trade_type)
        sl = calculate_stop_loss(entry_price, trade_type, grab['price'], swing_price)
        tp = calculate_take_profit(entry_price, sl, trade_type)
        
        # Simulate trade outcome by scanning future bars until TP or SL hit or max bars reached
        trade_outcome = None
        entry_index = i
        for j in range(entry_index + 1, len(df)):
            high = df['high'].iloc[j]
            low = df['low'].iloc[j]
            
            if trade_type == 'long':
                # Check if SL hit first
                if low <= sl:
                    trade_outcome = {'result': 'loss', 'exit_price': sl, 'exit_index': j}
                    break
                # Check if TP hit first
                elif high >= tp:
                    trade_outcome = {'result': 'win', 'exit_price': tp, 'exit_index': j}
                    break
            else:  # short
                if high >= sl:
                    trade_outcome = {'result': 'loss', 'exit_price': sl, 'exit_index': j}
                    break
                elif low <= tp:
                    trade_outcome = {'result': 'win', 'exit_price': tp, 'exit_index': j}
                    break
        
        # If neither SL nor TP hit, close at last bar price (close)
        if trade_outcome is None:
            exit_price = df['close'].iloc[-1]
            exit_index = len(df) - 1
            # Determine if trade was profitable or not
            if trade_type == 'long':
                result = 'win' if exit_price > entry_price else 'loss'
            else:
                result = 'win' if exit_price < entry_price else 'loss'
            trade_outcome = {'result': result, 'exit_price': exit_price, 'exit_index': exit_index}
        
        profit = 0
        if trade_type == 'long':
            profit = (trade_outcome['exit_price'] - entry_price) * LOT_SIZE
        else:
            profit = (entry_price - trade_outcome['exit_price']) * LOT_SIZE
        
        trades.append({
            'entry_time': df.index[entry_index],
            'exit_time': df.index[trade_outcome['exit_index']],
            'trade_type': trade_type,
            'entry_price': entry_price,
            'exit_price': trade_outcome['exit_price'],
            'result': trade_outcome['result'],
            'profit': profit
        })
    
    return trades

def print_summary(trades):
    total_trades = len(trades)
    wins = sum(1 for t in trades if t['result'] == 'win')
    losses = total_trades - wins
    total_profit = sum(t['profit'] for t in trades)
    avg_profit = total_profit / total_trades if total_trades > 0 else 0
    win_rate = wins / total_trades * 100 if total_trades > 0 else 0

    print(f"Total trades: {total_trades}")
    print(f"Wins: {wins}")
    print(f"Losses: {losses}")
    print(f"Win rate: {win_rate:.2f}%")
    print(f"Total profit: {total_profit:.2f}")
    print(f"Average profit per trade: {avg_profit:.4f}")

if __name__ == "__main__":
    df = fetch_data(SYMBOL, TIMEFRAME, N_BARS)
    trades = backtest(df)
    print_summary(trades)
    mt5.shutdown()
