BUY = "BUY"
STRONG_BUY = "STRONG_BUY"
SELL = "SELL"
STRONG_SELL = "STRONG_SELL"
HOLD = "HOLD"
ERROR = "ERROR"

RECOMMEDATIONS = [
    BUY,
    STRONG_BUY,
    SELL,
    STRONG_SELL,
    HOLD,
    ERROR,
]


def MA(ma: float, close: float) -> str:
    """Compute Moving Average

    Args:
        ma (float): MA value
        close (float): Close value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (ma < close):
        return BUY
    elif (ma > close):
        return SELL
    else:
        return HOLD


def RSI(rsi: float, rsi1: float) -> str:
    """Compute Relative Strength Index

    Args:
        rsi (float): RSI value
        rsi1 (float): RSI[1] value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (rsi < 30 and rsi1 < rsi):
        return BUY
    elif (rsi > 70 and rsi1 > rsi):
        return SELL
    else:
        return HOLD


def Stoch(k: float, d: float, k1: float, d1: float) -> str:
    """Compute Stochastic

    Args:
        k (float): Stoch.K value
        d (float): Stoch.D value
        k1 (float): Stoch.K[1] value
        d1 (float): Stoch.D[1] value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (k < 20 and d < 20 and k > d and k1 < d1):
        return BUY
    elif (k > 80 and d > 80 and k < d and k1 > d1):
        return SELL
    else:
        return HOLD


def CCI20(cci20: float, cci201: float) -> str:
    """Compute Commodity Channel Index 20

    Args:
        cci20 (float): CCI20 value
        cci201 ([type]): CCI20[1] value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (cci20 < -100 and cci20 > cci201):
        return BUY
    elif (cci20 > 100 and cci20 < cci201):
        return SELL
    else:
        return HOLD


def ADX(adx: float, adxpdi: float, adxndi: float, adxpdi1: float, adxndi1: float) -> str:
    """Compute Average Directional Index

    Args:
        adx (float): ADX value
        adxpdi (float): ADX+DI value
        adxndi (float): ADX-DI value
        adxpdi1 (float): ADX+DI[1] value
        adxndi1 (float): ADX-DI[1] value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (adx > 20 and adxpdi1 < adxndi1 and adxpdi > adxndi):
        return BUY
    elif (adx > 20 and adxpdi1 > adxndi1 and adxpdi < adxndi):
        return SELL
    else:
        return HOLD


def AO(ao: float, ao1: float, ao2: float) -> str:
    """Compute Awesome Oscillator

    Args:
        ao (float): AO value
        ao1 (float): AO[1] value
        ao2 (float): AO[2] value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (ao > 0 and ao1 < 0) or \
            (ao > 0 and ao1 > 0 and ao > ao1 and ao2 > ao1):
        return BUY
    elif (ao < 0 and ao1 > 0) or \
            (ao < 0 and ao1 < 0 and ao < ao1 and ao2 < ao1):
        return SELL
    else:
        return HOLD


def Mom(mom: float, mom1: float) -> str:
    """Compute Momentum

    Args:
        mom (float): Mom value
        mom1 (float): Mom[1] value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (mom < mom1):
        return SELL
    elif (mom > mom1):
        return BUY
    else:
        return HOLD


def MACD(macd: float, signal: float) -> str:
    """Compute Moving Average Convergence/Divergence

    Args:
        macd (float): MACD.macd value
        signal (float): MACD.signal value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (macd > signal):
        return BUY
    elif (macd < signal):
        return SELL
    else:
        return HOLD


def BBbuy(close: float, bblower: float) -> str:
    """Compute Bull Bear Buy

    Args:
        close (float): close value
        bblower (float): BB.lower value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (close < bblower):
        return BUY
    else:
        return HOLD


def BBsell(close: float, bbupper: float) -> str:
    """Compute Bull Bear Sell

    Args:
        close (float): close value
        bbupper (float): BB.upper value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (close > bbupper):
        return SELL
    else:
        return HOLD


