"""
Data ingestion layer: fetches market data from multiple sources.

Sources:
  - Yahoo Finance (yfinance) — free, no API key needed
  - Alpha Vantage — requires API key (placeholder)
  - Polygon.io — requires API key (placeholder)
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

import pandas as pd
import requests

from config.settings import (
    ENABLE_YFINANCE,
    ENABLE_ALPHA_VANTAGE,
    ENABLE_POLYGON,
    ALPHA_VANTAGE_API_KEY,
    POLYGON_API_KEY,
    TIMEFRAMES,
    DEFAULT_TIMEFRAME,
    DATA_CACHE_DIR,
)

logger = logging.getLogger(__name__)


# =========================================================================
#  Yahoo Finance (free, no API key)
# =========================================================================

def fetch_yfinance(
    symbol: str,
    timeframe: str = DEFAULT_TIMEFRAME,
    period: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance.

    Args:
        symbol: Ticker symbol (e.g. "ES=F", "EURUSD=X", "AAPL")
        timeframe: Bar size from TIMEFRAMES keys ("1m","5m","15m","1h","1d")
        period: Override the default period for this timeframe

    Returns:
        DataFrame with columns: [open, high, low, close, volume]
    """
    import yfinance as yf

    tf = TIMEFRAMES.get(timeframe, TIMEFRAMES[DEFAULT_TIMEFRAME])
    p = period or tf["period"]
    interval = tf["interval"]

    logger.info(f"Fetching {symbol} from Yahoo Finance ({interval}/{p})")

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=p, interval=interval)

    if df.empty:
        logger.warning(f"No data returned for {symbol} ({interval}/{p})")
        return df

    # Standardize column names
    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })
    df.index.name = "timestamp"
    df = df[["open", "high", "low", "close", "volume"]].copy()
    df.dropna(inplace=True)

    return df


# =========================================================================
#  Alpha Vantage
# =========================================================================

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
_alpha_vantage_disabled_logged = False


