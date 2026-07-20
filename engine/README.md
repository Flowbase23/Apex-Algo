# Apex Algo Trading Engine

AI-powered automated trading system for futures and forex markets. Combines historical pattern recognition (Random Forest, Neural Networks) with real-time data feeds to make disciplined, emotion-free trades.

## Architecture

```
trading-engine/
├── config/settings.py       # Global configuration & defaults
├── data/
│   ├── fetcher.py           # Data ingestion (yfinance, Alpha Vantage, Polygon.io)
│   └── processor.py         # Cleaning, normalization, feature engineering
├── models/
│   ├── random_forest.py     # Random Forest training & prediction
│   ├── neural_net.py        # Neural Network training & prediction
│   └── ensemble.py          # Ensemble model combining predictions
├── strategy/
│   ├── rules.py             # Explicit logical trading rules
│   └── signals.py           # Signal generation (ML predictions + rules)
├── backtest/
│   ├── engine.py            # Backtesting engine
│   └── metrics.py           # Performance metrics (Sharpe, drawdown, win rate)
├── paper_trading/
│   └── simulator.py         # Paper trading account simulator
└── live/
    └── executor.py          # Live order execution stub/interface
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run a backtest
python -m trading_engine.backtest.engine --config config/settings.py

# Run paper trading
python -m trading_engine.paper_trading.simulator
```

## Markets Supported

- **Futures:** ES (S&P 500 E-mini), NQ (Nasdaq 100 E-mini), CL (Crude Oil), GC (Gold)
- **Forex:** EUR/USD, GBP/USD, USD/JPY

## Data Sources

| Source       | API Key Required | Default |
|-------------|-----------------|---------|
| Yahoo Finance | No             | ✅ Enabled |
| Alpha Vantage | Yes (placeholder) | ⏸ Disabled |
| Polygon.io    | Yes (placeholder) | ⏸ Disabled |

## Configuration

Edit `config/settings.py` to set:
- Market symbols and timeframes
- API keys for premium data sources
- Model hyperparameters
- Risk management limits
- Trading hours (daytime only by default)

## KPIs Tracked

- Sharpe Ratio (risk-adjusted returns)
- Win Rate & Avg Risk/Reward per trade
- Maximum Drawdown (peak-to-trough loss)
- Total Return & Number of Trades

## License

Proprietary — Apex Algo Trading