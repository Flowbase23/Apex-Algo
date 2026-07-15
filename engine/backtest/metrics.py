"""
Performance metrics for backtest evaluation.

Computes standard trading KPIs:
  - Sharpe Ratio
  - Win Rate
  - Avg Risk/Reward
  - Maximum Drawdown
  - Total Return
  - Number of Trades
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from backtest.engine import BacktestResult

logger = logging.getLogger(__name__)


def compute_metrics(result: BacktestResult, risk_free_rate: float = 0.05) -> dict:
    """Compute comprehensive performance metrics from backtest results.

    Args:
        result: BacktestResult from a backtest run
        risk_free_rate: Annual risk-free rate (e.g. 0.05 = 5%)

    Returns:
        dict of metric name -> value
    """
    trades = result.trades
    equity = result.equity_curve

    metrics = {}

    # --- Basic ---
    metrics["initial_capital"] = result.initial_capital
    metrics["final_capital"] = result.final_capital
    metrics["total_return_pct"] = result.total_return
    metrics["total_return_dollar"] = result.final_capital - result.initial_capital
    metrics["total_commission"] = result.total_commission
    metrics["num_trades"] = len(trades)
    metrics["signals_generated"] = result.signals_generated

    if len(trades) == 0:
        metrics["win_rate"] = 0.0
        metrics["avg_win"] = 0.0
        metrics["avg_loss"] = 0.0
        metrics["profit_factor"] = 0.0
        metrics["avg_risk_reward"] = 0.0
        metrics["max_drawdown_pct"] = 0.0
        metrics["max_drawdown_dollar"] = 0.0
        metrics["sharpe_ratio"] = 0.0
        metrics["sortino_ratio"] = 0.0
        metrics["calmar_ratio"] = 0.0
        return metrics

    # --- Win Rate ---
    winning_trades = [t for t in trades if t.net_pnl > 0]
    losing_trades = [t for t in trades if t.net_pnl <= 0]
    metrics["win_rate"] = len(winning_trades) / len(trades) * 100

    # --- Avg Win / Avg Loss ---
    winners_pnl = np.array([t.net_pnl for t in winning_trades])
    losers_pnl = np.array([t.net_pnl for t in losing_trades])

    metrics["avg_win"] = float(np.mean(winners_pnl)) if len(winners_pnl) > 0 else 0.0
    metrics["avg_loss"] = float(np.mean(losers_pnl)) if len(losers_pnl) > 0 else 0.0
    metrics["largest_win"] = float(np.max(winners_pnl)) if len(winners_pnl) > 0 else 0.0
    metrics["largest_loss"] = float(np.min(losers_pnl)) if len(losers_pnl) > 0 else 0.0

    # --- Profit Factor ---
    gross_profit = sum(t.net_pnl for t in winning_trades)
    gross_loss = abs(sum(t.net_pnl for t in losing_trades))
    metrics["profit_factor"] = float(gross_profit / gross_loss) if gross_loss > 0 else float("inf")

    # --- Avg Risk/Reward ---
    if metrics["avg_loss"] != 0:
        metrics["avg_risk_reward"] = abs(metrics["avg_win"] / metrics["avg_loss"])
    else:
        metrics["avg_risk_reward"] = float("inf")

    # --- Max Drawdown ---
    cumulative = equity.values
    running_max = np.maximum.accumulate(cumulative)
    drawdown = cumulative - running_max
    drawdown_pct = drawdown / running_max * 100

    metrics["max_drawdown_pct"] = float(np.min(drawdown_pct))
    metrics["max_drawdown_dollar"] = float(np.min(drawdown))

    # --- Sharpe Ratio ---
    if len(equity) > 1:
        returns = equity.pct_change().dropna()
        if len(returns) > 0 and returns.std() > 0:
            excess_returns = returns - risk_free_rate / 252  # Daily RF
            metrics["sharpe_ratio"] = float(
                np.sqrt(252) * excess_returns.mean() / returns.std()
            )
        else:
            metrics["sharpe_ratio"] = 0.0

        # --- Sortino Ratio (downside deviation only) ---
        downside = returns[returns < 0]
        if len(downside) > 0 and downside.std() > 0:
            metrics["sortino_ratio"] = float(
                np.sqrt(252) * excess_returns.mean() / downside.std()
            )
        else:
            metrics["sortino_ratio"] = 0.0
    else:
        metrics["sharpe_ratio"] = 0.0
        metrics["sortino_ratio"] = 0.0

    # --- Calmar Ratio ---
    if metrics["max_drawdown_pct"] != 0:
        metrics["calmar_ratio"] = abs(metrics["total_return_pct"] / metrics["max_drawdown_pct"])
    else:
        metrics["calmar_ratio"] = float("inf")

    # --- Trade Duration Stats ---
    if trades:
        durations = [(t.exit_time - t.entry_time).total_seconds() / 3600 for t in trades]
        metrics["avg_trade_duration_hours"] = float(np.mean(durations))
        metrics["max_trade_duration_hours"] = float(np.max(durations))
        metrics["min_trade_duration_hours"] = float(np.min(durations))

    # --- Average MAE / MFE (optional advanced) ---
    metrics["avg_commission_per_trade"] = result.total_commission / len(trades)

    return metrics


def print_report(result: BacktestResult) -> None:
    """Print a human-readable performance report.

    Args:
        result: BacktestResult to summarize
    """
    metrics = compute_metrics(result)

    print("=" * 60)
    print("BACKTEST PERFORMANCE REPORT")
    print("=" * 60)
    print(f"Initial Capital:  ${metrics['initial_capital']:>10,.2f}")
    print(f"Final Capital:    ${metrics['final_capital']:>10,.2f}")
    print(f"Total Return:     {metrics['total_return_pct']:>9.2f}%")
    print(f"Total P&L:        ${metrics['total_return_dollar']:>10,.2f}")
    print(f"Total Commission: ${metrics['total_commission']:>10,.2f}")
    print("-" * 60)
    print(f"Number of Trades:      {metrics['num_trades']:>6}")
    print(f"Win Rate:              {metrics['win_rate']:>5.1f}%")
    print(f"Profit Factor:         {metrics['profit_factor']:>8.3f}")
    print(f"Avg Risk/Reward:       {metrics['avg_risk_reward']:>8.3f}")
    print(f"Avg Win:               ${metrics['avg_win']:>10,.2f}")
    print(f"Avg Loss:              ${metrics['avg_loss']:>10,.2f}")
    print(f"Largest Win:           ${metrics['largest_win']:>10,.2f}")
    print(f"Largest Loss:          ${metrics['largest_loss']:>10,.2f}")
    print("-" * 60)
    print(f"Max Drawdown:          {metrics['max_drawdown_pct']:>8.2f}%")
    print(f"Max Drawdown ($):      ${metrics['max_drawdown_dollar']:>10,.2f}")
    print(f"Sharpe Ratio:          {metrics['sharpe_ratio']:>8.3f}")
    print(f"Sortino Ratio:         {metrics['sortino_ratio']:>8.3f}")
    print(f"Calmar Ratio:          {metrics['calmar_ratio']:>8.3f}")
    print(f"Avg Trade Duration:    {metrics.get('avg_trade_duration_hours', 0):>5.1f} hours")
    print("=" * 60)


def metrics_to_dataframe(metrics: dict) -> pd.DataFrame:
    """Convert metrics dict to a single-row DataFrame for CSV export.

    Args:
        metrics: dict from compute_metrics()

    Returns:
        DataFrame with metrics as columns
    """
    return pd.DataFrame([metrics])