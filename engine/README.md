# Apex Algo Trading Engine

AI-powered automated trading system for futures and forex markets. Combines historical pattern recognition (Random Forest, Neural Networks) with real-time data feeds to make disciplined, emotion-free trades.

## Quick Start

```bash
chmod +x setup.sh && ./setup.sh
```

This single command:
- Checks Python 3.10+ is installed
- Creates an isolated virtual environment
- Installs all dependencies
- Copies `.env.example` → `.env` (edit it later for premium API keys)
- Runs the test suite to verify everything works

After setup, run the demo:

```bash
source venv/bin/activate
python demo.py
```

## Prerequisites

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Python | 3.10+ | [Download](https://www.python.org/downloads/) |
| pip | 23.0+ | Bundled with Python |
| OS | Linux, macOS, WSL2 | Windows native works but WSL2 recommended |
| Disk | ~2 GB | For venv + TensorFlow + data cache |

## Manual Setup

If you prefer to set up step by step:

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env to add API keys (optional — Yahoo Finance works for free)

# 4. Verify installation
python -m pytest tests/ -v
```

## Architecture

```
trading-engine/
├── config/
│   └── settings.py           # Global configuration & defaults
├── data/
│   ├── fetcher.py             # Data ingestion (yfinance, Alpha Vantage, Polygon.io)
│   └── processor.py           # Cleaning, normalization, feature engineering
├── models/
│   ├── random_forest.py       # Random Forest training & prediction
│   ├── neural_net.py          # Neural Network training & prediction
│   └── ensemble.py            # Ensemble model combining predictions
├── strategy/
│   ├── rules.py               # Explicit logical trading rules
│   └── signals.py             # Signal generation (ML predictions + rules)
├── backtest/
│   ├── engine.py              # Event-driven backtesting engine
│   └── metrics.py             # Performance metrics (Sharpe, drawdown, win rate)
├── paper_trading/
│   └── simulator.py           # Paper trading account simulator
├── live/
│   └── executor.py            # Live order execution stubs (NinjaTrader, QuantConnect)
├── tests/
│   ├── test_imports.py        # Import verification (11 tests)
│   └── test_integration.py    # Full integration suite (17 tests)
├── demo.py                    # End-to-end pipeline demo
├── setup.sh                   # One-command installer
├── requirements.txt           # Python dependencies
├── .env.example               # API key template
└── .gitignore
```

## Markets Supported

### Futures
| Symbol | Name               | Exchange | Tick Size | Point Value |
|--------|--------------------|----------|-----------|-------------|
| ES     | S&P 500 E-mini     | CME      | 0.25      | $50.00      |
| NQ     | Nasdaq 100 E-mini  | CME      | 0.25      | $20.00      |
| CL     | Crude Oil          | NYMEX    | 0.01      | $1,000.00   |
| GC     | Gold               | COMEX    | 0.10      | $100.00     |

### Forex
| Symbol | Name                 | Pip Size | Lot Size  |
|--------|----------------------|----------|-----------|
| EURUSD | Euro / US Dollar     | 0.0001   | 100,000   |
| GBPUSD | British Pound / USD  | 0.0001   | 100,000   |
| USDJPY | US Dollar / Yen      | 0.01     | 100,000   |

## Data Sources

| Source         | API Key Required | Default    | Notes                        |
|----------------|:----------------:|------------|------------------------------|
| Yahoo Finance  | No               | ✅ Enabled | Free, no signup required     |
| Alpha Vantage  | Yes              | ⏸ Disabled | Free tier: 25 req/day        |
| Polygon.io     | Yes              | ⏸ Disabled | Free tier: 5 req/min         |

### Enabling Premium Sources

1. Get an API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) or [Polygon.io](https://polygon.io/dashboard)
2. Add it to `.env`:
   ```
   ALPHA_VANTAGE_API_KEY=your_key_here
   POLYGON_API_KEY=your_key_here
   ```
3. Enable in `config/settings.py`:
   ```python
   ENABLE_ALPHA_VANTAGE = True
   ENABLE_POLYGON = True
   ```

## Configuration

Edit `config/settings.py` to customize:

```python
# Markets
DEFAULT_FUTURES = ["ES", "NQ"]      # Futures to trade
DEFAULT_FOREX = ["EURUSD"]           # Forex pairs to trade

# Trading hours (Eastern Time)
TRADING_HOURS = {"start": "09:30", "end": "16:00"}

# Risk management
MAX_POSITION_SIZE_PCT = 0.02         # Max 2% per trade
MAX_DAILY_DRAWDOWN_PCT = 0.05        # Stop if 5% down in a day
STOP_LOSS_ATR_MULTIPLIER = 2.0       # Stop-loss distance
TAKE_PROFIT_ATR_MULTIPLIER = 3.0     # Take-profit distance

# Model hyperparameters
RANDOM_FOREST_CONFIG = { ... }
NEURAL_NET_CONFIG = { ... }

# Backtest defaults
BACKTEST_CONFIG = {
    "initial_capital": 100_000.0,
    "commission": 2.50,
    "slippage_pct": 0.001,
}
```

## Usage

### Run the Demo (full pipeline)

```bash
source venv/bin/activate
python demo.py
```

Fetches S&P 500 futures data, engineers features, trains RF + NN models, runs a backtest, and prints a performance report.

### Programmatic Usage

```python
from trading_engine import *

# Fetch data
df = fetch_data("ES=F", timeframe="1d")

# Build features
featured = build_features(df)

# Train a model
rf = RandomForestModel()
rf.train(featured[feature_columns()], targets)

# Backtest
result = run_backtest(featured, ensemble=ensemble, symbol="ES")

# View metrics
metrics = compute_metrics(result)
print(f"Sharpe: {metrics['sharpe_ratio']:.3f}, Win Rate: {metrics['win_rate']:.1f}%")
```

### Run Tests

```bash
# All tests
python -m pytest tests/ -v

# Import verification only
python -m pytest tests/test_imports.py -v

# Integration tests only
python -m pytest tests/test_integration.py -v
```

## KPIs Tracked

| Metric              | Description                                  |
|---------------------|----------------------------------------------|
| Sharpe Ratio        | Risk-adjusted returns (annualized)           |
| Sortino Ratio       | Downside risk-adjusted returns               |
| Win Rate            | Percentage of profitable trades              |
| Profit Factor       | Gross profit / gross loss                    |
| Maximum Drawdown    | Peak-to-trough loss percentage               |
| Total Return        | Cumulative return on initial capital         |
| Avg Risk/Reward     | Average win size / average loss size         |
| Number of Trades    | Total trade count in period                  |

## Troubleshooting

### `ModuleNotFoundError: No module named 'tensorflow'`
TensorFlow can be finicky on some systems. Try:
```bash
pip uninstall tensorflow -y
pip install tensorflow
```
The engine falls back gracefully if TensorFlow isn't available — Random Forest and rule-based signals still work.

### `No data returned` from Yahoo Finance
Yahoo Finance occasionally rate-limits or changes their API. The demo falls back to synthetic data automatically. For production use, consider enabling Alpha Vantage or Polygon.io.

### `PermissionError` on setup.sh
```bash
chmod +x setup.sh
```

## License

Proprietary — Apex Algo Trading
