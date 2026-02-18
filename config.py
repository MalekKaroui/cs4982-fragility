"""
config.py
=========
Central configuration module for the Operational Fragility Modeling Framework.

All tunable parameters, file paths, and constants are defined here
to ensure reproducibility and easy experimentation.

Author: Malek Karoui
Course: CS4982 - Winter 2026
University of New Brunswick
"""

from pathlib import Path
import logging

# ──────────────────────────────────────────────
# PROJECT PATHS
# ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"

NODE_CSV = DATA_DIR / "node.csv"
EDGE_CSV = DATA_DIR / "edge.csv"
GCSI_CSV = DATA_DIR / "gcsi.csv"

# ──────────────────────────────────────────────
# SIMULATION PARAMETERS
# ──────────────────────────────────────────────
RANDOM_SEED = 42
DEFAULT_N_CASCADES = 500          # Monte Carlo iterations per node
STRESS_LEVELS = ["low", "medium", "high"]

# Edge weight normalization range
WEIGHT_MIN = 0.10                 # Minimum propagation probability
WEIGHT_MAX = 0.65                 # Maximum propagation probability

# Base failure probability range for nodes (assigned randomly)
BASE_FAIL_PROB_MIN = 0.03
BASE_FAIL_PROB_MAX = 0.12

# Convergence test parameters
CONVERGENCE_SAMPLE_SIZES = [50, 100, 200, 300, 400, 500]

# ──────────────────────────────────────────────
# GCSI STRESS MULTIPLIER PERCENTILE THRESHOLDS
# ──────────────────────────────────────────────
GCSI_LOW_PERCENTILE = 33
GCSI_HIGH_PERCENTILE = 66

# ──────────────────────────────────────────────
# VISUALIZATION
# ──────────────────────────────────────────────
TOP_K_DEFAULT = 10
NETWORK_LAYOUT_SEED = 42
COLORSCALE = "YlOrRd"
DPI = 300

# ──────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_LEVEL = logging.INFO


def setup_logging():
    """Configure project-wide logging."""
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
    return logging.getLogger("fragility_framework")


def ensure_directories():
    """Create all required output directories."""
    for d in [
        RESULTS_DIR,
        FIGURES_DIR,
        FIGURES_DIR / "histograms",
        FIGURES_DIR / "heatmaps",
        FIGURES_DIR / "topk",
        FIGURES_DIR / "convergence",
    ]:
        d.mkdir(parents=True, exist_ok=True)