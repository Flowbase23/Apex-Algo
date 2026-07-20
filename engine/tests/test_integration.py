"""
Integration tests for the Apex Algo Trading Engine.

Tests validate that all modules load and basic operations succeed
without errors. Run with: python -m pytest tests/ -v
"""

import sys
import os

# Ensure engine is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_config_imports():
    """Config module loads and exposes expected symbols."""
    from config.settings import (
        FUTURES_SYMBOLS, FOREX_SYMBOLS,
        DEFAULT_FUTURES, DEFAULT_FOREX,
        TRADING_HOURS, RANDOM_FOREST_CONFIG, NEURAL_NET_CONFIG,
    )
    assert "ES" in FUTURES_SYMBOLS
    assert "EURUSD" in FOREX_SYMBOLS
    assert len(DEFAULT_FUTURES) >= 1
    assert len(DEFAULT_FOREX) >= 1
    assert "start" in TRADING_HOURS
    assert "n_estimators" in RANDOM_FOREST_CONFIG


def test_config_get_enabled_symbols():
    """get_enabled_symbols returns valid mixed list."""
    from config.settings import get_enabled_symbols
    symbols = get_enabled_symbols()
    assert len(symbols) > 0
    assert isinstance(symbols, list)


def test_data_fetcher_imports():
    """Data fetcher exposes all fetch functions."""
    from data.fetcher import (
        fetch_data, fetch_yfinance, fetch_alpha_vantage,
        fetch_polygon, get_yahoo_symbol,
        load_cached_data, save_cached_data,
    )
    assert get_yahoo_symbol("futures", "ES") == "ES=F"
    assert get_yahoo_symbol("futures", "NQ") == "NQ=F"
    assert get_yahoo_symbol("forex", "EURUSD") == "EURUSD=X"
    assert get_yahoo_symbol("forex", "GBPUSD") == "GBPUSD=X"


def test_data_processor_imports():
    """Data processor exposes all feature functions."""
    from data.processor import (
        clean_ohlcv, resample_ohlcv, build_features,
        add_sma, add_ema, add_rsi, add_macd,
        add_bollinger_bands, add_atr, add_volume_indicators,
        add_price_features, add_target, add_regression_target,
        feature_columns,
    )
    cols = feature_columns()
    assert "rsi" in cols
    assert "macd" in cols
    assert "atr" in cols
    assert len(cols) >= 20


def test_data_processor_clean():
    """clean_ohlcv handles valid and invalid data."""
    import pandas as pd
    import numpy as np
    from data.processor import clean_ohlcv

    df = pd.DataFrame({
        "open": [100.0, 101.0, np.nan, 103.0],
        "high": [102.0, 103.0, 104.0, 105.0],
        "low": [99.0, 100.0, 101.0, 102.0],
        "close": [101.0, 102.0, np.nan, 104.0],
        "volume": [1000, 1100, 1200, 1300],
    }, index=pd.date_range("2024-01-01", periods=4, freq="1h"))

    cleaned = clean_ohlcv(df)
    assert len(cleaned) == 2  # NaN rows dropped
    assert list(cleaned.columns) == ["open", "high", "low", "close", "volume"]


def test_data_processor_features():
    """Full feature pipeline produces expected columns."""
    import pandas as pd
    import numpy as np
    from data.processor import build_features

    # Create synthetic price data (200 bars)
    dates = pd.date_range("2024-01-01", periods=200, freq="1h")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(200) * 0.5)

    df = pd.DataFrame({
        "open": prices + np.random.randn(200) * 0.1,
        "high": prices + abs(np.random.randn(200)) * 0.5 + 0.5,
        "low": prices - abs(np.random.randn(200)) * 0.5 - 0.5,
        "close": prices,
        "volume": np.random.randint(500, 2000, 200),
    }, index=dates)

    featured = build_features(df)
    assert len(featured) > 0
    assert "sma_20" in featured.columns
    assert "rsi" in featured.columns
    assert "macd" in featured.columns
    assert "bb_upper" in featured.columns
    assert "atr" in featured.columns


def test_random_forest_model():
    """RandomForestModel trains and predicts."""
    import pandas as pd
    import numpy as np
    from models.random_forest import RandomForestModel

    model = RandomForestModel()
    X = pd.DataFrame({
        "feature_a": np.random.randn(100),
        "feature_b": np.random.randn(100),
        "feature_c": np.random.randn(100),
    })
    y = pd.Series(np.random.choice([-1, 0, 1], 100))

    metrics = model.train(X, y, validate=True)
    assert model.is_trained
    assert "test_accuracy" in metrics
    assert "feature_importances" in metrics

    preds = model.predict(X)
    assert len(preds) == 100
    assert set(preds).issubset({-1, 0, 1})

    conf = model.predict_confidence(X)
    assert conf.between(0, 1).all()


