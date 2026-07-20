"""
Import verification tests for the Apex Algo Trading Engine.

Verifies:
  - Every module imports without error
  - Key classes instantiate correctly
  - A tiny backtest (100 rows) runs without crashing

Usage:
    cd /home/team/shared/trading-engine
    ../venv/bin/python -m pytest tests/test_imports.py -v
"""

import sys
import os
import warnings

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_config():
    """Config imports and exposes expected symbols."""
    from config.settings import (
        FUTURES_SYMBOLS, FOREX_SYMBOLS, DEFAULT_FUTURES, DEFAULT_FOREX,
        TRADING_HOURS, TRADING_TIMEZONE, RANDOM_FOREST_CONFIG,
        NEURAL_NET_CONFIG, BACKTEST_CONFIG, get_enabled_symbols,
    )
    assert "ES" in FUTURES_SYMBOLS
    assert "EURUSD" in FOREX_SYMBOLS
    assert "ES" in DEFAULT_FUTURES
    assert "EURUSD" in DEFAULT_FOREX
    assert TRADING_TIMEZONE == "US/Eastern"
    assert "n_estimators" in RANDOM_FOREST_CONFIG
    assert len(get_enabled_symbols()) >= 2


def test_data_fetcher():
    """Data fetcher imports and converts symbols."""
    from data.fetcher import (
        fetch_data, fetch_yfinance, fetch_alpha_vantage,
        fetch_polygon, get_yahoo_symbol,
        load_cached_data, save_cached_data,
    )
    assert get_yahoo_symbol("futures", "ES") == "ES=F"
    assert get_yahoo_symbol("futures", "NQ") == "NQ=F"
    assert get_yahoo_symbol("forex", "EURUSD") == "EURUSD=X"
    assert get_yahoo_symbol("forex", "USDJPY") == "USDJPY=X"
    assert get_yahoo_symbol("futures", "CL") == "CL=F"
    assert get_yahoo_symbol("futures", "GC") == "GC=F"


def test_data_processor():
    """Data processor imports and builds features."""
    from data.processor import (
        clean_ohlcv, resample_ohlcv, build_features,
        add_sma, add_ema, add_rsi, add_macd,
        add_bollinger_bands, add_atr,
        add_volume_indicators, add_price_features,
        add_target, add_regression_target,
        feature_columns,
    )
    cols = feature_columns()
    required = ["rsi", "macd", "atr", "sma_20", "ema_12", "bb_upper"]
    for r in required:
        assert r in cols, f"Missing feature: {r}"
    assert len(cols) >= 25, f"Expected >=25 features, got {len(cols)}"


def test_models():
    """All model classes import and instantiate."""
    from models.random_forest import RandomForestModel
    from models.neural_net import NeuralNetworkModel
    from models.ensemble import EnsembleModel

    rf = RandomForestModel()
    assert rf is not None
    assert not rf.is_trained

    nn = NeuralNetworkModel()
    assert nn is not None
    assert not nn.is_trained

    ens = EnsembleModel(rf_model=rf, nn_model=nn)
    assert ens is not None
    assert not ens.is_trained


def test_strategy_rules():
    """Strategy rules import all constants and functions."""
    from strategy.rules import (
        BUY, SELL, NEUTRAL, STRONG_BUY, STRONG_SELL,
        compute_rule_signals,
        rsi_overbought_oversold, ema_crossover,
        macd_signal_cross, bollinger_breakout,
        sma_trend, volume_breakout, price_momentum,
    )
    assert BUY == 1
    assert SELL == -1
    assert NEUTRAL == 0
    assert STRONG_BUY == 2
    assert STRONG_SELL == -2


def test_signal_generator():
    """SignalGenerator instantiates and generates signals."""
    from strategy.signals import SignalGenerator, is_market_open, filter_trading_hours

    gen = SignalGenerator()
    assert gen.rules_weight == 0.3
    assert gen.ml_weight == 0.7

    # Market hours check
    from datetime import datetime
    import pytz
    eastern = pytz.timezone("US/Eastern")
    sat = eastern.localize(datetime(2024, 1, 6, 12, 0))
    assert not is_market_open(sat)
    wed = eastern.localize(datetime(2024, 1, 3, 11, 0))
    assert is_market_open(wed)


