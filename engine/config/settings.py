"""
Global configuration and defaults for the Apex Algo Trading Engine.

All settings can be overridden via environment variables or a local config file.
"""

import os
from pathlib import Path

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_CACHE_DIR = ROOT_DIR / "data_cache"
LOGS_DIR = ROOT_DIR / "logs"

# Ensure directories exist
DATA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# --- Trading Hours (daytime only by default) ---
TRADING_HOURS = {
    "start": "09:30",  # Eastern Time
    "end": "16:00",
}
TRADING_TIMEZONE = "US/Eastern"
TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday–Friday

# --- Markets ---
FUTURES_SYMBOLS = {
    "ES":  {"name": "S&P 500 E-mini",     "exchange": "CME",  "tick_size": 0.25,  "point_value": 50.0},
    "NQ":  {"name": "Nasdaq 100 E-mini",  "exchange": "CME",  "tick_size": 0.25,  "point_value": 20.0},
    "CL":  {"name": "Crude Oil",          "exchange": "NYMEX","tick_size": 0.01,  "point_value": 1000.0},
    "GC":  {"name": "Gold",               "exchange": "COMEX","tick_size": 0.10,  "point_value": 100.0},
}

FOREX_SYMBOLS = {
    "EURUSD": {"name": "Euro / US Dollar",    "pip_size": 0.0001, "lot_size": 100_000},
    "GBPUSD": {"name": "British Pound / USD", "pip_size": 0.0001, "lot_size": 100_000},
    "USDJPY": {"name": "US Dollar / Yen",     "pip_size": 0.01,   "lot_size": 100_000},
}

# Default symbols to trade
DEFAULT_FUTURES = ["ES", "NQ"]
DEFAULT_FOREX = ["EURUSD"]

# --- Data Sources ---
ENABLE_YFINANCE = True
ENABLE_ALPHA_VANTAGE = False
ENABLE_POLYGON = False

# Placeholder API keys — owner will fill these in
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "YOUR_ALPHA_VANTAGE_KEY")
POLYGON_API_KEY = os.environ.get("POLYGON_API_KEY", "YOUR_POLYGON_KEY")

# Default timeframe for analysis
TIMEFRAMES = {
    "1m":  {"interval": "1m",  "period": "7d"},
    "5m":  {"interval": "5m",  "period": "30d"},
    "15m": {"interval": "15m", "period": "60d"},
    "1h":  {"interval": "60m", "period": "6mo"},
    "1d":  {"interval": "1d",  "period": "2y"},
}
DEFAULT_TIMEFRAME = "1h"

# --- Risk Management ---
# Override via .env: MAX_POSITION_SIZE_PCT, MAX_DAILY_DRAWDOWN_PCT, etc.
MAX_POSITION_SIZE_PCT = float(
    os.environ.get("MAX_POSITION_SIZE_PCT", "0.02")
)  # Max % of capital per trade
MAX_DAILY_DRAWDOWN_PCT = float(
    os.environ.get("MAX_DAILY_DRAWDOWN_PCT", "0.05")
)  # Stop trading if daily drawdown exceeds this
MAX_LEVERAGE = float(
    os.environ.get("MAX_LEVERAGE", "1.0")
)  # No leverage by default (set >1 for margin)
STOP_LOSS_ATR_MULTIPLIER = float(
    os.environ.get("STOP_LOSS_ATR_MULTIPLIER", "2.0")
)  # Stop-loss as multiple of ATR
TAKE_PROFIT_ATR_MULTIPLIER = float(
    os.environ.get("TAKE_PROFIT_ATR_MULTIPLIER", "3.0")
)  # Take-profit as multiple of ATR

# --- Paper Trading ---
PAPER_STARTING_CAPITAL = float(
    os.environ.get("PAPER_STARTING_CAPITAL", "100000")
)  # Simulated account size
PAPER_COMMISSION_PER_TRADE = float(
    os.environ.get("PAPER_COMMISSION_PER_TRADE", "2.50")
)  # Per round-turn commission

# --- Model Hyperparameters ---
RANDOM_FOREST_CONFIG = {
    "n_estimators": 200,
    "max_depth": 10,
    "min_samples_split": 20,
    "min_samples_leaf": 10,
    "random_state": 42,
    "n_jobs": -1,
}

NEURAL_NET_CONFIG = {
    "hidden_layers": [64, 32, 16],
    "dropout_rate": 0.2,
    "learning_rate": 0.001,
    "batch_size": 32,
    "epochs": 50,
    "validation_split": 0.2,
    "random_state": 42,
}

# --- Backtest Defaults ---
BACKTEST_CONFIG = {
    "initial_capital": 100_000.0,
    "commission": 2.50,
    "slippage_pct": 0.001,  # 0.1% slippage per trade
}


def get_enabled_symbols():
    """Return full list of enabled symbols across all markets."""
    return DEFAULT_FUTURES + DEFAULT_FOREX