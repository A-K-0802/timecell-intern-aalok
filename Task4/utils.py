"""Utility functions for Task4 Portfolio Visualizer."""

import os
from pathlib import Path
from typing import Any
from rich.console import Console

console = Console(force_terminal=True, no_color=False, legacy_windows=False)


def ensure_output_dir(output_dir: str) -> Path:
    """Create output directory if it doesn't exist."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def log_info(message: str) -> None:
    """Log informational message."""
    console.print(f"[blue][INFO][/blue] {message}")


def log_success(message: str) -> None:
    """Log success message."""
    console.print(f"[green][OK][/green] {message}")


def log_warning(message: str) -> None:
    """Log warning message."""
    console.print(f"[yellow][WARN][/yellow] {message}")


def log_error(message: str) -> None:
    """Log error message."""
    console.print(f"[red][ERR][/red] {message}")


def format_inr(value: float) -> str:
    """Format value as INR currency."""
    if value >= 1_000_000:
        return f"Rs.{value / 1_000_000:.2f}Cr"
    elif value >= 1_000:
        return f"Rs.{value / 1_000:.2f}K"
    else:
        return f"Rs.{value:.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.2f}%"


def get_plot_path(output_dir: str, plot_filename: str) -> str:
    """Get full path for a plot file."""
    return str(Path(output_dir) / plot_filename)