def test_backtest():
    """Backtest engine + metrics import and instantiate."""
    from backtest.engine import BacktestEngine, BacktestResult, Trade, run_backtest
    from backtest.metrics import compute_metrics, print_report, metrics_to_dataframe

    engine = BacktestEngine(initial_capital=100_000, commission=2.50)
    assert engine.initial_capital == 100_000


def test_paper_trading():
    """PaperSimulator imports and instantiates."""
    from paper_trading.simulator import PaperSimulator, PaperOrder, PaperTrade, PaperPosition

    sim = PaperSimulator(initial_capital=50_000)
    assert sim.initial_capital == 50_000
    assert sim.cash == 50_000


def test_live_executor():
    """Live executor + broker adapters import."""
    from live.executor import (
        Executor, NinjaTraderAdapter, QuantConnectAdapter,
        Order, OrderSide, OrderType, OrderStatus,
    )
    adapter = NinjaTraderAdapter()
    assert adapter.is_connected()

    executor = Executor(broker=NinjaTraderAdapter())
    assert executor.is_ready


def test_tiny_backtest_pipeline():
    """Full pipeline on 100 rows of synthetic data — must not crash."""
    import numpy as np
    import pandas as pd
    from data.processor import build_features, add_target
    from models.random_forest import RandomForestModel
    from strategy.signals import SignalGenerator
    from backtest.engine import BacktestEngine, run_backtest
    from backtest.metrics import compute_metrics

    # Generate synthetic data (need 500+ to survive SMA(200) + other indicators)
    np.random.seed(1)
    n_bars = 500
    dates = pd.date_range("2024-01-01", periods=n_bars, freq="D")
    prices = 4000 + np.cumsum(np.random.randn(n_bars) * 20)

    df = pd.DataFrame({
        "open": prices * (1 + np.random.randn(n_bars) * 0.002),
        "high": prices * (1 + abs(np.random.randn(n_bars)) * 0.008 + 0.004),
        "low": prices * (1 - abs(np.random.randn(n_bars)) * 0.008 - 0.004),
        "close": prices,
        "volume": np.random.randint(800_000, 2_500_000, n_bars),
    }, index=dates)

    # Feature engineering
    featured = build_features(df)
    assert len(featured) > 0, f"build_features returned empty with {n_bars} bars"

    # Backtest with rules
    gen = SignalGenerator()
    result = run_backtest(featured, initial_capital=100_000, symbol="TEST")
    assert result.initial_capital == 100_000

    # Metrics
    metrics = compute_metrics(result)
    assert "sharpe_ratio" in metrics
    assert "win_rate" in metrics
    assert "max_drawdown_pct" in metrics
    assert "total_return_pct" in metrics
    assert "num_trades" in metrics

    # Verify no crash for any metric value
    print(f"  Tiny backtest done: {metrics['num_trades']} trades, "
          f"return={metrics['total_return_pct']:.2f}%, "
          f"Sharpe={metrics['sharpe_ratio']:.3f}")


def test_all_symbols():
    """All configured futures and forex symbols are valid."""
    from config.settings import FUTURES_SYMBOLS, FOREX_SYMBOLS, DEFAULT_FUTURES, DEFAULT_FOREX
    from data.fetcher import get_yahoo_symbol

    for sym in DEFAULT_FUTURES:
        yh = get_yahoo_symbol("futures", sym)
        assert "=" in yh, f"Bad yahoo symbol for {sym}: {yh}"

    for sym in DEFAULT_FOREX:
        yh = get_yahoo_symbol("forex", sym)
        assert "=" in yh, f"Bad yahoo symbol for {sym}: {yh}"


if __name__ == "__main__":
    # Run all tests manually
    test_config()
    print("✓ test_config")
    test_data_fetcher()
    print("✓ test_data_fetcher")
    test_data_processor()
    print("✓ test_data_processor")
    test_models()
    print("✓ test_models")
    test_strategy_rules()
    print("✓ test_strategy_rules")
    test_signal_generator()
    print("✓ test_signal_generator")
    test_backtest()
    print("✓ test_backtest")
    test_paper_trading()
    print("✓ test_paper_trading")
    test_live_executor()
    print("✓ test_live_executor")
    test_all_symbols()
    print("✓ test_all_symbols")
    test_tiny_backtest_pipeline()
    print("✓ test_tiny_backtest_pipeline")
    print("\nAll 11 import tests passed!")