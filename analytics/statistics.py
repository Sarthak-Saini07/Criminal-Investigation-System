"""
NumPy Statistical Engine & Linear Regression Crime Prediction Model.
Strictly relies ONLY on NumPy matrix operations without any external ML libraries.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Any

def compute_numpy_statistics(data_series: pd.Series) -> Dict[str, float]:
    """Computes descriptive statistical metrics using NumPy vector operations."""
    arr = np.array(data_series.dropna(), dtype=np.float64)
    if arr.size == 0:
        return {"mean": 0.0, "median": 0.0, "variance": 0.0, "std_dev": 0.0, "p25": 0.0, "p75": 0.0}

    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "variance": float(np.var(arr, ddof=1)) if arr.size > 1 else 0.0,
        "std_dev": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr))
    }

def min_max_normalize(data_series: pd.Series) -> np.ndarray:
    """Min-Max Normalization using NumPy: (X - min) / (max - min)."""
    arr = np.array(data_series.dropna(), dtype=np.float64)
    if arr.size == 0 or np.max(arr) == np.min(arr):
        return np.zeros_like(arr)
    return (arr - np.min(arr)) / (np.max(arr) - np.min(arr))

def compute_moving_average(arr: np.ndarray, window_size: int = 3) -> np.ndarray:
    """Computes moving average using NumPy 1D convolution."""
    if arr.size < window_size:
        return arr
    weights = np.ones(window_size) / window_size
    return np.convolve(arr, weights, mode='valid')

def numpy_linear_regression_predict(monthly_counts: List[int], future_steps: int = 6) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Pure NumPy Ordinary Least Squares (OLS) Linear Regression for Crime Forecasting.
    Solves Beta = (X^T * X)^(-1) * X^T * Y using NumPy matrix algebra.
    
    Returns:
        historical_pred (np.ndarray): In-sample fitted crime counts.
        future_pred (np.ndarray): Forecasted crime counts for future months.
        r_squared (float): Coefficient of determination R^2 score.
    """
    y = np.array(monthly_counts, dtype=np.float64)
    n = len(y)
    if n < 2:
        return y, y, 0.0

    # 1. Construct Design Matrix X with Bias Term: shape (n, 2)
    # Column 0: Intercept (ones), Column 1: Time index t (1, 2, ..., n)
    t = np.arange(1, n + 1, dtype=np.float64)
    X = np.column_stack((np.ones(n), t))

    # 2. OLS Matrix Closed-Form Equation: Beta = (X^T * X)^(-1) * X^T * y
    XtX = np.matmul(X.T, X)
    XtX_inv = np.linalg.pinv(XtX)  # Pseudoinverse for numerical stability
    Xty = np.matmul(X.T, y)
    beta = np.matmul(XtX_inv, Xty)  # beta[0] = intercept, beta[1] = slope

    # 3. In-Sample Predictions
    historical_pred = np.matmul(X, beta)

    # 4. Out-of-Sample Future Forecast
    t_future = np.arange(n + 1, n + 1 + future_steps, dtype=np.float64)
    X_future = np.column_stack((np.ones(future_steps), t_future))
    future_pred = np.matmul(X_future, beta)

    # 5. R-Squared Metric Calculation
    ss_res = np.sum((y - historical_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return historical_pred, future_pred, float(r_squared)
