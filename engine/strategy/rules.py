"""
Explicit logical trading rules based on technical indicators.

These rules encode classic trading logic (overbought/oversold, trend following,
breakout detection, mean reversion) that can be combined with or used as
a baseline against ML predictions.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# =========================================================================
#  Signal Constants
# =========================================================================

STRONG_BUY = 2
BUY = 1
NEUTRAL = 0
SELL = -1
STRONG_SELL = -2

DIRECTION_BUY = 1
DIRECTION_SELL = -1


# =========================================================================
#  Rule functions
# =========================================================================

def _check_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    """Check which required columns are missing from df."""
    return [c for c in required if c not in df.columns]


def rsi_overbought_oversold(df: pd.DataFrame) -> pd.Series:
    """RSI overbought/oversold rule.

    - SELL when RSI > 70 (overbought)
    - BUY when RSI < 30 (oversold)

    Returns:
        Series of signals (-1 or 1)
    """
    missing = _check_columns(df, ["rsi"])
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)
    signal[df["rsi"] > 70] = SELL
    signal[df["rsi"] < 30] = BUY
    return signal


def rsi_divergence(df: pd.DataFrame, lookback: int = 14) -> pd.Series:
    """Detect RSI divergence — potential reversal signals.

    Bullish divergence: price makes lower low, RSI makes higher low
    Bearish divergence: price makes higher high, RSI makes lower high

    Returns:
        Series of signals (-1 bearish, 1 bullish, 0 none)
    """
    missing = _check_columns(df, ["close", "rsi"])
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)

    # Rolling windows to find local extrema
    for i in range(lookback, len(df) - lookback):
        idx = df.index[i]
        window = df.iloc[i - lookback: i + 1]

        # Current values
        price_low = df["close"].iloc[i]
        rsi_val = df["rsi"].iloc[i]

        # Previous swing low/high
        prev_low_idx = window["close"].idxmin()
        prev_high_idx = window["close"].idxmax()

        if prev_low_idx != idx:
            prev_price_low = df.loc[prev_low_idx, "close"]
            prev_rsi_low = df.loc[prev_low_idx, "rsi"]

            # Bullish divergence: price lower low, RSI higher low
            if price_low < prev_price_low and rsi_val > prev_rsi_low:
                signal[idx] = BUY

        if prev_high_idx != idx:
            prev_price_high = df.loc[prev_high_idx, "close"]
            prev_rsi_high = df.loc[prev_high_idx, "rsi"]

            # Bearish divergence: price higher high, RSI lower high
            if (df["close"].iloc[i] > prev_price_high and
                df["rsi"].iloc[i] < prev_rsi_high):
                signal[idx] = SELL

    return signal


def ema_crossover(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.Series:
    """EMA crossover rule.

    - BUY when fast EMA crosses above slow EMA
    - SELL when fast EMA crosses below slow EMA

    Returns:
        Series of signals
    """
    fast_col = f"ema_{fast}"
    slow_col = f"ema_{slow}"

    missing = _check_columns(df, [fast_col, slow_col])
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Run add_ema() first.")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)

    # Crossover detection
    prev_fast = df[fast_col].shift(1)
    prev_slow = df[slow_col].shift(1)

    signal[(df[fast_col] > df[slow_col]) & (prev_fast <= prev_slow)] = BUY
    signal[(df[fast_col] < df[slow_col]) & (prev_fast >= prev_slow)] = SELL

    return signal


def sma_trend(df: pd.DataFrame, short: int = 50, long: int = 200) -> pd.Series:
    """SMA trend rule (Golden Cross / Death Cross).

    - BUY when short SMA > long SMA (Golden Cross)
    - SELL when short SMA < long SMA (Death Cross)

    Returns:
        Series of signals
    """
    short_col = f"sma_{short}"
    long_col = f"sma_{long}"

    missing = _check_columns(df, [short_col, long_col])
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Run add_sma() first.")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)
    signal[df[short_col] > df[long_col]] = BUY
    signal[df[short_col] < df[long_col]] = SELL
    return signal


def bollinger_breakout(df: pd.DataFrame) -> pd.Series:
    """Bollinger Bands breakout/mean reversion rule.

    - SELL when price touches upper band (overextended)
    - BUY when price touches lower band (oversold)

    Returns:
        Series of signals
    """
    missing = _check_columns(df, ["close", "bb_upper", "bb_lower"])
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Run add_bollinger_bands() first.")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)
    signal[df["close"] >= df["bb_upper"]] = SELL
    signal[df["close"] <= df["bb_lower"]] = BUY
    return signal


def macd_signal_cross(df: pd.DataFrame) -> pd.Series:
    """MACD signal line crossover rule.

    - BUY when MACD crosses above signal line
    - SELL when MACD crosses below signal line

    Returns:
        Series of signals
    """
    missing = _check_columns(df, ["macd", "macd_signal"])
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Run add_macd() first.")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)

    prev_macd = df["macd"].shift(1)
    prev_signal = df["macd_signal"].shift(1)

    signal[(df["macd"] > df["macd_signal"]) & (prev_macd <= prev_signal)] = BUY
    signal[(df["macd"] < df["macd_signal"]) & (prev_macd >= prev_signal)] = SELL

    return signal


def volume_breakout(df: pd.DataFrame, volume_threshold: float = 1.5) -> pd.Series:
    """Volume breakout rule.

    - BUY when price up + volume > threshold * average volume
    - SELL when price down + volume > threshold * average volume

    Returns:
        Series of signals
    """
    missing = _check_columns(df, ["close", "volume", "volume_sma_20"])
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Run add_volume_indicators() first.")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)
    high_volume = df["volume"] > df["volume_sma_20"] * volume_threshold

    signal[high_volume & (df["close"] > df["close"].shift(1))] = BUY
    signal[high_volume & (df["close"] < df["close"].shift(1))] = SELL
    return signal


def price_momentum(df: pd.DataFrame, lookback: int = 5) -> pd.Series:
    """Price momentum rule.

    - BUY when return over lookback is positive and above threshold
    - SELL when return over lookback is negative and below threshold

    Returns:
        Series of signals
    """
    missing = _check_columns(df, ["close"])
    if missing:
        raise ValueError(f"Missing required columns: {missing}.")

    signal = pd.Series(NEUTRAL, index=df.index, dtype=int)
    momentum = df["close"].pct_change(lookback)
    threshold = 0.02  # 2% momentum threshold

    signal[momentum > threshold] = BUY
    signal[momentum < -threshold] = SELL
    return signal


# =========================================================================
#  Combined Rule Engine
# =========================================================================

def compute_rule_signals(df: pd.DataFrame, rules: Optional[list[str]] = None) -> pd.DataFrame:
    """Compute signals from a set of rule names.

    Args:
        df: DataFrame with technical indicators
        rules: List of rule names to apply (default: all)

    Returns:
        DataFrame with one column per rule and a 'consensus' column
    """
    available_rules = {
        "rsi_ob_os": rsi_overbought_oversold,
        "rsi_divergence": rsi_divergence,
        "ema_crossover": ema_crossover,
        "sma_trend": sma_trend,
        "bollinger_breakout": bollinger_breakout,
        "macd_signal": macd_signal_cross,
        "volume_breakout": volume_breakout,
        "price_momentum": price_momentum,
    }

    if rules is None:
        rules = list(available_rules.keys())

    results = {}
    for name in rules:
        if name in available_rules:
            try:
                results[name] = available_rules[name](df)
            except (ValueError, KeyError) as e:
                logger.warning(f"Could not compute rule '{name}': {e}")
                results[name] = pd.Series(NEUTRAL, index=df.index, dtype=int)

    result_df = pd.DataFrame(results, index=df.index)

    # Consensus: sum of all signals, clipped to [-2, 2]
    result_df["consensus"] = result_df.sum(axis=1).clip(-2, 2).astype(int)

    return result_df