def fetch_alpha_vantage(
    symbol: str,
    interval: str = "60min",
    outputsize: str = "compact",
) -> pd.DataFrame:
    """Fetch data from Alpha Vantage (requires API key).

    Args:
        symbol: Forex pair (e.g. "EURUSD") or stock symbol
        interval: "1min","5min","15min","30min","60min","daily","weekly","monthly"
        outputsize: "compact" (last 100) or "full" (up to 20 years)

    Returns:
        DataFrame with columns: [open, high, low, close, volume]
    """
    global _alpha_vantage_disabled_logged

    if not ENABLE_ALPHA_VANTAGE:
        if not _alpha_vantage_disabled_logged:
            logger.info("Alpha Vantage disabled — set ENABLE_ALPHA_VANTAGE=True and provide API key")
            _alpha_vantage_disabled_logged = True
        return pd.DataFrame()

    if ALPHA_VANTAGE_API_KEY == "YOUR_ALPHA_VANTAGE_KEY":
        logger.warning("Alpha Vantage API key not configured")
        return pd.DataFrame()

    function = "FX_INTRADAY" if interval.endswith("min") else "FX_DAILY"
    params = {
        "function": function,
        "from_symbol": symbol[:3],
        "to_symbol": symbol[3:],
        "interval": interval,
        "outputsize": outputsize,
        "apikey": ALPHA_VANTAGE_API_KEY,
    }

    if function == "FX_DAILY":
        params.pop("interval", None)

    logger.info(f"Fetching {symbol} from Alpha Vantage ({interval})")
    response = requests.get(ALPHA_VANTAGE_BASE, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "Time Series" not in str(data.keys()):
        logger.error(f"Unexpected Alpha Vantage response: {data.get('Note', data)}")
        return pd.DataFrame()

    # Parse the time series key (varies by function)
    series_key = [k for k in data if "Time Series" in k]
    if not series_key:
        return pd.DataFrame()

    df = pd.DataFrame.from_dict(data[series_key[0]], orient="index")
    column_map = {
        "1. open": "open", "2. high": "high", "3. low": "low",
        "4. close": "close", "5. volume": "volume",
    }
    df = df.rename(columns=column_map)
    df.index = pd.to_datetime(df.index)
    df.index.name = "timestamp"
    df = df[["open", "high", "low", "close", "volume"]].astype(float)
    df.dropna(inplace=True)
    df.sort_index(inplace=True)

    return df


# =========================================================================
#  Polygon.io
# =========================================================================

_polygon_disabled_logged = False


def fetch_polygon(
    symbol: str,
    timespan: str = "hour",
    multiplier: int = 1,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 5000,
) -> pd.DataFrame:
    """Fetch data from Polygon.io (requires API key).

    Args:
        symbol: Ticker (e.g. "ES=F", "EURUSD=X")
        timespan: "minute","hour","day","week","month"
        multiplier: Size of the timespan multiplier
        from_date: Start date "YYYY-MM-DD" (default: 30 days ago)
        to_date: End date "YYYY-MM-DD" (default: today)
        limit: Max results per page

    Returns:
        DataFrame with columns: [open, high, low, close, volume]
    """
    global _polygon_disabled_logged

    if not ENABLE_POLYGON:
        if not _polygon_disabled_logged:
            logger.info("Polygon.io disabled — set ENABLE_POLYGON=True and provide API key")
            _polygon_disabled_logged = True
        return pd.DataFrame()

    if POLYGON_API_KEY == "YOUR_POLYGON_KEY":
        logger.warning("Polygon.io API key not configured")
        return pd.DataFrame()

    from_date = from_date or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = to_date or datetime.now().strftime("%Y-%m-%d")

    url = (
        f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/"
        f"{multiplier}/{timespan}/{from_date}/{to_date}"
    )
    params = {"adjusted": "true", "sort": "asc", "limit": limit, "apiKey": POLYGON_API_KEY}

    logger.info(f"Fetching {symbol} from Polygon.io ({multiplier}{timespan})")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if "results" not in data:
        logger.error(f"Polygon.io returned no results: {data.get('error', data)}")
        return pd.DataFrame()

    df = pd.DataFrame(data["results"])
    df.rename(columns={
        "o": "open", "h": "high", "l": "low",
        "c": "close", "v": "volume", "t": "timestamp",
    }, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df = df[["open", "high", "low", "close", "volume"]]
    df.dropna(inplace=True)

    return df


# =========================================================================
#  Unified Fetcher
# =========================================================================

def fetch_data(
    symbol: str,
    timeframe: str = DEFAULT_TIMEFRAME,
    source: str = "yfinance",
    **kwargs,
) -> pd.DataFrame:
    """Unified data fetcher. Tries the requested source first, falls back.

    Args:
        symbol: Ticker symbol
        timeframe: Bar size key ("1m","5m","15m","1h","1d")
        source: Preferred data source ("yfinance", "alphavantage", "polygon")

    Returns:
        DataFrame with standard columns [open, high, low, close, volume]
    """
    fetchers = {
        "yfinance": fetch_yfinance,
        "alphavantage": fetch_alpha_vantage,
        "polygon": fetch_polygon,
    }

    fetcher = fetchers.get(source, fetch_yfinance)

    try:
        df = fetcher(symbol, timeframe=timeframe, **kwargs)
        if not df.empty:
            return df
    except Exception as e:
        logger.warning(f"Failed to fetch from {source}: {e}")

    # Fallback to yfinance if the chosen source failed
    if source != "yfinance":
        logger.info(f"Falling back to yfinance for {symbol}")
        return fetch_yfinance(symbol, timeframe=timeframe)

    return pd.DataFrame()


# Utility: symbol -> yfinance format
def get_yahoo_symbol(market: str, symbol: str) -> str:
    """Convert internal symbol to Yahoo Finance ticker format."""
    FUTURES_SUFFIX = {
        "ES": "ES=F",
        "NQ": "NQ=F",
        "CL": "CL=F",
        "GC": "GC=F",
    }
    FOREX_SUFFIX = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
    }

    if symbol in FUTURES_SUFFIX:
        return FUTURES_SUFFIX[symbol]
    elif symbol in FOREX_SUFFIX:
        return FOREX_SUFFIX[symbol]
    return symbol


# =========================================================================
#  Cache helpers
# =========================================================================

def cache_path(symbol: str, timeframe: str) -> Path:
    """Return filesystem cache path for (symbol, timeframe) data."""
    safe = symbol.replace("=", "_").replace("/", "_")
    return DATA_CACHE_DIR / f"{safe}_{timeframe}.parquet"


def load_cached_data(symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
    """Load cached data if it exists and is recent (< 1 hour old)."""
    path = cache_path(symbol, timeframe)
    if path.exists():
        age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
        if age < timedelta(hours=1):
            logger.debug(f"Loading cached data for {symbol} ({timeframe})")
            return pd.read_parquet(path)
        else:
            logger.debug(f"Cache expired for {symbol} ({timeframe})")
    return None


def save_cached_data(df: pd.DataFrame, symbol: str, timeframe: str) -> None:
    """Save DataFrame to cache."""
    path = cache_path(symbol, timeframe)
    df.to_parquet(path)
    logger.debug(f"Cached {symbol} ({timeframe}) — {len(df)} rows")