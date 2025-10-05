"""
ML-based transport validation inference.

EXPERIMENTAL: This module uses trained XGBoost/LightGBM models to validate
whether a user was actually traveling on a specific vehicle based on sensor data.

Current approach: Uses aggregated 1Hz features with XGBoost/LightGBM
Future improvement: Transformer model with attention mechanism

TODO: TRANSFORMER MODEL (HIGH PRIORITY)
======================================
The current approach aggregates 100Hz sensor data to 1Hz with statistics.
However, a TRANSFORMER model would be significantly better because:

1. ATTENTION MECHANISM:
   - Can focus on relevant parts of the journey (stops, accelerations, turns)
   - Understands temporal dependencies better
   - No need for manual feature engineering

2. SCALABILITY:
   - Can process entire journey sequences at once
   - Better handles variable-length journeys
   - More robust to missing data

3. EXTENSIBILITY FOR ECO-MOBILITY GRATIFICATION:
   - Can be extended to classify ALL transport modes:
     * Public transport (bus, tram, train, metro)
     * Car (driver vs passenger)
     * Bicycle
     * Walking
     * Electric scooter
     * Other

   - This enables:
     * Rewarding users for eco-friendly transport choices
     * Tracking carbon footprint
     * Gamification (badges, points, leaderboards)
     * City-wide mobility analytics
     * Personalized route suggestions

4. CONTINUOUS LEARNING:
   - Model improves with every user journey
   - Can adapt to new transport modes
   - Learns user-specific patterns

RECOMMENDED ARCHITECTURE:
- Input: Raw 100Hz sensor sequences (no aggregation needed)
- Encoder: Transformer encoder (self-attention + feed-forward)
- Output: Multi-class classification (transport mode + validity)
- Training: Supervised learning with user feedback

IMPLEMENTATION STEPS:
1. Collect sufficient training data (>10k journeys)
2. Implement transformer architecture (PyTorch/TensorFlow)
3. Train with cross-validation
4. A/B test against current XGBoost model
5. Deploy if performance improvement >5%
6. Extend to multi-modal classification
7. Implement reward system for eco-mobility
"""

import json
import sys
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

