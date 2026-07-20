"""
Signal generation: combines ML model predictions with rule-based logic
to produce final trading signals.

The signal aggregator:
1. Gets predictions from ML ensemble
2. Computes rule-based signals
3. Combines both sources using configurable weights
4. Applies filters (confidence threshold, market hours, etc.)
"""

import logging
from datetime import datetime, time
from typing import Optional

import numpy as np
import pandas as pd

from config.settings import (
    TRADING_HOURS,
    TRADING_TIMEZONE,
    TRADING_DAYS,
)
from strategy.rules import compute_rule_signals
from models.ensemble import EnsembleModel

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates and filters trading signals from ML models and rule logic."""

    def __init__(
        self,
        ensemble: Optional[EnsembleModel] = None,
        rules_weight: float = 0.3,
        ml_weight: float = 0.7,
        confidence_threshold: float = 0.6,
        min_rule_agreement: int = 1,
    ):
        self.ensemble = ensemble
        self.rules_weight = rules_weight
        self.ml_weight = ml_weight
        self.confidence_threshold = confidence_threshold
        self.min_rule_agreement = min_rule_agreement  # Min rules that must agree

    def generate(self, df: pd.DataFrame) -> pd.Series:
        """Generate final trading signals.

        Args:
            df: DataFrame with features and technical indicators

        Returns:
            Series of signals: 1 (BUY), -1 (SELL), 0 (NEUTRAL/NO TRADE)
        """
        # 1. Get rule signals
        rule_df = compute_rule_signals(df)
        rule_consensus = rule_df["consensus"]

        # 2. Get ML signals
        ml_signal = self._get_ml_signals(df)

        # 3. Combine
        combined = self._combine_signals(rule_consensus, ml_signal)

        return combined

    def _get_ml_signals(self, df: pd.DataFrame) -> pd.Series:
        """Get signals from the ML ensemble."""
        if self.ensemble is None or not self.ensemble.is_trained:
            logger.debug("Ensemble not available — using rule signals only")
            return pd.Series(0, index=df.index)

        try:
            # Get feature columns
            from data.processor import feature_columns
            features = [c for c in feature_columns() if c in df.columns]
            if not features:
                logger.warning("No ML features found in DataFrame")
                return pd.Series(0, index=df.index)

            X = df[features].dropna()
            if X.empty:
                return pd.Series(0, index=df.index)

            predictions = self.ensemble.predict(X)
            confidences = self.ensemble.predict_confidence(X)

            # Filter by confidence threshold
            signals = pd.Series(0, index=X.index)
            signals[confidences >= self.confidence_threshold] = predictions[
                confidences >= self.confidence_threshold
            ]

            return signals
        except Exception as e:
            logger.error(f"ML signal generation failed: {e}")
            return pd.Series(0, index=df.index)

    def _combine_signals(
        self,
        rule_signal: pd.Series,
        ml_signal: pd.Series,
    ) -> pd.Series:
        """Combine rule and ML signals using weighted average.

        Args:
            rule_signal: Rule-based consensus signals (-2 to 2)
            ml_signal: ML ensemble signals (-1, 0, 1)

        Returns:
            Final combined signal (-1, 0, 1)
        """
        # Normalize rule signal to [-1, 1]
        rule_normalized = rule_signal.clip(-1, 1)

        combined = (
            rule_normalized * self.rules_weight +
            ml_signal.reindex(rule_normalized.index, fill_value=0) * self.ml_weight
        )

        # Threshold: strong conviction needed for non-zero signal
        threshold = 0.3  # minimum combined score to generate a signal
        final = pd.Series(0, index=combined.index)
        final[combined > threshold] = 1
        final[combined < -threshold] = -1

        return final

    def generate_with_details(self, df: pd.DataFrame) -> dict:
        """Generate signals with detailed breakdown for analysis.

        Returns:
            dict with 'signal', 'rule_signals', 'ml_signal', and 'confidence'
        """
        rule_df = compute_rule_signals(df)
        ml_signal = self._get_ml_signals(df)
        final = self._combine_signals(rule_df["consensus"], ml_signal)

        return {
            "signal": final,
            "rule_signals": rule_df,
            "ml_signal": ml_signal,
        }


# =========================================================================
#  Market Hours Filter
# =========================================================================

def is_market_open(dt: Optional[datetime] = None) -> bool:
    """Check if current time is within trading hours.

    Args:
        dt: Datetime to check (default: now in Eastern time)

    Returns:
        True if market is open
    """
    import pytz

    if dt is None:
        eastern = pytz.timezone(TRADING_TIMEZONE)
        dt = datetime.now(eastern)

    # Check weekday
    if dt.weekday() not in TRADING_DAYS:
        return False

    # Check hours
    start = time.fromisoformat(TRADING_HOURS["start"])
    end = time.fromisoformat(TRADING_HOURS["end"])

    return start <= dt.time() <= end


def filter_trading_hours(df: pd.DataFrame) -> pd.DataFrame:
    """Filter DataFrame to only include rows within trading hours.

    Args:
        df: DataFrame with DatetimeIndex

    Returns:
        Filtered DataFrame
    """
    import pytz

    eastern = pytz.timezone(TRADING_TIMEZONE)

    # Localize index if needed
    if df.index.tz is None:
        df.index = df.index.tz_localize("UTC").tz_convert(eastern)
    else:
        df.index = df.index.tz_convert(eastern)

    start = time.fromisoformat(TRADING_HOURS["start"])
    end = time.fromisoformat(TRADING_HOURS["end"])

    mask = (
        df.index.map(lambda x: x.weekday() in TRADING_DAYS) &
        df.index.map(lambda x: start <= x.time() <= end)
    )

    return df[mask]