"""
Apex Algo Trading Engine

AI-powered trading system for futures and forex markets.
"""

from config.settings import (
    FUTURES_SYMBOLS,
    FOREX_SYMBOLS,
    DEFAULT_FUTURES,
    DEFAULT_FOREX,
)

from data.fetcher import (
    fetch_data,
    fetch_yfinance,
    fetch_alpha_vantage,
    fetch_polygon,
    get_yahoo_symbol,
)

from data.processor import (
    build_features,
    clean_ohlcv,
    feature_columns,
)

from models.random_forest import RandomForestModel
from models.neural_net import NeuralNetworkModel
from models.ensemble import EnsembleModel

from strategy.rules import (
    compute_rule_signals,
    BUY, SELL, NEUTRAL,
    STRONG_BUY, STRONG_SELL,
)

from strategy.signals import (
    SignalGenerator,
    is_market_open,
    filter_trading_hours,
)

from backtest.engine import (
    BacktestEngine,
    BacktestResult,
    Trade,
    run_backtest,
)

from backtest.metrics import (
    compute_metrics,
    print_report,
)

from paper_trading.simulator import PaperSimulator

from live.executor import (
    Executor,
    NinjaTraderAdapter,
    QuantConnectAdapter,
    Order,
    OrderSide,
    OrderType,
)

__all__ = [
    # Config
    "FUTURES_SYMBOLS",
    "FOREX_SYMBOLS",
    "DEFAULT_FUTURES",
    "DEFAULT_FOREX",

    # Data
    "fetch_data",
    "fetch_yfinance",
    "fetch_alpha_vantage",
    "fetch_polygon",
    "get_yahoo_symbol",
    "build_features",
    "clean_ohlcv",
    "feature_columns",

    # Models
    "RandomForestModel",
    "NeuralNetworkModel",
    "EnsembleModel",

    # Strategy
    "compute_rule_signals",
    "SignalGenerator",
    "is_market_open",
    "filter_trading_hours",
    "BUY", "SELL", "NEUTRAL",
    "STRONG_BUY", "STRONG_SELL",

    # Backtest
    "BacktestEngine",
    "BacktestResult",
    "Trade",
    "run_backtest",
    "compute_metrics",
    "print_report",

    # Paper Trading
    "PaperSimulator",

    # Live
    "Executor",
    "NinjaTraderAdapter",
    "QuantConnectAdapter",
    "Order",
    "OrderSide",
    "OrderType",
]