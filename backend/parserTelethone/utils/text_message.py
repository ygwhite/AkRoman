def create_message(signal_dict):
    for k, v in signal_dict.items():
        signal_dict[k] = '' if v is None else v

    pair = f"📊 Pair: {signal_dict.get('pair').upper()}" if signal_dict.get('pair') else ""
    timeframe = f"⏳ Timeframe: {signal_dict.get('timeframe')}" if signal_dict.get('timeframe') else ""
    type = f"⚠️ Signal type: {signal_dict.get('type')}" if signal_dict.get('type') else ""
    leverage = f"🚀 Leverage: {signal_dict.get('leverage')}" if signal_dict.get('leverage') else ""
    entry_targets = f"ℹ️ Entry Targets: {signal_dict.get('entry_targets')}" if signal_dict.get('entry_targets') else ""
    take_profit = f"🟩 Take-Profit Targets: {signal_dict.get('take_profit')}" if signal_dict.get('take_profit') else ""
    stop = f"🛑 Stop Targets: {signal_dict.get('stop')}" if signal_dict.get('stop') else ""
    price = f"💰 Price: {signal_dict.get('price')}" if signal_dict.get('price') else ""

    return f"""{pair}
{timeframe}
{type}
{leverage}
{entry_targets}
{take_profit}
{stop}
{price}
"""
