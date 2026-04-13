"""
gcsi_loader.py
==============
Global Supply Chain Stress Index (GSCSI) Integration Module.

Loads monthly GSCSI values and converts them into stress multipliers
using percentile-based thresholds for low/medium/high scenarios.

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

from typing import Dict, Optional

import numpy as np
import pandas as pd

from . import config

logger = config.setup_logging()


def _get_value_column(df: pd.DataFrame) -> str:
    """Pick the GSCSI value column robustly."""
    # preferred
    if "value" in df.columns:
        return "value"
    # fallback: first numeric column
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError(f"GSCSI CSV has no numeric columns. Columns: {list(df.columns)}")
    return numeric_cols[0]


class GCSIStressModel:
    """Manages GSCSI data and provides scenario-based stress multipliers."""

    def __init__(self, path: Optional[str] = None):
        self.path = path or config.GCSI_CSV
        self.data = self._load()
        self.thresholds = self._compute_thresholds()
        self.multipliers = self._compute_multipliers()

    def _load(self) -> pd.DataFrame:
        """Load GSCSI CSV and validate."""
        try:
            df = pd.read_csv(self.path)
            col = _get_value_column(df)
            df = df.rename(columns={col: "value"})
            df = df.dropna(subset=["value"])
            logger.info("GSCSI loaded: %d data points.", len(df))
            return df
        except FileNotFoundError:
            logger.warning("GSCSI file not found at %s. Using default.", self.path)
            return pd.DataFrame({"value": [0.5, 1.0, 1.5]})

    def _compute_thresholds(self) -> Dict[str, float]:
        """Compute percentile thresholds from data."""
        values = self.data["value"].astype(float)
        return {
            "p33": float(np.percentile(values, config.GCSI_LOW_PERCENTILE)),
            "p66": float(np.percentile(values, config.GCSI_HIGH_PERCENTILE)),
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
        }

    def _compute_multipliers(self) -> Dict[str, float]:
        """Compute average GSCSI value within each stress regime."""
        values = self.data["value"].astype(float)
        p33 = self.thresholds["p33"]
        p66 = self.thresholds["p66"]

        low_vals = values[values <= p33]
        mid_vals = values[(values > p33) & (values < p66)]
        high_vals = values[values >= p66]

        multipliers = {
            "low": float(low_vals.mean()) if len(low_vals) > 0 else 0.5,
            "medium": float(mid_vals.mean()) if len(mid_vals) > 0 else 1.0,
            "high": float(high_vals.mean()) if len(high_vals) > 0 else 1.5,
        }

        logger.info("Stress multipliers: %s", multipliers)
        return multipliers

    def get_multiplier(self, scenario: str = "medium") -> float:
        """Return stress multiplier for 'low'/'medium'/'high'."""
        return self.multipliers.get(scenario.lower(), 1.0)

    def get_summary(self) -> dict:
        """Summary for dashboard."""
        return {
            "data_points": len(self.data),
            **self.thresholds,
            **{f"mult_{k}": v for k, v in self.multipliers.items()},
        }


_model = None


def get_stress_multiplier(scenario: str = "medium") -> float:
    """Module-level convenience getter."""
    global _model
    if _model is None:
        _model = GCSIStressModel()
    return _model.get_multiplier(scenario)