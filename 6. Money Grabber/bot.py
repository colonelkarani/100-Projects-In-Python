import MetaTrader5 as mt5


if not mt5.initialize():
    print("Failed to connect")


rates = mt5.copy_rates_from_pos("EURUSD", mt5.TIMEFRAME_H4, 0, 100)
print(rates)