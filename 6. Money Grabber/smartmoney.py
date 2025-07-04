import smartmoney as smc

import MetaTrader5 as mt5

if not mt5.initialize():
    print("Error connecting to mt5")

rates = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_H1, 1, 100)



