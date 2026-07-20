"""
Random Forest model for trading signal prediction.

Trains on technical indicators and price features to predict
directional market moves (up/down/flat).
"""

import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

from config.settings import RANDOM_FOREST_CONFIG

logger = logging.getLogger(__name__)


class RandomForestModel:
    """Random Forest classifier for trading signals.

    Predicts whether the market will go up (1), down (-1), or stay flat (0)
    based on engineered features.
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or RANDOM_FOREST_CONFIG
        self.model: Optional[RandomForestClassifier] = None
        self.feature_names: list[str] = []
        self.is_trained = False

    def build_model(self) -> RandomForestClassifier:
        """Construct and return a fresh RandomForest classifier."""
        return RandomForestClassifier(
            n_estimators=self.config["n_estimators"],
            max_depth=self.config["max_depth"],
            min_samples_split=self.config["min_samples_split"],
            min_samples_leaf=self.config["min_samples_leaf"],
            random_state=self.config["random_state"],
            n_jobs=self.config["n_jobs"],
            class_weight="balanced",
            verbose=0,
        )

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = 0.2,
        validate: bool = True,
    ) -> dict:
        """Train the Random Forest model.

        Args:
            X: Feature DataFrame
            y: Target Series (1, 0, -1)
            test_size: Fraction of data for validation
            validate: Whether to compute validation metrics

        Returns:
            dict with training metrics (accuracy, classification report)
        """
        self.feature_names = list(X.columns)
        self.model = self.build_model()

        if validate and len(X) > 100:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=self.config["random_state"],
                stratify=y if len(y.unique()) > 1 else None,
            )
        else:
            X_train, X_test, y_train, y_test = X, None, y, None

        logger.info(
            f"Training RandomForest on {len(X_train)} samples "
            f"with {len(self.feature_names)} features"
        )

        self.model.fit(X_train, y_train)
        self.is_trained = True

        metrics = {"train_samples": len(X_train)}

        if y_test is not None and len(y_test) > 0:
            y_pred = self.model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            metrics["test_accuracy"] = float(acc)
            metrics["test_samples"] = len(y_test)
            metrics["classification_report"] = classification_report(
                y_test, y_pred, output_dict=True, zero_division=0
            )
            logger.info(f"Test accuracy: {acc:.4f}")

        # Feature importance
        metrics["feature_importances"] = dict(
            sorted(
                zip(self.feature_names, self.model.feature_importances_),
                key=lambda x: x[1],
                reverse=True,
            )
        )

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict direction for given features.

        Args:
            X: Feature DataFrame with same columns as training

        Returns:
            Array of predictions (-1, 0, 1)
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model not trained yet. Call train() first.")

        # Ensure columns match training
        X = X[self.feature_names]
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get probability estimates for each class.

        Args:
            X: Feature DataFrame

        Returns:
            Array of shape (n_samples, n_classes) with class probabilities
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model not trained yet. Call train() first.")

        X = X[self.feature_names]
        return self.model.predict_proba(X)

    def predict_confidence(self, X: pd.DataFrame) -> pd.Series:
        """Predict with confidence score (max probability).

        Args:
            X: Feature DataFrame

        Returns:
            Series with confidence values (0.0–1.0)
        """
        proba = self.predict_proba(X)
        return pd.Series(proba.max(axis=1), index=X.index)

    def save(self, path: str) -> str:
        """Save model to disk.

        Args:
            path: File path (without extension)

        Returns:
            Full path to saved model
        """
        if self.model is None:
            raise RuntimeError("No model to save.")

        model_path = f"{path}_rf_model.joblib"
        meta_path = f"{path}_rf_meta.joblib"

        joblib.dump(self.model, model_path)
        joblib.dump({
            "feature_names": self.feature_names,
            "config": self.config,
            "is_trained": self.is_trained,
        }, meta_path)

        logger.info(f"Model saved to {model_path}")
        return model_path

    def load(self, path: str) -> None:
        """Load model from disk.

        Args:
            path: Base path (without extension) used when saving
        """
        model_path = f"{path}_rf_model.joblib"
        meta_path = f"{path}_rf_meta.joblib"

        self.model = joblib.load(model_path)
        meta = joblib.load(meta_path)
        self.feature_names = meta["feature_names"]
        self.config = meta["config"]
        self.is_trained = meta["is_trained"]

        logger.info(f"Model loaded from {model_path}")