"""
Train transport validation classifier using XGBoost and LightGBM.

This script trains two models to validate whether a user is actually
traveling on a specific public transport vehicle based on sensor data.

Models:
- XGBoost Classifier
- LightGBM Classifier

Evaluation metrics:
- Accuracy
- Precision, Recall, F1-Score
- ROC-AUC
- Confusion Matrix
"""

import sys
from pathlib import Path

import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split


def load_data(data_path="ml/transport_validation_data.csv"):
    """Load prepared training data."""
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples")
    return df


def prepare_train_test_split(df, test_size=0.2, random_state=42):
    """Split data into train and test sets."""
    print(f"\nSplitting data: {100*(1-test_size):.0f}% train, {100*test_size:.0f}% test")

    # Separate features and label
    X = df.drop("is_valid_trip", axis=1)
    y = df["is_valid_trip"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    print(f"Train set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    print(f"Train label distribution: {y_train.value_counts().to_dict()}")
    print(f"Test label distribution: {y_test.value_counts().to_dict()}")

    return X_train, X_test, y_train, y_test


def train_xgboost(X_train, y_train, X_test, y_test):
    """Train XGBoost classifier."""
    print("\n" + "=" * 60)
    print("Training XGBoost Classifier")
    print("=" * 60)

    # Hyperparameters
    params = {
        "objective": "binary:logistic",
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "eval_metric": "logloss",
    }

    print("\nHyperparameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    # Train model
    model = xgb.XGBClassifier(**params)
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    return model, y_pred, y_pred_proba


def train_lightgbm(X_train, y_train, X_test, y_test):
    """Train LightGBM classifier."""
    print("\n" + "=" * 60)
    print("Training LightGBM Classifier")
    print("=" * 60)

    # Hyperparameters
    params = {
        "objective": "binary",
        "metric": "binary_logloss",
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
        "verbose": -1,
    }

    print("\nHyperparameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")

    # Train model
    model = lgb.LGBMClassifier(**params)
    model.fit(
        X_train,
        y_train,
        eval_set=[(X_test, y_test)],
        eval_metric="logloss",
    )

    # Predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]

    return model, y_pred, y_pred_proba


def evaluate_model(model_name, y_test, y_pred, y_pred_proba):
    """Evaluate model performance."""
    print(f"\n=== {model_name} Performance ===")

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")

    # Classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Invalid", "Valid"]))

    # ROC-AUC
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print(f"ROC-AUC Score: {roc_auc:.4f}")

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(cm)

    return accuracy, roc_auc, cm


def plot_feature_importance(model, feature_names, model_name, top_n=20):
    """Plot feature importance."""
    print(f"\nPlotting feature importance for {model_name}...")

    # Get feature importance
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        print("Model does not have feature_importances_ attribute")
        return

    # Create dataframe
    feature_imp = pd.DataFrame(
        {"feature": feature_names, "importance": importances}
    ).sort_values("importance", ascending=False)

    # Plot top N features
    plt.figure(figsize=(10, 8))
    sns.barplot(data=feature_imp.head(top_n), x="importance", y="feature")
    plt.title(f"{model_name} - Top {top_n} Feature Importance")
    plt.xlabel("Importance")
    plt.ylabel("Feature")
    plt.tight_layout()

    output_path = f"ml/{model_name.lower().replace(' ', '_')}_feature_importance.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved to {output_path}")
    plt.close()


def plot_confusion_matrix(cm, model_name):
    """Plot confusion matrix."""
    print(f"\nPlotting confusion matrix for {model_name}...")

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Invalid", "Valid"],
        yticklabels=["Invalid", "Valid"],
    )
    plt.title(f"{model_name} - Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()

    output_path = f"ml/{model_name.lower().replace(' ', '_')}_confusion_matrix.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved to {output_path}")
    plt.close()


def plot_roc_curve(y_test, y_pred_proba_xgb, y_pred_proba_lgb):
    """Plot ROC curves for both models."""
    print("\nPlotting ROC curves...")

    plt.figure(figsize=(10, 8))

    # XGBoost ROC
    fpr_xgb, tpr_xgb, _ = roc_curve(y_test, y_pred_proba_xgb)
    roc_auc_xgb = roc_auc_score(y_test, y_pred_proba_xgb)
    plt.plot(
        fpr_xgb,
        tpr_xgb,
        label=f"XGBoost (AUC = {roc_auc_xgb:.4f})",
        linewidth=2,
    )

    # LightGBM ROC
    fpr_lgb, tpr_lgb, _ = roc_curve(y_test, y_pred_proba_lgb)
    roc_auc_lgb = roc_auc_score(y_test, y_pred_proba_lgb)
    plt.plot(
        fpr_lgb,
        tpr_lgb,
        label=f"LightGBM (AUC = {roc_auc_lgb:.4f})",
        linewidth=2,
    )

    # Diagonal line
    plt.plot([0, 1], [0, 1], "k--", label="Random Classifier")

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves - Transport Validation Classifier")
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.tight_layout()

    output_path = "ml/roc_curves_comparison.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Saved to {output_path}")
    plt.close()


