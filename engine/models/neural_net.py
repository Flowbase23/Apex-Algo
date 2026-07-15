"""
Neural Network model for trading signal prediction.

Uses TensorFlow/Keras to build and train a feed-forward neural network
for predicting directional market moves.
"""

import logging
import os
from typing import Optional, Tuple

import numpy as np
import pandas as pd

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # Suppress TF info messages

from config.settings import NEURAL_NET_CONFIG

logger = logging.getLogger(__name__)

# Lazy import to avoid requiring TF if user doesn't use NN
_tf_available = None


def _check_tf():
    """Check if TensorFlow is available."""
    global _tf_available
    if _tf_available is None:
        try:
            import tensorflow as tf
            _tf_available = True
        except ImportError:
            _tf_available = False
    return _tf_available


class NeuralNetworkModel:
    """Feed-forward Neural Network for trading signal prediction.

    Architecture: Input -> Dense layers with dropout -> Output (3 classes)
    """

    def __init__(self, config: Optional[dict] = None):
        if not _check_tf():
            raise ImportError(
                "TensorFlow is required for NeuralNetworkModel. "
                "Install it with: pip install tensorflow"
            )

        self.config = config or NEURAL_NET_CONFIG
        self.model = None
        self.feature_names: list[str] = []
        self.is_trained = False
        self._history = None

    def _build_network(self, input_dim: int, num_classes: int = 3):
        """Build the Keras Sequential model."""
        import tensorflow as tf

        layers = self.config["hidden_layers"]
        dropout_rate = self.config["dropout_rate"]

        model = tf.keras.Sequential()
        model.add(tf.keras.layers.Input(shape=(input_dim,)))

        for i, units in enumerate(layers):
            model.add(tf.keras.layers.Dense(units, activation="relu"))
            model.add(tf.keras.layers.Dropout(dropout_rate))

        model.add(tf.keras.layers.Dense(num_classes, activation="softmax"))

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config["learning_rate"]),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )

        return model

    def train(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        validation_data: Optional[Tuple[pd.DataFrame, pd.Series]] = None,
        verbose: int = 0,
    ) -> dict:
        """Train the Neural Network.

        Args:
            X: Feature DataFrame
            y: Target Series (1, 0, -1) — mapped to 0, 1, 2 internally
            validation_data: Optional (X_val, y_val) tuple
            verbose: Keras verbosity level

        Returns:
            dict with training history
        """
        import tensorflow as tf

        self.feature_names = list(X.columns)

        # Map targets: -1→0, 0→1, 1→2 (for sparse_categorical_crossentropy)
        y_mapped = y.map({-1: 0, 0: 1, 1: 2}).values

        num_classes = len(y.unique())
        input_dim = X.shape[1]

        self.model = self._build_network(input_dim, num_classes)
        logger.info(
            f"Training NeuralNetwork on {len(X)} samples "
            f"with {input_dim} features, {num_classes} classes"
        )

        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss" if validation_data else "loss",
                patience=10,
                restore_best_weights=True,
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss" if validation_data else "loss",
                factor=0.5,
                patience=5,
                min_lr=1e-6,
            ),
        ]

        if validation_data:
            X_val, y_val = validation_data
            y_val_mapped = y_val.map({-1: 0, 0: 1, 1: 2}).values

            self._history = self.model.fit(
                X.values, y_mapped,
                validation_data=(X_val.values, y_val_mapped),
                epochs=self.config["epochs"],
                batch_size=self.config["batch_size"],
                callbacks=callbacks,
                verbose=verbose,
            )
        else:
            self._history = self.model.fit(
                X.values, y_mapped,
                validation_split=self.config["validation_split"],
                epochs=self.config["epochs"],
                batch_size=self.config["batch_size"],
                callbacks=callbacks,
                verbose=verbose,
            )

        self.is_trained = True

        metrics = {
            "train_samples": len(X),
            "final_loss": float(self._history.history["loss"][-1]),
            "final_accuracy": float(self._history.history["accuracy"][-1]),
        }

        if "val_loss" in self._history.history:
            metrics["val_loss"] = float(self._history.history["val_loss"][-1])
            metrics["val_accuracy"] = float(self._history.history["val_accuracy"][-1])

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict direction.

        Args:
            X: Feature DataFrame

        Returns:
            Array of predictions (-1, 0, 1)
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model not trained yet. Call train() first.")

        X = X[self.feature_names]
        probs = self.model.predict(X.values, verbose=0)
        # Map back: 0→-1, 1→0, 2→1
        pred_classes = np.argmax(probs, axis=1)
        return np.array([[-1, 0, 1][c] for c in pred_classes])

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get probability estimates for each class.

        Args:
            X: Feature DataFrame

        Returns:
            Array of shape (n_samples, 3) with probabilities for [-1, 0, 1]
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Model not trained yet. Call train() first.")

        X = X[self.feature_names]
        return self.model.predict(X.values, verbose=0)

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
            Full path to saved model directory
        """
        if self.model is None:
            raise RuntimeError("No model to save.")

        import json

        model_path = f"{path}_nn_model"
        meta_path = f"{path}_nn_meta.json"

        self.model.save(model_path)
        with open(meta_path, "w") as f:
            json.dump({
                "feature_names": self.feature_names,
                "config": self.config,
                "is_trained": self.is_trained,
            }, f)

        logger.info(f"Neural network model saved to {model_path}")
        return model_path

    def load(self, path: str) -> None:
        """Load model from disk.

        Args:
            path: Base path (without extension) used when saving
        """
        import json
        import tensorflow as tf

        model_path = f"{path}_nn_model"
        meta_path = f"{path}_nn_meta.json"

        self.model = tf.keras.models.load_model(model_path)
        with open(meta_path, "r") as f:
            meta = json.load(f)

        self.feature_names = meta["feature_names"]
        self.config = meta["config"]
        self.is_trained = meta["is_trained"]

        logger.info(f"Neural network model loaded from {model_path}")