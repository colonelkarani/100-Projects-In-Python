import MetaTrader5 as mt5

if not mt5.initialize():
    print("MT5 initialization failed")
    mt5.shutdown()
    exit()

symbol = "USDJPY"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(f"Symbol {symbol} not found")
else:
    try:
        # Try new attribute first
        modes = symbol_info.order_filling_modes
        print("Supported filling modes bitmask:", modes)
    except AttributeError:
        # Fallback to older single filling_mode attribute
        try:
            filling_mode = symbol_info.filling_mode
            print("Single filling mode:", filling_mode)
            # Interpret filling_mode
            if filling_mode == mt5.ORDER_FILLING_IOC:
                print("Filling mode: ORDER_FILLING_IOC")
            elif filling_mode == mt5.ORDER_FILLING_FOK:
                print("Filling mode: ORDER_FILLING_FOK")
            elif filling_mode == mt5.ORDER_FILLING_RETURN:
                print("Filling mode: ORDER_FILLING_RETURN")
            else:
                print("Unknown filling mode")
        except AttributeError:
            print("No filling mode attribute available for this symbol")

mt5.shutdown()