def save_models(xgb_model, lgb_model):
    """Save trained models."""
    print("\nSaving models...")

    # Save XGBoost
    xgb_model.save_model("ml/xgboost_transport_validator.json")
    print("Saved XGBoost model to ml/xgboost_transport_validator.json")

    # Save LightGBM
    lgb_model.booster_.save_model("ml/lightgbm_transport_validator.txt")
    print("Saved LightGBM model to ml/lightgbm_transport_validator.txt")


def main():
    """Main training function."""
    print("=" * 60)
    print("Transport Validation Classifier - Training")
    print("=" * 60)
    print()

    # Create output directory
    Path("ml").mkdir(exist_ok=True)

    # Load data
    df = load_data()

    # Check if we have both classes
    if df["is_valid_trip"].nunique() < 2:
        print("ERROR: Dataset must contain both valid and invalid trips!")
        print("Current label distribution:")
        print(df["is_valid_trip"].value_counts())
        return

    # Prepare train/test split
    X_train, X_test, y_train, y_test = prepare_train_test_split(df)

    # Train XGBoost
    xgb_model, xgb_pred, xgb_pred_proba = train_xgboost(
        X_train, y_train, X_test, y_test
    )
    xgb_accuracy, xgb_roc_auc, xgb_cm = evaluate_model(
        "XGBoost", y_test, xgb_pred, xgb_pred_proba
    )

    # Train LightGBM
    lgb_model, lgb_pred, lgb_pred_proba = train_lightgbm(
        X_train, y_train, X_test, y_test
    )
    lgb_accuracy, lgb_roc_auc, lgb_cm = evaluate_model(
        "LightGBM", y_test, lgb_pred, lgb_pred_proba
    )

    # Plot feature importance
    feature_names = X_train.columns.tolist()
    plot_feature_importance(xgb_model, feature_names, "XGBoost")
    plot_feature_importance(lgb_model, feature_names, "LightGBM")

    # Plot confusion matrices
    plot_confusion_matrix(xgb_cm, "XGBoost")
    plot_confusion_matrix(lgb_cm, "LightGBM")

    # Plot ROC curves
    plot_roc_curve(y_test, xgb_pred_proba, lgb_pred_proba)

    # Save models
    save_models(xgb_model, lgb_model)

    # Final comparison
    print("\n" + "=" * 60)
    print("Model Comparison")
    print("=" * 60)
    print(f"{'Metric':<20} {'XGBoost':<15} {'LightGBM':<15}")
    print("-" * 50)
    print(f"{'Accuracy':<20} {xgb_accuracy:<15.4f} {lgb_accuracy:<15.4f}")
    print(f"{'ROC-AUC':<20} {xgb_roc_auc:<15.4f} {lgb_roc_auc:<15.4f}")

    if xgb_roc_auc > lgb_roc_auc:
        print("\n✓ XGBoost performs better (higher ROC-AUC)")
    elif lgb_roc_auc > xgb_roc_auc:
        print("\n✓ LightGBM performs better (higher ROC-AUC)")
    else:
        print("\n= Both models perform equally")

    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  - ml/xgboost_transport_validator.json")
    print("  - ml/lightgbm_transport_validator.txt")
    print("  - ml/xgboost_feature_importance.png")
    print("  - ml/lightgbm_feature_importance.png")
    print("  - ml/xgboost_confusion_matrix.png")
    print("  - ml/lightgbm_confusion_matrix.png")
    print("  - ml/roc_curves_comparison.png")
    print()


if __name__ == "__main__":
    main()