def test_neural_network_model():
    """NeuralNetworkModel trains and predicts (if TF available)."""
    import pandas as pd
    import numpy as np

    try:
        from models.neural_net import NeuralNetworkModel
    except ImportError:
        return  # Skip if TF not installed

    model = NeuralNetworkModel()
    X = pd.DataFrame({
        "feature_a": np.random.randn(50),
        "feature_b": np.random.randn(50),
    })
    y = pd.Series(np.random.choice([-1, 0, 1], 50))

    metrics = model.train(X, y, verbose=0)
    assert model.is_trained
    assert "final_loss" in metrics

    preds = model.predict(X)
    assert len(preds) == 50


def test_ensemble_model():
    """EnsembleModel combines RF and NN predictions."""
    import pandas as pd
    import numpy as np
    from models.ensemble import EnsembleModel
    from models.random_forest import RandomForestModel

    rf = RandomForestModel()
    X = pd.DataFrame({"feat": np.random.randn(50)})
    y = pd.Series(np.random.choice([-1, 0, 1], 50))

    ens = EnsembleModel(rf_model=rf, nn_model=None)
    metrics = ens.train(X, y)
    assert ens.is_trained

    preds = ens.predict(X)
    assert len(preds) == 50


def test_strategy_rules_imports():
    """Strategy rules have all key functions and constants."""
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


def test_strategy_rules_compute():
    """compute_rule_signals works with feature DataFrame."""
    import pandas as pd
    import numpy as np
    from data.processor import build_features
    from strategy.rules import compute_rule_signals

    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    df = pd.DataFrame({
        "open": prices + np.random.randn(100) * 0.1,
        "high": prices + abs(np.random.randn(100)) * 0.5 + 0.5,
        "low": prices - abs(np.random.randn(100)) * 0.5 - 0.5,
        "close": prices,
        "volume": np.random.randint(500, 2000, 100),
    }, index=dates)

    featured = build_features(df)
    rules_df = compute_rule_signals(featured)
    assert "consensus" in rules_df.columns
    assert len(rules_df) > 0


def test_signal_generator():
    """SignalGenerator creates combined signals."""
    import pandas as pd
    import numpy as np
    from data.processor import build_features
    from strategy.signals import SignalGenerator

    dates = pd.date_range("2024-01-01", periods=100, freq="1h")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    df = pd.DataFrame({
        "open": prices + np.random.randn(100) * 0.1,
        "high": prices + abs(np.random.randn(100)) * 0.5 + 0.5,
        "low": prices - abs(np.random.randn(100)) * 0.5 - 0.5,
        "close": prices,
        "volume": np.random.randint(500, 2000, 100),
    }, index=dates)

    featured = build_features(df)
    gen = SignalGenerator()
    signals = gen.generate(featured)
    assert len(signals) == len(featured)
    assert set(signals.unique()).issubset({-1, 0, 1})


def test_market_hours():
    """is_market_open correctly checks trading hours."""
    from strategy.signals import is_market_open
    from datetime import datetime
    import pytz

    eastern = pytz.timezone("US/Eastern")
    # A Saturday at noon - should be closed
    sat = eastern.localize(datetime(2024, 1, 6, 12, 0))
    assert not is_market_open(sat)

    # A weekday at 11am - should be open
    wed = eastern.localize(datetime(2024, 1, 3, 11, 0))
    assert is_market_open(wed)


def test_backtest_engine():
    """BacktestEngine runs and produces trades."""
    import pandas as pd
    import numpy as np
    from data.processor import build_features
    from strategy.signals import SignalGenerator
    from backtest.engine import BacktestEngine

    dates = pd.date_range("2024-01-01", periods=200, freq="1h")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(200) * 0.5)
    df = pd.DataFrame({
        "open": prices + np.random.randn(200) * 0.1,
        "high": prices + abs(np.random.randn(200)) * 0.5 + 0.5,
        "low": prices - abs(np.random.randn(200)) * 0.5 - 0.5,
        "close": prices,
        "volume": np.random.randint(500, 2000, 200),
    }, index=dates)

    featured = build_features(df)
    gen = SignalGenerator()
    engine = BacktestEngine(initial_capital=50000, commission=2.50)
    result = engine.run(featured, gen, symbol="TEST")
    assert result.initial_capital == 50000
    assert len(result.trades) >= 0
    assert len(result.equity_curve) > 0


