# Apex Algo Trading Engine

AI-powered automated trading system for futures and forex markets. Combines historical pattern recognition (Random Forest, Neural Networks) with real-time data feeds to make disciplined, emotion-free trades.

## System Requirements

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Python | 3.10+ | [Download](https://www.python.org/downloads/) |
| RAM | 8 GB | TensorFlow models use ~2-4 GB at runtime |
| Disk | 5 GB free | For dependencies, model checkpoints, data cache |
| OS | Linux, macOS, WSL2 | Windows native works but WSL2 recommended |
| pip | 23.0+ | Bundled with Python 3.10+ |

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Flowbase23/Apex-Algo.git
cd Apex-Algo/engine

# 2. One-command setup
chmod +x setup.sh && ./setup.sh

# 3. Activate and run the demo
source venv/bin/activate
python demo.py
```

This fetches real S&P 500 futures data, engineers 28 technical indicators, trains Random Forest + Neural Network models, runs a backtest, and prints a performance report.

## Configuration

All settings live in `config/settings.py` and can be overridden via environment variables in `.env`.

### Markets

```python
# config/settings.py
DEFAULT_FUTURES = ["ES", "NQ"]    # S&P 500, Nasdaq
DEFAULT_FOREX = ["EURUSD"]         # Euro/US Dollar
```

Available futures: ES (S&P 500 E-mini), NQ (Nasdaq 100), CL (Crude Oil), GC (Gold)
Available forex: EURUSD, GBPUSD, USDJPY

### Risk Management

```bash
# .env
MAX_POSITION_SIZE_PCT=0.02       # Max 2% per trade
MAX_DAILY_DRAWDOWN_PCT=0.05      # Stop trading after 5% daily loss
MAX_LEVERAGE=1.0                 # No leverage by default
STOP_LOSS_ATR_MULTIPLIER=2.0     # Stop-loss at 2× ATR
TAKE_PROFIT_ATR_MULTIPLIER=3.0   # Take-profit at 3× ATR
```

### Trading Hours

```python
TRADING_HOURS = {"start": "09:30", "end": "16:00"}  # Eastern Time
TRADING_TIMEZONE = "US/Eastern"
TRADING_DAYS = [0, 1, 2, 3, 4]                      # Monday–Friday
```

### Data Sources

| Source | API Key | Free Tier | Default |
|--------|:-------:|-----------|---------|
| Yahoo Finance | No | Unlimited | ✅ Enabled |
| Alpha Vantage | Yes | 25 req/day | ⏸ Disabled |
| Polygon.io | Yes | 5 req/min | ⏸ Disabled |

Enable premium sources in `.env`:

```bash
ALPHA_VANTAGE_API_KEY=your_key
POLYGON_API_KEY=your_key
```

Then flip the flags in `config/settings.py`:

```python
ENABLE_ALPHA_VANTAGE = True
ENABLE_POLYGON = True
```

## Connecting a Broker

The engine includes adapter stubs for two broker platforms. These are interface definitions ready for implementation once API keys and credentials are provided.

### NinjaTrader

```python
from live.executor import Executor, NinjaTraderAdapter

# Create a NinjaTrader-connected executor
adapter = NinjaTraderAdapter(host="localhost", port=36973)
adapter.connect()

executor = Executor(broker=adapter)
if executor.is_ready:
    # Place orders, manage positions, stream market data
    from live.executor import Order, OrderSide, OrderType
    order = Order(
        symbol="ES",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=1,
    )
    executor.submit(order)
```

**Prerequisites:**
- NinjaTrader 8 installed with AT Interface enabled
- API credentials configured in NinjaTrader's Options → AT Interface
- Firewall allows local TCP connections on the AT Interface port

### QuantConnect

```python
from live.executor import QuantConnectAdapter

adapter = QuantConnectAdapter(
    user_id="your_user_id",
    api_token="your_api_token",
)
adapter.connect()

executor = Executor(broker=adapter)
```

**Prerequisites:**
- QuantConnect account with live trading enabled
- API token from your QuantConnect dashboard
- Strategy model files uploaded to your QuantConnect project

## Paper Trading

The engine includes a full paper trading simulator for risk-free strategy testing.

```python
from paper_trading.simulator import PaperSimulator

# Start with $100,000 simulated account
sim = PaperSimulator(initial_capital=100_000)
sim.start()

# Place a simulated order
order = sim.place_order("ES", "buy", quantity=1, price=4500.0)
print(f"Order filled at ${order.filled_price:.2f}")

# Check positions and equity
snapshot = sim.snapshot()
print(f"Equity: ${snapshot['equity']:,.2f}")
print(f"Open positions: {len(snapshot['open_positions'])}")

# Run a backtest first to validate your strategy
from backtest.engine import run_backtest
from backtest.metrics import compute_metrics

result = run_backtest(featured_df, symbol="ES")
metrics = compute_metrics(result)
print(f"Sharpe: {metrics['sharpe_ratio']:.3f}, Win Rate: {metrics['win_rate']:.1f}%")
```

### Paper Trading Flow

1. **Backtest** — Validate the strategy on historical data
2. **Paper trade** — Run live market hours with simulated money
3. **Review metrics** — Check Sharpe, drawdown, win rate weekly
4. **Go live** — Connect a funded broker account when ready

## Going Live

When you're ready to trade real capital:

1. **Paper trade for at least 2 weeks** — Confirm strategy performance matches backtest expectations
2. **Start small** — Begin with 1 contract / mini lot and scale up gradually
3. **Monitor daily** — Check `MAX_DAILY_DRAWDOWN_PCT` in `.env` and adjust if needed
4. **Connect your broker** — Implement the NinjaTrader or QuantConnect adapter with your real credentials
5. **Never override risk limits** — The engine enforces position size and drawdown limits automatically

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
├── setup.py                   # pip-installable package
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
└── .gitignore
```

## Manual Setup

If you prefer step-by-step control:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .                # Install the engine as a package
cp .env.example .env            # Edit .env with your settings
python -m pytest tests/ -v      # Verify everything works
```

## Programmatic Usage

```python
from data.fetcher import fetch_yfinance
from data.processor import build_features, add_target, feature_columns
from models.random_forest import RandomForestModel
from backtest.engine import run_backtest
from backtest.metrics import compute_metrics

# Fetch data
df = fetch_yfinance("ES=F", timeframe="1d", period="2y")

# Engineer features
featured = build_features(df)

# Train model
cols = [c for c in feature_columns() if c in featured.columns]
rf = RandomForestModel()
rf.train(featured[cols], features["target"])

# Backtest
result = run_backtest(featured, symbol="ES")
metrics = compute_metrics(result)
print(f"Sharpe: {metrics['sharpe_ratio']:.3f} | Win Rate: {metrics['win_rate']:.1f}%")
```

## KPIs Tracked

| Metric | Description |
|--------|-------------|
| Sharpe Ratio | Risk-adjusted returns (annualized) |
| Sortino Ratio | Downside risk-adjusted returns |
| Win Rate | Percentage of profitable trades |
| Profit Factor | Gross profit ÷ gross loss |
| Maximum Drawdown | Peak-to-trough loss % |
| Total Return | Cumulative return on initial capital |
| Avg Risk/Reward | Average win size ÷ average loss size |

## FAQ

### Do I need an API key to get started?
No. Yahoo Finance is free and enabled by default — the demo runs out of the box.

### Does this trade real money automatically?
Not by default. The live executor has **stub adapters** — you must implement broker-specific authentication and order routing before any real trades execute.

### What markets can I trade?
Futures (ES, NQ, CL, GC) and forex (EUR/USD, GBP/USD, USD/JPY). Edit `DEFAULT_FUTURES` and `DEFAULT_FOREX` in `config/settings.py`.

### Can I use my own strategy rules?
Yes. Add custom rule functions in `strategy/rules.py` and they'll be automatically included in the signal generator. Or replace the ML models with your own in `models/`.

### What's the minimum account size?
The backtest default is $100,000. For futures, typical margin requirements suggest at least $10,000 for micros (MES/MNQ) and $50,000+ for minis (ES/NQ). Adjust `PAPER_STARTING_CAPITAL` in `.env`.

### How accurate are the backtests?
Realistic — the engine models commission ($2.50/round-turn), slippage (0.1%), and trading hours. It does NOT model market impact or liquidity gaps. Always paper trade before going live.

### How do I update the engine?
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
```

### TensorFlow fails to install
Try: `pip uninstall tensorflow -y && pip install tensorflow`. The engine falls back gracefully — Random Forest and rule-based signals work without TensorFlow.

## Troubleshooting

### `ModuleNotFoundError: No module named 'pandas'`
Run `source venv/bin/activate` first, then `pip install -r requirements.txt`.

### `No data returned` from Yahoo Finance
Yahoo Finance occasionally rate-limits. The demo falls back to synthetic data. For production, enable Alpha Vantage or Polygon.io.

### `PermissionError` on setup.sh
```bash
chmod +x setup.sh
```

## License

Proprietary — Apex Algo Trading
