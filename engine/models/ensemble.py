"""
Ensemble model: combines predictions from Random Forest and Neural Network
for improved signal quality.

Uses weighted voting, confidence-based blending, or stacking.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

from models.random_forest import RandomForestModel
from models.neural_net import NeuralNetworkModel

logger = logging.getLogger(__name__)


class EnsembleModel:
    """Ensemble combining Random Forest and Neural Network predictions.

    Supports three blending strategies:
      - "vote": Majority vote across models
      - "weighted": Weighted average of probabilities
      - "confidence": Use the prediction from the most confident model
    """

    def __init__(
        self,
        rf_model: Optional[RandomForestModel] = None,
        nn_model: Optional[NeuralNetworkModel] = None,
        strategy: str = "weighted",
        weights: Optional[list[float]] = None,
    ):
        self.rf_model = rf_model
        self.nn_model = nn_model
        self.strategy = strategy
        # Default weights: RF 0.5, NN 0.5
        self.weights = weights or [0.5, 0.5]
        self.is_trained = False

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        validation_data: Optional[tuple] = None,
    ) -> dict:
        """Train both underlying models.

        Args:
            X: Feature DataFrame
            y: Target Series
            validation_data: Optional (X_val, y_val) tuple

        Returns:
            dict with training metrics for each model
        """
        metrics = {}

        # Train Random Forest
        if self.rf_model is not None:
            logger.info("Training Random Forest model...")
            val_split = 0.2
            if validation_data:
                X_val, y_val = validation_data
                # Use full training data, validate separately
            rf_metrics = self.rf_model.train(X, y, test_size=val_split)
            metrics["random_forest"] = rf_metrics
        else:
            logger.warning("No Random Forest model provided for ensemble")

        # Train Neural Network
        if self.nn_model is not None:
            logger.info("Training Neural Network model...")
            nn_metrics = self.nn_model.train(
                X, y,
                validation_data=validation_data,
                verbose=0,
            )
            metrics["neural_network"] = nn_metrics
        else:
            logger.warning("No Neural Network model provided for ensemble")

        self.is_trained = True
        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Ensemble prediction.

        Args:
            X: Feature DataFrame

        Returns:
            Array of predictions (-1, 0, 1)
        """
        if not self.is_trained:
            raise RuntimeError("Ensemble not trained. Call train() first.")

        if self.strategy == "vote":
            return self._vote_predict(X)
        elif self.strategy == "confidence":
            return self._confidence_predict(X)
        else:  # weighted
            return self._weighted_predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get combined probability estimates for each class.

        Returns:
            Array of shape (n_samples, 3) with probabilities for [-1, 0, 1]
        """
        probas = []
        total_weight = 0.0

        if self.rf_model is not None and self.rf_model.is_trained:
            rf_proba = self.rf_model.predict_proba(X)
            # RF returns probabilities in order of classes_ attribute
            # Map to standard [-1, 0, 1] order
            probas.append(rf_proba * self.weights[0])
            total_weight += self.weights[0]

        if self.nn_model is not None and self.nn_model.is_trained:
            nn_proba = self.nn_model.predict_proba(X)
            # NN returns in [-1, 0, 1] order since we mapped during training
            probas.append(nn_proba * self.weights[1])
            total_weight += self.weights[1]

        if not probas:
            raise RuntimeError("No trained models available in ensemble")

        combined = sum(probas) / total_weight
        return combined

    def predict_confidence(self, X: pd.DataFrame) -> pd.Series:
        """Get confidence scores for ensemble predictions.

        Args:
            X: Feature DataFrame

        Returns:
            Series with confidence values (0.0–1.0)
        """
        proba = self.predict_proba(X)
        return pd.Series(proba.max(axis=1), index=X.index)

    def _vote_predict(self, X: pd.DataFrame) -> np.ndarray:
        """Majority vote across models."""
        predictions = []

        if self.rf_model is not None and self.rf_model.is_trained:
            predictions.append(self.rf_model.predict(X))
        if self.nn_model is not None and self.nn_model.is_trained:
            predictions.append(self.nn_model.predict(X))

        if not predictions:
            raise RuntimeError("No trained models available in ensemble")

        # Stack predictions and take mode
        stacked = np.column_stack(predictions)
        # Use bincount along axis=1
        result = np.array([
            np.bincount(row + 1).argmax() - 1  # shift to handle -1
            for row in stacked
        ])
        return result

    def _weighted_predict(self, X: pd.DataFrame) -> np.ndarray:
        """Weighted average of probabilities."""
        proba = self.predict_proba(X)
        return np.array([[-1, 0, 1][p] for p in np.argmax(proba, axis=1)])

    def _confidence_predict(self, X: pd.DataFrame) -> np.ndarray:
        """Use the prediction from the most confident model."""
        predictions = []
        max_confidences = []

        if self.rf_model is not None and self.rf_model.is_trained:
            p = self.rf_model.predict(X)
            c = self.rf_model.predict_confidence(X)
            predictions.append(p)
            max_confidences.append(c.values)

        if self.nn_model is not None and self.nn_model.is_trained:
            p = self.nn_model.predict(X)
            c = self.nn_model.predict_confidence(X)
            predictions.append(p)
            max_confidences.append(c.values)

        if not predictions:
            raise RuntimeError("No trained models available in ensemble")

        conf_array = np.column_stack(max_confidences)
        pred_array = np.column_stack(predictions)

        # Pick prediction from the model with highest confidence
        best_model_idx = np.argmax(conf_array, axis=1)
        return np.array([pred_array[i, idx] for i, idx in enumerate(best_model_idx)])

    def save(self, path: str) -> list[str]:
        """Save both models to disk.

        Args:
            path: Base path (without extension)

        Returns:
            List of saved model paths
        """
        paths = []
        if self.rf_model is not None:
            paths.append(self.rf_model.save(path))
        if self.nn_model is not None:
            paths.append(self.nn_model.save(path))
        return paths

    def load(self, path: str) -> None:
        """Load both models from disk.

        Args:
            path: Base path (without extension) used when saving
        """
        if self.rf_model is not None:
            self.rf_model.load(path)
        if self.nn_model is not None:
            self.nn_model.load(path)
        self.is_trained = True