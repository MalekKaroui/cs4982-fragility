"""
gcsi_loader.py
==============
Global Supply Chain Stress Index (GSCSI) Integration Module.

Loads monthly GSCSI values and converts them into stress multipliers
using percentile-based thresholds for low/medium/high scenarios.

Reference:
    World Bank (2024). Global Supply Chain Stress Index.

Author: Malek Karoui
Course: CS4982 - Winter 2026
"""

from typing import Dict

import numpy as np
import pandas as pd

import config

logger = config.setup_logging()


class GCSIStressModel:
    """
    Manages GSCSI data and provides scenario-based stress multipliers.

    The model divides historical GSCSI values into three regimes
    using the 33rd and 66th percentile thresholds:
        - Low:    values ≤ P33
        - Medium: P33 < values < P66
        - High:   values ≥ P66

    Attributes
    ----------
    data : pd.DataFrame
        The loaded GSCSI time series.
    thresholds : dict
        Computed percentile boundaries.
    multipliers : dict
        Scenario → float multiplier mapping.
    """

    def __init__(self, path: str = None):
        self.path = path or config.GCSI_CSV
        self.data = self._load()
        self.thresholds = self._compute_thresholds()
        self.multipliers = self._compute_multipliers()

    def _load(self) -> pd.DataFrame:
        """Load GCSI CSV and validate."""
        try:
            df = pd.read_csv(self.path)
            if "value" not in df.columns:
                raise ValueError("GCSI CSV must contain a 'value' column.")
            df = df.dropna(subset=["value"])
            logger.info("GSCSI loaded: %d data points.", len(df))
            return df
        except FileNotFoundError:
            logger.warning("GSCSI file not found at %s. Using default.", self.path)
            return pd.DataFrame({"value": [0.5, 1.0, 1.5]})

    def _compute_thresholds(self) -> Dict[str, float]:
        """Compute percentile thresholds from data."""
        values = self.data["value"]
        return {
            "p33": float(np.percentile(values, config.GCSI_LOW_PERCENTILE)),
            "p66": float(np.percentile(values, config.GCSI_HIGH_PERCENTILE)),
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
        }

    def _compute_multipliers(self) -> Dict[str, float]:
        """
        Compute the average GSCSI value within each stress regime.
        These serve as multipliers for failure propagation.
        """
        values = self.data["value"]
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
        """
        Returns the stress multiplier for a given scenario.

        Parameters
        ----------
        scenario : str
            One of 'low', 'medium', 'high'.

        Returns
        -------
        float
            The stress multiplier value.
        """
        return self.multipliers.get(scenario.lower(), 1.0)

    def get_summary(self) -> dict:
        """Returns a summary for display in the dashboard."""
        return {
            "data_points": len(self.data),
            **self.thresholds,
            **{f"mult_{k}": v for k, v in self.multipliers.items()},
        }


# Module-level convenience function (backward compatible)
_model = None

def get_stress_multiplier(scenario: str = "medium") -> float:
    """
    Convenience function for backward compatibility.
    Lazily initializes the GCSIStressModel singleton.
    """
    global _model
    if _model is None:
        _model = GCSIStressModel()
    return _model.get_multiplier(scenario)


if __name__ == "__main__":
    model = GCSIStressModel()
    print("GSCSI Summary:")
    for k, v in model.get_summary().items():
        print(f"  {k}: {v}")