# Try to import ML libraries
try:
    import lightgbm as lgb  # type: ignore
    import xgboost as xgb  # type: ignore

    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    lgb = None  # type: ignore
    xgb = None  # type: ignore

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TransportClassifier:
    """
    EXPERIMENTAL: ML-based transport validation.

    This class loads trained XGBoost/LightGBM models and uses them to validate
    whether a user was actually on a specific vehicle based on sensor data.

    Status: TESTING PHASE - Data collection for model evaluation
    """

    def __init__(self, model_type="xgboost"):
        """
        Initialize the transport classifier.

        Args:
            model_type: "xgboost" or "lightgbm"
        """
        self.model_type = model_type
        self.model = None
        self.is_loaded = False

        if not ML_AVAILABLE:
            print("WARNING: XGBoost/LightGBM not available. ML validation disabled.")
            return

        # Try to load the model
        try:
            self.load_model()
        except Exception as e:
            print(f"WARNING: Could not load {model_type} model: {e}")
            print("ML validation will not be available.")

    def load_model(self):
        """Load the trained model from disk."""
        if self.model_type == "xgboost":
            if xgb is None:
                raise ImportError("XGBoost not available")
            model_path = Path(__file__).parent / "xgboost_transport_validator.json"
            if model_path.exists():
                self.model = xgb.XGBClassifier()  # type: ignore
                self.model.load_model(str(model_path))  # type: ignore
                self.is_loaded = True
                print(f"Loaded XGBoost model from {model_path}")
            else:
                raise FileNotFoundError(f"XGBoost model not found at {model_path}")

        elif self.model_type == "lightgbm":
            if lgb is None:
                raise ImportError("LightGBM not available")
            model_path = Path(__file__).parent / "lightgbm_transport_validator.txt"
            if model_path.exists():
                self.model = lgb.Booster(model_file=str(model_path))  # type: ignore
                self.is_loaded = True
                print(f"Loaded LightGBM model from {model_path}")
            else:
                raise FileNotFoundError(f"LightGBM model not found at {model_path}")

        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def prepare_features(self, journey_data: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features from raw journey data for model inference.

        This aggregates high-frequency sensor data to 1Hz with statistics,
        same as the training data preparation.

        Args:
            journey_data: DataFrame with raw sensor readings (100Hz)

        Returns:
            DataFrame with aggregated features (1Hz)
        """
        # TODO: CRITICAL - This aggregation step is a bottleneck
        # A Transformer model would work directly with raw 100Hz sequences
        # and learn the optimal feature representation automatically

        from ml.prepare_transport_validation_data import aggregate_to_1hz

        # Aggregate to 1Hz
        aggregated = aggregate_to_1hz(journey_data)

        # Add temporal features
        aggregated["timestamp"] = pd.to_datetime(aggregated["timestamp"])
        aggregated["hour_of_day"] = aggregated["timestamp"].dt.hour
        aggregated["day_of_week"] = aggregated["timestamp"].dt.dayofweek
        aggregated["is_weekend"] = aggregated["day_of_week"].isin([5, 6]).astype(int)

        # TODO: Add vehicle type encoding if needed
        # (This should match the training data preparation)

        return aggregated

    def predict(
        self, journey_data: pd.DataFrame, threshold: float = 0.5
    ) -> Tuple[bool, float, Dict]:
        """
        Predict whether user was actually on the vehicle.

        EXPERIMENTAL: This is for testing and data collection only.
        Results are logged but not yet used for final decision.

        Args:
            journey_data: Raw sensor data from the journey
            threshold: Classification threshold (default 0.5)

        Returns:
            Tuple of:
            - is_valid: Boolean prediction
            - confidence: Probability score (0-1)
            - metadata: Additional information for analysis
        """
        if not self.is_loaded:
            # Fallback to rule-based validation
            return (
                False,
                0.0,
                {"error": "Model not loaded", "method": "rule_based_fallback"},
            )

        try:
            # Prepare features
            features = self.prepare_features(journey_data)

            if len(features) == 0:
                return (
                    False,
                    0.0,
                    {
                        "error": "No features after aggregation",
                        "method": "rule_based_fallback",
                    },
                )

            # Drop non-feature columns
            feature_cols = [
                col
                for col in features.columns
                if col
                not in [
                    "timestamp",
                    "journey_data_id",
                    "vehicle_trip_id",
                    "user_id",
                    "is_valid_trip",
                ]
            ]
            X = features[feature_cols]

            # Handle missing values
            X = X.fillna(0)

            # Predict
            if self.model_type == "xgboost":
                proba = self.model.predict_proba(X)[:, 1]  # type: ignore
            else:  # lightgbm
                proba = self.model.predict(X)  # type: ignore

            # Aggregate predictions (majority vote + average confidence)
            avg_proba = float(np.mean(proba))  # type: ignore
            is_valid = avg_proba >= threshold

            metadata = {
                "method": f"ml_{self.model_type}",
                "num_samples": len(X),
                "avg_confidence": avg_proba,
                "min_confidence": float(np.min(proba)),  # type: ignore
                "max_confidence": float(np.max(proba)),  # type: ignore
                "std_confidence": float(np.std(proba)),  # type: ignore
                "threshold": threshold,
            }

            return is_valid, avg_proba, metadata

        except Exception as e:
            print(f"ERROR in ML prediction: {e}")
            return False, 0.0, {"error": str(e), "method": "rule_based_fallback"}

    def predict_and_log(
        self,
        journey_data: pd.DataFrame,
        rule_based_result: bool,
        log_file: str = "ml/validation_comparison.jsonl",
    ) -> Tuple[bool, float, Dict]:
        """
        Predict and log results for comparison with rule-based approach.

        This function:
        1. Makes ML prediction
        2. Compares with rule-based result
        3. Logs both for analysis
        4. Returns rule-based result (ML is experimental only)

        Args:
            journey_data: Raw sensor data
            rule_based_result: Result from current rule-based validation
            log_file: Path to log file

        Returns:
            Tuple of (is_valid, confidence, metadata)
        """
        # Make ML prediction
        ml_prediction, ml_confidence, ml_metadata = self.predict(journey_data)

        # Log comparison
        log_entry = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "rule_based_result": rule_based_result,
            "ml_prediction": ml_prediction,
            "ml_confidence": ml_confidence,
            "agreement": rule_based_result == ml_prediction,
            "metadata": ml_metadata,
        }

        # Append to log file
        try:
            log_path = Path(__file__).parent / log_file
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"WARNING: Could not log ML prediction: {e}")

        # EXPERIMENTAL: Return ML prediction for testing
        # In production, this should be A/B tested against rule-based
        print(
            f"[ML VALIDATION] Rule-based: {rule_based_result}, "
            f"ML: {ml_prediction} (confidence: {ml_confidence:.2f}), "
            f"Agreement: {log_entry['agreement']}"
        )

        return ml_prediction, ml_confidence, ml_metadata


# Singleton instance
_classifier = None


def get_classifier(model_type="xgboost") -> TransportClassifier:
    """Get or create the transport classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = TransportClassifier(model_type=model_type)
    return _classifier


def validate_transport_ml(
    journey_data: pd.DataFrame, rule_based_result: bool
) -> Tuple[bool, float]:
    """
    EXPERIMENTAL: ML-based transport validation.

    This function is called from the streak verification logic to:
    1. Test ML model predictions
    2. Collect data for model evaluation
    3. Compare with rule-based approach

    Currently returns rule-based result, but logs ML predictions.

    TODO: NEXT STEPS
    ================
    1. Collect >1000 validation samples
    2. Analyze ML vs rule-based agreement rate
    3. If ML accuracy >95% and agreement >90%, enable A/B testing
    4. If A/B test successful, replace rule-based with ML
    5. Implement Transformer model for better performance
    6. Extend to multi-modal transport classification

    Args:
        journey_data: Raw sensor data from journey
        rule_based_result: Result from current validation logic

    Returns:
        Tuple of (is_valid, confidence)
    """
    classifier = get_classifier()

    if not classifier.is_loaded:
        # Model not available, use rule-based
        return rule_based_result, 1.0 if rule_based_result else 0.0

    # Make prediction and log
    ml_prediction, ml_confidence, metadata = classifier.predict_and_log(
        journey_data, rule_based_result
    )

    # EXPERIMENTAL: For now, return rule-based result
    # Uncomment below to use ML prediction (after sufficient testing)
    # return ml_prediction, ml_confidence

    return rule_based_result, 1.0 if rule_based_result else 0.0
