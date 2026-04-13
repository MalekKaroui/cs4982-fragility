"""
GSCSI loader + stress scenario helpers.

Provides:
- load_gcsi(): returns a pandas Series of GSCSI values
- get_stress_multipliers(): dict with low/medium/high multipliers
- get_stress_multiplier(level): returns multiplier for a given level
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from . import config

logger = logging.getLogger(__name__)


def _pick_value_column(df: pd.DataFrame) -> str:
    """
    Pick a likely numeric column containing GSCSI values.
    Tries common names; otherwise picks the first numeric column.
    """
    # common column names
    candidates = ["GSCSI", "gscsi", "value", "Value", "stress", "Stress", "index", "Index"]
    for c in candidates:
        if c in df.columns and pd.api.types.is_numeric_dtype(df[c]):
            return c

    # fallback: first numeric column
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric_cols:
        raise ValueError(
            f"No numeric column found in GSCSI CSV. Columns: {list(df.columns)}"
        )
    return numeric_cols[0]


def load_gcsi(csv_path: Optional[Path] = None) -> pd.Series:
    """
    Load GSCSI values from CSV and return as a clean numeric Series.
    """
    csv_path = Path(csv_path) if csv_path else config.GCSI_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"GSCSI file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    value_col = _pick_value_column(df)

    s = pd.to_numeric(df[value_col], errors="coerce").dropna().astype(float)
    if len(s) == 0:
        raise ValueError(f"GSCSI series is empty after cleaning: {csv_path}")

    logger.info("Loaded GSCSI series: n=%d (column=%s)", len(s), value_col)
    return s


def get_stress_multipliers(
    csv_path: Optional[Path] = None,
    low_percentile: float = 0.33,
    high_percentile: float = 0.66,
) -> Dict[str, float]:
    """
    Derive low/medium/high stress multipliers from the empirical GSCSI distribution.

    - low  = 33rd percentile
    - med  = median (50th percentile)
    - high = 66th percentile

    This matches your report design and typically yields values like:
    low ≈ 0.3125, med ≈ 0.7000, high ≈ 1.4375 (depending on CSV contents).
    """
    s = load_gcsi(csv_path)

    low = float(s.quantile(low_percentile))
    med = float(s.quantile(0.50))
    high = float(s.quantile(high_percentile))

    return {"low": low, "medium": med, "high": high}


def get_stress_multiplier(level: str, csv_path: Optional[Path] = None) -> float:
    """
    Convenience getter used by simulation code.
    level: 'low' | 'medium' | 'high'
    """
    level = level.strip().lower()
    multipliers = get_stress_multipliers(csv_path)

    if level not in multipliers:
        raise ValueError(f"Unknown stress level '{level}'. Use: low, medium, high")

    return multipliers[level]