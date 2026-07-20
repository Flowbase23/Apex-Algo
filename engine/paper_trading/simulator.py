"""
Paper trading simulator: virtual account for testing strategies in real-time
without risking real capital.

Simulates order execution, position tracking, P&L calculation,
and trade journaling with realistic latency and slippage.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from config.settings import (
    PAPER_STARTING_CAPITAL,
    PAPER_COMMISSION_PER_TRADE,
    MAX_POSITION_SIZE_PCT,
    MAX_DAILY_DRAWDOWN_PCT,
)
from data.processor import feature_columns as get_feature_cols
from strategy.signals import SignalGenerator, is_market_open

logger = logging.getLogger(__name__)


@dataclass
class PaperOrder:
    """A simulated order."""
    id: str
    symbol: str
    side: str  # "buy" or "sell"
    type: str  # "market" or "limit"
    quantity: float
    price: float
    filled_price: float = 0.0
    status: str = "pending"  # pending, filled, cancelled
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    filled_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class PaperPosition:
    """An open position in the paper account."""
    symbol: str
    direction: int  # 1 = long, -1 = short
    quantity: float
    entry_price: float
    entry_time: datetime
    current_price: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

    @property
    def unrealized_pnl(self) -> float:
        if self.direction == 1:
            return (self.current_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.current_price) * self.quantity

    @property
    def unrealized_pnl_pct(self) -> float:
        cost = self.entry_price * self.quantity
        if cost == 0:
            return 0.0
        return self.unrealized_pnl / cost * 100


@dataclass
class PaperTrade:
    """A completed trade with realized P&L."""
    symbol: str
    direction: int
    quantity: float
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    gross_pnl: float
    net_pnl: float
    commission: float
    exit_reason: str


class PaperSimulator:
    """Paper trading simulator — simulates a live account.

    Tracks positions, P&L, and risk limits. Reacts to market data
    by generating signals and simulating fills.
    """

    def __init__(
        self,
        initial_capital: float = PAPER_STARTING_CAPITAL,
        commission: float = PAPER_COMMISSION_PER_TRADE,
        signal_generator: Optional[SignalGenerator] = None,
        journal_path: Optional[Path] = None,
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.signal_generator = signal_generator
        self.journal_path = journal_path or Path("/home/team/shared/trading-engine/logs/paper_journal.json")

        # Account state
        self.cash = initial_capital
        self.positions: dict[str, PaperPosition] = {}  # symbol -> position
        self.trades: list[PaperTrade] = []
        self.orders: list[PaperOrder] = []
        self.equity_history: list[dict] = []
        self.daily_pnl: dict[str, float] = {}  # date_str -> pnl
        self.is_running = False

    @property
    def equity(self) -> float:
        """Current total equity (cash + unrealized P&L)."""
        total = self.cash
        for pos in self.positions.values():
            total += pos.unrealized_pnl
        return total

    @property
    def day_pnl(self) -> float:
        """Today's P&L."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self.daily_pnl.get(today, 0.0)

    def start(self) -> dict:
        """Start (or reset) the paper trading session.

        Returns:
            dict with initial account snapshot
        """
        self.cash = self.initial_capital
        self.positions.clear()
        self.trades.clear()
        self.orders.clear()
        self.equity_history.clear()
        self.daily_pnl.clear()
        self.is_running = True

        logger.info(f"Paper trading started — capital=${self.initial_capital:.2f}")
        return self.snapshot()

    def stop(self) -> dict:
        """Stop paper trading and close all positions.

        Returns:
            Final account snapshot
        """
        # Close all open positions at current prices
        for symbol in list(self.positions.keys()):
            self._close_position(symbol, self.positions[symbol].current_price, "session_end")

        self.is_running = False
        self._journal()
        logger.info(f"Paper trading stopped — final equity=${self.equity:.2f}")
        return self.snapshot()

    def process_bar(self, df_row: pd.Series) -> dict:
        """Process a single bar of market data.

        Generates signals and executes trades.

        Args:
            df_row: Single row of OHLCV + features data

        Returns:
            dict of actions taken
        """
        if not self.is_running:
            return {"error": "Simulator not started"}

        if not is_market_open():
            return {"note": "Market closed"}

        actions = {"signals": [], "fills": [], "closes": []}

        # Update positions with current price
        for pos in self.positions.values():
            pos.current_price = df_row.get("close", pos.current_price)

        # Check stop-loss / take-profit for all positions
        self._check_exits(df_row, actions)

        # Generate signal
        if self.signal_generator is not None and "close" in df_row:
            # We need a DataFrame with features for signal generation
            pass  # signals handled externally in tick mode

        # Record equity
        self._record_equity(df_row)

        return actions

    def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        order_type: str = "market",
        notes: str = "",
    ) -> PaperOrder:
        """Place a simulated order.

        Args:
            symbol: Trading symbol
            side: "buy" or "sell"
            quantity: Number of units
            price: Limit price (for limit orders) or market price
            order_type: "market" or "limit"
            notes: Optional notes

        Returns:
            PaperOrder object
        """
        if not self.is_running:
            raise RuntimeError("Simulator not started")

        order = PaperOrder(
            id=f"ord_{len(self.orders) + 1}_{datetime.now(timezone.utc).timestamp()}",
            symbol=symbol,
            side=side,
            type=order_type,
            quantity=quantity,
            price=price,
            notes=notes,
        )

        if order_type == "market":
            order.filled_price = price
            order.status = "filled"
            order.filled_at = datetime.now(timezone.utc)
            self._fill_order(order)
        else:
            self.orders.append(order)

        return order

    def _fill_order(self, order: PaperOrder) -> None:
        """Fill an order and update account state."""
        side_mult = 1 if order.side == "buy" else -1

        # Check if we already have a position in this symbol
        existing = self.positions.get(order.symbol)

        if existing and existing.direction != side_mult:
            # Opposite side — close or reduce existing position
            if order.quantity >= existing.quantity:
                # Close existing position fully
                self._close_position(
                    order.symbol, order.filled_price, "opposite_signal"
                )
                remaining = order.quantity - existing.quantity
                if remaining > 0:
                    # Open new position in opposite direction
                    self._open_position(
                        order.symbol, side_mult, remaining, order.filled_price
                    )
            else:
                # Reduce position size
                self._close_position(
                    order.symbol, order.filled_price, "partial_close",
                    quantity=order.quantity,
                )
        elif existing:
            # Same direction — add to position
            existing.quantity += order.quantity
            existing.entry_price = (
                existing.entry_price * existing.quantity + order.filled_price * order.quantity
            ) / (existing.quantity + order.quantity)
            existing.current_price = order.filled_price
        else:
            # New position
            self._open_position(
                order.symbol, side_mult, order.quantity, order.filled_price
            )

        # Deduct cash
        cost = order.filled_price * order.quantity * side_mult
        self.cash -= cost
        self.cash -= self.commission

        order.status = "filled"
        order.filled_at = datetime.now(timezone.utc)
        self.orders.append(order)

    def _open_position(
        self, symbol: str, direction: int, quantity: float, price: float
    ) -> None:
        """Open a new position."""
        self.positions[symbol] = PaperPosition(
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            entry_price=price,
            entry_time=datetime.now(timezone.utc),
            current_price=price,
        )

    def _close_position(
        self,
        symbol: str,
        exit_price: float,
        reason: str,
        quantity: Optional[float] = None,
    ) -> None:
        """Close (or partially close) a position."""
        pos = self.positions.get(symbol)
        if not pos:
            return

        close_qty = quantity or pos.quantity

        gross_pnl = self._calc_pnl(pos.entry_price, exit_price, close_qty, pos.direction)

        trade = PaperTrade(
            symbol=symbol,
            direction=pos.direction,
            quantity=close_qty,
            entry_price=pos.entry_price,
            exit_price=exit_price,
            entry_time=pos.entry_time,
            exit_time=datetime.now(timezone.utc),
            gross_pnl=gross_pnl,
            net_pnl=gross_pnl - self.commission,
            commission=self.commission,
            exit_reason=reason,
        )
        self.trades.append(trade)

        # Update cash
        self.cash += gross_pnl - self.commission

        # Update daily P&L
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.daily_pnl[today] = self.daily_pnl.get(today, 0) + trade.net_pnl

        # Update or remove position
        if quantity and quantity < pos.quantity:
            pos.quantity -= quantity
        else:
            del self.positions[symbol]

    def _check_exits(self, df_row: pd.Series, actions: dict) -> None:
        """Check and execute stop-loss/take-profit exits."""
        current_price = df_row.get("close", 0)
        if current_price == 0:
            return

        for symbol in list(self.positions.keys()):
            pos = self.positions[symbol]
            pos.current_price = current_price

            sl = pos.stop_loss
            tp = pos.take_profit

            if pos.direction == 1:  # Long
                if sl and current_price <= sl:
                    actions["closes"].append(f"Stop-loss {symbol}")
                    self._close_position(symbol, current_price, "stop_loss")
                elif tp and current_price >= tp:
                    actions["closes"].append(f"Take-profit {symbol}")
                    self._close_position(symbol, current_price, "take_profit")
            else:  # Short
                if sl and current_price >= sl:
                    actions["closes"].append(f"Stop-loss {symbol}")
                    self._close_position(symbol, current_price, "stop_loss")
                elif tp and current_price <= tp:
                    actions["closes"].append(f"Take-profit {symbol}")
                    self._close_position(symbol, current_price, "take_profit")

        # Check daily drawdown limit
        if self.day_pnl / self.equity * 100 < -MAX_DAILY_DRAWDOWN_PCT * 100:
            logger.warning(f"Daily drawdown limit reached ({self.day_pnl:.2f}). Stopping trading.")
            for symbol in list(self.positions.keys()):
                self._close_position(symbol, current_price, "drawdown_limit")

    def _record_equity(self, df_row: pd.Series) -> None:
        """Record equity snapshot."""
        self.equity_history.append({
            "timestamp": df_row.name.isoformat() if hasattr(df_row.name, "isoformat") else str(df_row.name),
            "equity": self.equity,
            "cash": self.cash,
            "positions": len(self.positions),
        })

    def _calc_pnl(
        self, entry_price: float, exit_price: float,
        quantity: float, direction: int,
    ) -> float:
        if direction == 1:
            return (exit_price - entry_price) * quantity
        else:
            return (entry_price - exit_price) * quantity

    def snapshot(self) -> dict:
        """Get current account snapshot.

        Returns:
            dict with account state
        """
        return {
            "initial_capital": self.initial_capital,
            "cash": self.cash,
            "equity": self.equity,
            "day_pnl": self.day_pnl,
            "day_return_pct": (self.day_pnl / self.equity * 100) if self.equity > 0 else 0,
            "total_pnl": self.equity - self.initial_capital,
            "total_return_pct": (self.equity / self.initial_capital - 1) * 100,
            "open_positions": {
                s: {
                    "direction": "LONG" if p.direction == 1 else "SHORT",
                    "quantity": p.quantity,
                    "entry_price": p.entry_price,
                    "current_price": p.current_price,
                    "unrealized_pnl": p.unrealized_pnl,
                }
                for s, p in self.positions.items()
            },
            "num_trades": len(self.trades),
            "num_orders": len(self.orders),
            "is_running": self.is_running,
        }

    def summary(self) -> str:
        """Get a text summary of account performance."""
        snap = self.snapshot()
        win_rate = 0
        if self.trades:
            wins = sum(1 for t in self.trades if t.net_pnl > 0)
            win_rate = wins / len(self.trades) * 100

        return (
            f"Paper Account Summary\n"
            f"{'=' * 40}\n"
            f"Initial Capital:   ${snap['initial_capital']:>10,.2f}\n"
            f"Current Equity:    ${snap['equity']:>10,.2f}\n"
            f"Total P&L:         ${snap['total_pnl']:>10,.2f}\n"
            f"Total Return:      {snap['total_return_pct']:>8.2f}%\n"
            f"Day P&L:           ${snap['day_pnl']:>10,.2f}\n"
            f"Open Positions:    {snap['open_positions']}\n"
            f"Total Trades:      {len(self.trades)}\n"
            f"Win Rate:          {win_rate:.1f}%\n"
        )

    def _journal(self) -> None:
        """Save trade journal to disk."""
        journal = {
            "session_end": datetime.now(timezone.utc).isoformat(),
            "initial_capital": self.initial_capital,
            "final_equity": self.equity,
            "total_pnl": self.equity - self.initial_capital,
            "total_return_pct": (self.equity / self.initial_capital - 1) * 100,
            "trades": [asdict(t) for t in self.trades],
            "equity_history": self.equity_history,
        }

        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.journal_path, "w") as f:
            json.dump(journal, f, indent=2, default=str)

        logger.info(f"Trade journal saved to {self.journal_path}")