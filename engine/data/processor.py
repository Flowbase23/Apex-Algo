"""
Data processing: cleaning, normalization, and feature engineering.

Transforms raw OHLCV data into ML-ready datasets with technical indicators
and derived features.
"""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# =========================================================================
#  Cleaning
# =========================================================================

def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw OHLCV data.

    - Ensures required columns exist
    - Drops rows with NaN/Inf
    - Sorts by timestamp
    - Removes duplicates on index
    - Ensures numeric types

    Args:
        df: Raw DataFrame with columns [open, high, low, close, volume]

    Returns:
        Cleaned DataFrame
    """
    required = ["open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()
    df.index = pd.to_datetime(df.index)

    # Ensure numeric
    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Remove rows with NaN or Inf
    df = df.replace([np.inf, -np.inf], np.nan)
    df.dropna(subset=required, inplace=True)

    # Sort and deduplicate
    df.sort_index(inplace=True)
    df = df[~df.index.duplicated(keep="first")]

    return df


def resample_ohlcv(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Resample OHLCV data to a different timeframe.

    Args:
        df: OHLCV DataFrame (index = datetime)
        rule: Pandas offset string e.g. "5min", "1h", "1d"

    Returns:
        Resampled DataFrame
    """
    return df.resample(rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna()


# =========================================================================
#  Technical Indicators
# =========================================================================

def add_sma(df: pd.DataFrame, windows: list[int] = [5, 10, 20, 50, 200]) -> pd.DataFrame:
    """Add Simple Moving Average columns."""
    df = df.copy()
    for w in windows:
        df[f"sma_{w}"] = df["close"].rolling(window=w).mean()
    return df


def add_ema(df: pd.DataFrame, windows: list[int] = [8, 12, 21, 26]) -> pd.DataFrame:
    """Add Exponential Moving Average columns."""
    df = df.copy()
    for w in windows:
        df[f"ema_{w}"] = df["close"].ewm(span=w, adjust=False).mean()
    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Add Relative Strength Index (fully vectorized, EMA-based).

    Uses EMA smoothing which is equivalent to Wilder's smoothing
    with alpha = 1/period (the standard modern RSI calculation).
    """
    df = df.copy()
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = 100 - (100 / (1 + rs))
    return df


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Add MACD, Signal line, and Histogram."""
    df = df.copy()
    ema_fast = df["close"].ewm(span=fast, adjust=False).mean()
    ema_slow = df["close"].ewm(span=slow, adjust=False).mean()
    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=signal, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df


def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
    """Add Bollinger Bands."""
    df = df.copy()
    df["bb_middle"] = df["close"].rolling(window=period).mean()
    bb_std = df["close"].rolling(window=period).std()
    df["bb_upper"] = df["bb_middle"] + std_dev * bb_std
    df["bb_lower"] = df["bb_middle"] - std_dev * bb_std
    df["bb_width"] = df["bb_upper"] - df["bb_lower"]
    df["bb_position"] = (df["close"] - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"]).replace(0, np.nan)
    return df


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Add Average True Range (ATR)."""
    df = df.copy()
    high_low = df["high"] - df["low"]
    high_close = abs(df["high"] - df["close"].shift())
    low_close = abs(df["low"] - df["close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df["atr"] = tr.rolling(window=period).mean()
    return df


def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add volume-based indicators."""
    df = df.copy()
    df["volume_sma_20"] = df["volume"].rolling(window=20).mean()
    df["volume_ratio"] = df["volume"] / df["volume_sma_20"].replace(0, np.nan)
    df["volume_change"] = df["volume"].pct_change()
    return df


# =========================================================================
#  Price-derived features
# =========================================================================

def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add price-derived features: returns, ranges, gaps."""
    df = df.copy()
    df["return_1"] = df["close"].pct_change(1)
    df["return_5"] = df["close"].pct_change(5)
    df["return_20"] = df["close"].pct_change(20)
    df["range"] = (df["high"] - df["low"]) / df["close"]
    df["gap"] = (df["open"] - df["close"].shift(1)) / df["close"].shift(1)
    df["intraday_range"] = (df["high"] - df["low"]) / df["open"]
    return df


# =========================================================================
#  Target / Label engineering
# =========================================================================

def add_target(
    df: pd.DataFrame,
    forward_periods: int = 1,
    threshold_pct: float = 0.0,
) -> pd.DataFrame:
    """Add target column for supervised learning.

    Creates binary classification target:
      - 1 = price goes up by more than threshold_pct
      - 0 = price stays within threshold_pct (or goes down)
      - -1 = price goes down by more than threshold_pct (optional)

    Args:
        df: DataFrame with 'close' column
        forward_periods: Number of bars to look ahead
        threshold_pct: Minimum change to count as move (as decimal)

    Returns:
        DataFrame with added 'target' column
    """
    df = df.copy()
    future_return = df["close"].shift(-forward_periods) / df["close"] - 1
    df["target"] = 0
    df.loc[future_return > threshold_pct, "target"] = 1
    df.loc[future_return < -threshold_pct, "target"] = -1

    # Drop rows where target can't be computed (end of series)
    df.dropna(subset=["target"], inplace=True)
    df["target"] = df["target"].astype(int)
    return df


def add_regression_target(
    df: pd.DataFrame,
    forward_periods: int = 1,
) -> pd.DataFrame:
    """Add regression target: future return over forward_periods."""
    df = df.copy()
    df["target_return"] = df["close"].shift(-forward_periods) / df["close"] - 1
    df.dropna(subset=["target_return"], inplace=True)
    return df


# =========================================================================
#  Full Feature Pipeline
# =========================================================================

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full feature engineering pipeline.

    Args:
        df: Raw OHLCV DataFrame

    Returns:
        DataFrame with all technical indicators and price features
    """
    df = clean_ohlcv(df)
    df = add_sma(df)
    df = add_ema(df)
    df = add_rsi(df)
    df = add_macd(df)
    df = add_bollinger_bands(df)
    df = add_atr(df)
    df = add_volume_indicators(df)
    df = add_price_features(df)

    # Drop rows with NaN from rolling calculations
    df.dropna(inplace=True)
    return df


def feature_columns() -> list[str]:
    """Return all feature column names (excluding open/high/low/close/volume)."""
    return [
        "sma_5", "sma_10", "sma_20", "sma_50", "sma_200",
        "ema_8", "ema_12", "ema_21", "ema_26",
        "rsi",
        "macd", "macd_signal", "macd_hist",
        "bb_middle", "bb_upper", "bb_lower", "bb_width", "bb_position",
        "atr",
        "volume_sma_20", "volume_ratio", "volume_change",
        "return_1", "return_5", "return_20",
        "range", "gap", "intraday_range",
    ]