def PSAR(psar: float, open: float) -> str:
    """Compute Parabolic Stop-And-Reverse

    Args:
        psar (float): P.SAR value
        open (float): open value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (psar < open):
        return BUY
    elif (psar > open):
        return SELL
    else:
        return HOLD


def recommend(value: float) -> str:
    """Compute Recommend

    Args:
        value (float): recommend value

    Returns:
        str: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL, or ERROR
    """
    if (-1.0 <= value < -0.5):
        return STRONG_SELL
    elif (-0.5 <= value < -0.1):
        return SELL
    elif (-0.1 <= value <= 0.1):
        return HOLD
    elif (0.1 < value <= 0.5):
        return BUY
    elif (0.5 < value <= 1.0):
        return STRONG_BUY
    else:
        return ERROR


def simple(value: float) -> str:
    """Compute Simple

    Args:
        value (float): Rec.X value

    Returns:
        str: BUY, SELL, or HOLD
    """
    if (value == -1):
        return SELL
    elif (value == 1):
        return BUY
    else:
        return HOLD


def calculate(idcs: dict) -> dict:
    """
    idcs is short for indicators.
    """
    # Abbreviatures:
    # OSC  - oscillators
    # MA   - moving averages
    # RCM  - recommendation
    # CMP  - computed
    # SUMM - summary
    analysis = {
        "OSC": {
            "RCM": None,
            "BUY": 0,
            "SELL": 0,
            "HOLD": 0,
            "CMP": {},
        },
        "MA": {
            "RCM": None,
            "BUY": 0,
            "SELL": 0,
            "HOLD": 0,
            "CMP": {},
        },
        "SUMM": {
            "RCM": None,
            "BUY": 0,
            "SELL": 0,
            "HOLD": 0,
        },
    }

    params = [
        # OSCILLATORS
        ("OSC", "RSI", RSI, "RSI RSI[1]"),
        ("OSC", "STOCH.K", Stoch, "Stoch.K Stoch.D Stoch.K[1] Stoch.D[1]"),
        ("OSC", "CCI", CCI20, "CCI20 CCI20[1]"),
        ("OSC", "ADX", ADX, "ADX ADX+DI ADX-DI ADX+DI[1] ADX-DI[1]"),
        ("OSC", "AO", AO, "AO AO[1] AO[2]"),
        ("OSC", "Mom", Mom, "Mom Mom[1]"),
        ("OSC", "MACD", MACD, "MACD.macd MACD.signal"),
        ("OSC", "BB.buy", BBbuy, "close BB.lower"),
        ("OSC", "BB.sell", BBsell, "close BB.upper"),
        ("OSC", "P.SAR", PSAR, "P.SAR open"),
        ("OSC", "Stoch.RSI", simple, "Rec.Stoch.RSI"),
        ("OSC", "W%R", simple, "Rec.WR"),
        ("OSC", "BBP", simple, "Rec.BBPower"),
        ("OSC", "UO", simple, "Rec.UO"),
        # MOVING AVERAGES
        ("MA", "EMA10", MA, "EMA10 close"),
        ("MA", "SMA10", MA, "SMA10 close"),
        ("MA", "EMA20", MA, "EMA20 close"),
        ("MA", "SMA20", MA, "SMA20 close"),
        ("MA", "EMA30", MA, "EMA30 close"),
        ("MA", "SMA30", MA, "SMA30 close"),
        ("MA", "EMA50", MA, "EMA50 close"),
        ("MA", "SMA50", MA, "SMA50 close"),
        ("MA", "EMA100", MA, "EMA100 close"),
        ("MA", "SMA100", MA, "SMA100 close"),
        ("MA", "EMA200", MA, "EMA200 close"),
        ("MA", "SMA200", MA, "SMA200 close"),
        ("MA", "Ichimoku", simple, "Rec.Ichimoku"),
        ("MA", "VWMA", simple, "Rec.VWMA"),
        ("MA", "HullMA", simple, "Rec.HullMA9"),
        # SUMMARY
        # ("OSC",  "RCM",       recommend, "Recommend.Other"),
        ("MA", "RCM", recommend, "Recommend.MA"),
        ("SUMM", "RCM", recommend, "Recommend.All"),
    ]

    cmpr = lambda k: (idcs.get(k) is not None)

    for group_key, idc_key, func, arg_keys in params:

        arg_keys = arg_keys.split()

        if all(map(cmpr, arg_keys)):

            args = tuple(map(idcs.get, arg_keys))
            rcm = func(*args)

            if idc_key == "RCM":
                analysis[group_key]["RCM"] = rcm
            else:
                analysis[group_key]["CMP"][idc_key] = rcm
                analysis[group_key][rcm] += 1

    cmpr = lambda k: analysis["OSC"][k]
    analysis["OSC"]["RCM"] = max(("BUY", "SELL", "HOLD"), key=cmpr)

    for key in ("BUY", "HOLD", "SELL"):
        analysis["SUMM"][key] = analysis["OSC"][key] + analysis["MA"][key]

    return analysis
