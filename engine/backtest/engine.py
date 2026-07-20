"""
Backtesting engine: simulates trading on historical data.

Executes trades based on signals, tracks positions, P&L, and
produces a detailed trade log.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd

from config.settings import BACKTEST_CONFIG
from data.processor import build_features
from models.ensemble import EnsembleModel
from strategy.signals import SignalGenerator, filter_trading_hours

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single completed trade."""
    entry_time: datetime
    exit_time: datetime
    symbol: str
    direction: int  # 1 = long, -1 = short
    entry_price: float
    exit_price: float
    quantity: float
    gross_pnl: float
    net_pnl: float
    commission: float
    exit_reason: str  # "signal", "stop_loss", "take_profit", "end_of_data"


@dataclass
class BacktestResult:
    """Results from a backtest run."""
    trades: list[Trade] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=pd.Series)
    signals_generated: int = 0
    total_return: float = 0.0
    total_commission: float = 0.0
    initial_capital: float = 0.0
    final_capital: float = 0.0


class BacktestEngine:
    """Event-driven backtesting engine.

    Walks through historical data bar by bar, generating signals,
    managing positions, and recording trades.
    """

    def __init__(
        self,
        initial_capital: float = None,
        commission: float = None,
        slippage_pct: float = None,
        stop_loss_atr_mult: Optional[float] = None,
        take_profit_atr_mult: Optional[float] = None,
    ):
        cfg = BACKTEST_CONFIG
        self.initial_capital = initial_capital or cfg["initial_capital"]
        self.commission = commission or cfg["commission"]
        self.slippage_pct = slippage_pct or cfg["slippage_pct"]
        self.stop_loss_atr = stop_loss_atr_mult
        self.take_profit_atr = take_profit_atr_mult

    def run(
        self,
        df: pd.DataFrame,
        signal_generator: SignalGenerator,
        symbol: str = "SYMBOL",
        filter_market_hours: bool = True,
    ) -> BacktestResult:
        """Run a backtest.

        Args:
            df: OHLCV DataFrame with features
            signal_generator: SignalGenerator instance
            symbol: Trading symbol (for logging)
            filter_market_hours: Whether to restrict to daytime hours

        Returns:
            BacktestResult with trades and equity curve
        """
        # Build features if not already present
        if "sma_5" not in df.columns:
            df = build_features(df)

        if filter_market_hours:
            df = filter_trading_hours(df)

        if df.empty:
            logger.warning("No data after filtering")
            return BacktestResult()

        # Generate signals
        signals = signal_generator.generate(df)

        # Execute
        result = self._execute(df, signals, symbol)
        return result

    def _execute(
        self,
        df: pd.DataFrame,
        signals: pd.Series,
        symbol: str,
    ) -> BacktestResult:
        """Walk through data, execute trades based on signals."""
        result = BacktestResult(initial_capital=self.initial_capital)
        result.final_capital = self.initial_capital

        cash = self.initial_capital
        position = 0  # current quantity
        position_dir = 0  # 1 long, -1 short, 0 flat
        entry_price = 0.0
        entry_time = None
        entry_signal_bar = 0

        equity = [self.initial_capital]
        timestamps = []

        for i in range(len(df)):
            row = df.iloc[i]
            ts = df.index[i]
            timestamps.append(ts)

            signal = signals.iloc[i] if i < len(signals) else 0
            signal = int(signal) if not pd.isna(signal) else 0

            # Existing position management
            if position != 0:
                # Check stop-loss / take-profit
                exit_reason = self._check_exit(row, entry_price, position_dir)
                if exit_reason:
                    # Close position
                    exit_price = self._apply_slippage(
                        row["close"], position_dir * -1
                    )
                    gross_pnl = self._calc_pnl(
                        entry_price, exit_price, position, position_dir
                    )
                    trade = Trade(
                        entry_time=entry_time,
                        exit_time=ts,
                        symbol=symbol,
                        direction=position_dir,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        quantity=position,
                        gross_pnl=gross_pnl,
                        net_pnl=gross_pnl - self.commission,
                        commission=self.commission,
                        exit_reason=exit_reason,
                    )
                    result.trades.append(trade)

                    cash += gross_pnl - self.commission
                    result.total_commission += self.commission
                    position = 0
                    position_dir = 0
                    entry_price = 0.0
                    entry_time = None

            # New signal
            if position == 0 and signal != 0:
                # Enter new position
                position_dir = signal
                entry_price = self._apply_slippage(row["close"], position_dir)
                position = self._calc_position_size(cash, entry_price)
                entry_time = ts
                entry_signal_bar = i
                result.signals_generated += 1

            # Record equity
            current_equity = cash
            if position != 0:
                unrealized = self._calc_pnl(
                    entry_price, row["close"], position, position_dir
                )
                current_equity += unrealized
            equity.append(current_equity)

        # Close any remaining position at end of data
        if position != 0:
            exit_price = df.iloc[-1]["close"]
            gross_pnl = self._calc_pnl(
                entry_price, exit_price, position, position_dir
            )
            trade = Trade(
                entry_time=entry_time,
                exit_time=df.index[-1],
                symbol=symbol,
                direction=position_dir,
                entry_price=entry_price,
                exit_price=exit_price,
                quantity=position,
                gross_pnl=gross_pnl,
                net_pnl=gross_pnl - self.commission,
                commission=self.commission,
                exit_reason="end_of_data",
            )
            result.trades.append(trade)
            cash += gross_pnl - self.commission
            result.total_commission += self.commission
            equity[-1] = cash

        result.final_capital = cash
        result.total_return = (cash / self.initial_capital - 1) * 100
        result.equity_curve = pd.Series(equity, index=[df.index[0]] + timestamps)

        logger.info(
            f"Backtest completed: {len(result.trades)} trades, "
            f"return={result.total_return:.2f}%, "
            f"final=${result.final_capital:.2f}"
        )

        return result

    def _apply_slippage(self, price: float, direction: int) -> float:
        """Apply slippage to execution price."""
        slippage = price * self.slippage_pct
        if direction == 1:  # Buy — pay more
            return price + slippage
        else:  # Sell — receive less
            return price - slippage

    def _calc_position_size(self, capital: float, price: float) -> float:
        """Calculate position size based on available capital."""
        from config.settings import MAX_POSITION_SIZE_PCT, MAX_LEVERAGE

        max_position_value = capital * MAX_POSITION_SIZE_PCT * MAX_LEVERAGE
        quantity = max_position_value / price
        return max(1, round(quantity))

    def _calc_pnl(
        self, entry_price: float, exit_price: float,
        quantity: float, direction: int,
    ) -> float:
        """Calculate profit/loss for a trade."""
        if direction == 1:  # Long
            return (exit_price - entry_price) * quantity
        else:  # Short
            return (entry_price - exit_price) * quantity

    def _check_exit(
        self, row: pd.Series, entry_price: float, direction: int,
    ) -> Optional[str]:
        """Check if stop-loss or take-profit triggered."""
        if self.stop_loss_atr is None and self.take_profit_atr is None:
            return None

        current_price = row["close"]
        atr = row.get("atr", None)

        if atr is None or pd.isna(atr) or atr == 0:
            return None

        if direction == 1:  # Long
            stop_price = entry_price - (atr * self.stop_loss_atr)
            target_price = entry_price + (atr * self.take_profit_atr)

            if current_price <= stop_price:
                return "stop_loss"
            if current_price >= target_price:
                return "take_profit"
        else:  # Short
            stop_price = entry_price + (atr * self.stop_loss_atr)
            target_price = entry_price - (atr * self.take_profit_atr)

            if current_price >= stop_price:
                return "stop_loss"
            if current_price <= target_price:
                return "take_profit"

        return None


# =========================================================================
#  Convenience runner
# =========================================================================

def run_backtest(
    df: pd.DataFrame,
    ensemble: Optional[EnsembleModel] = None,
    initial_capital: float = 100_000.0,
    commission: float = 2.50,
    symbol: str = "SYMBOL",
) -> BacktestResult:
    """Quick backtest runner.

    Builds a default signal generator and runs the engine.

    Args:
        df: OHLCV DataFrame
        ensemble: Optional trained EnsembleModel
        initial_capital: Starting capital
        commission: Commission per round-turn
        symbol: Symbol name

    Returns:
        BacktestResult
    """
    generator = SignalGenerator(
        ensemble=ensemble,
        rules_weight=0.3,
        ml_weight=0.7 if ensemble and ensemble.is_trained else 1.0,
    )

    engine = BacktestEngine(
        initial_capital=initial_capital,
        commission=commission,
        stop_loss_atr_mult=2.0,
        take_profit_atr_mult=3.0,
    )

    return engine.run(df, generator, symbol)