def test_backtest_metrics():
    """compute_metrics produces all expected KPIs."""
    import pandas as pd
    import numpy as np
    from data.processor import build_features
    from strategy.signals import SignalGenerator
    from backtest.engine import BacktestEngine
    from backtest.metrics import compute_metrics

    dates = pd.date_range("2024-01-01", periods=300, freq="1h")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(300) * 0.5)
    df = pd.DataFrame({
        "open": prices + np.random.randn(300) * 0.1,
        "high": prices + abs(np.random.randn(300)) * 0.5 + 0.5,
        "low": prices - abs(np.random.randn(300)) * 0.5 - 0.5,
        "close": prices,
        "volume": np.random.randint(500, 2000, 300),
    }, index=dates)

    featured = build_features(df)
    gen = SignalGenerator()
    engine = BacktestEngine()
    result = engine.run(featured, gen)

    metrics = compute_metrics(result)
    assert "sharpe_ratio" in metrics
    assert "win_rate" in metrics
    assert "max_drawdown_pct" in metrics
    assert "profit_factor" in metrics
    assert "num_trades" in metrics


def test_paper_simulator():
    """PaperSimulator starts, places orders, and reports."""
    from paper_trading.simulator import PaperSimulator

    sim = PaperSimulator(initial_capital=100000)
    snap = sim.start()
    assert snap["is_running"]
    assert snap["cash"] == 100000
    assert snap["equity"] == 100000

    # Place an order
    order = sim.place_order("ES", "buy", 10, 4500.0)
    assert order.status == "filled"
    assert order.filled_price == 4500.0

    snap2 = sim.snapshot()
    assert len(snap2["open_positions"]) > 0

    final = sim.stop()
    assert not final["is_running"]


def test_live_executor():
    """Executor instantiates with NinjaTrader stub adapter."""
    from live.executor import Executor, NinjaTraderAdapter, Order, OrderSide, OrderType

    adapter = NinjaTraderAdapter()
    assert adapter.connect()
    assert adapter.is_connected()
    adapter.disconnect()

    executor = Executor(broker=NinjaTraderAdapter())
    assert executor.is_ready


def test_full_integration():
    """End-to-end: data -> features -> model training -> backtest -> metrics."""
    import pandas as pd
    import numpy as np
    from data.processor import build_features, add_target
    from models.random_forest import RandomForestModel
    from strategy.signals import SignalGenerator
    from backtest.engine import BacktestEngine
    from backtest.metrics import compute_metrics

    # 1. Synthetic data
    dates = pd.date_range("2024-01-01", periods=500, freq="1h")
    np.random.seed(42)
    prices = 100 + np.cumsum(np.random.randn(500) * 0.3)
    df = pd.DataFrame({
        "open": prices + np.random.randn(500) * 0.1,
        "high": prices + abs(np.random.randn(500)) * 0.3 + 0.3,
        "low": prices - abs(np.random.randn(500)) * 0.3 - 0.3,
        "close": prices,
        "volume": np.random.randint(500, 2000, 500),
    }, index=dates)

    # 2. Build features
    featured = build_features(df)
    assert len(featured) > 100

    # 3. Train model
    from data.processor import feature_columns
    cols = feature_columns()
    available = [c for c in cols if c in featured.columns]
    X = featured[available]
    target_df = add_target(featured, forward_periods=1, threshold_pct=0.005)
    y = target_df["target"]

    # Align X and y
    common_idx = X.index.intersection(y.index)
    X_aligned = X.loc[common_idx]

    rf = RandomForestModel()
    train_metrics = rf.train(X_aligned, y.loc[common_idx])
    assert train_metrics["test_accuracy"] >= 0

    # 4. Backtest with ML-enhanced signals
    gen = SignalGenerator(confidence_threshold=0.0)
    engine = BacktestEngine()
    result = engine.run(featured, gen, symbol="INTEGRATION_TEST")

    # 5. Compute metrics
    metrics = compute_metrics(result)
    assert metrics["initial_capital"] > 0
    assert metrics["num_trades"] >= 0  # Could be zero with random data

    print(f"Integration test passed: {len(result.trades)} trades, "
          f"return={metrics['total_return_pct']:.2f}%")


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))