"""Configuration and constants for Task4 Portfolio Visualizer."""

# API & LLM Settings
DEFAULT_TONE = "beginner"
GEMINI_MODEL = "gemini-2.5-flash"

# Visualization Settings
PLOT_STYLE = "seaborn-v0_8-darkgrid"
COLOR_PALETTE = "husl"
FIGURE_DPI = 100
FIGURE_WIDTH = 12
FIGURE_HEIGHT = 6

# Risk Thresholds
CONCENTRATION_THRESHOLD = 40.0  # %
RUNWAY_PASS_THRESHOLD = 12  # months
CRASH_MULTIPLIER_SEVERE = 1.0
CRASH_MULTIPLIER_MODERATE = 0.5

# File Defaults
DEFAULT_INPUT_FILE = "python_dict_input.py"
DEFAULT_OUTPUT_DIR = "./outputs"

# Plot file names
PLOT_ALLOCATION = "asset_allocation.png"
PLOT_RUNWAY = "runway_comparison.png"
PLOT_RISK_SCORES = "risk_scores.png"
PLOT_POST_CRASH = "post_crash_value.png"
PLOT_CONCENTRATION = "concentration_risk.png"
