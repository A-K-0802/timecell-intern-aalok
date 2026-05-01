"""Risk analysis module - wraps Task1 risk metrics."""

import sys
from pathlib import Path
from typing import Any, Dict, Mapping

# Add Task1 to path so we can import risk_metrics
task1_path = Path(__file__).parent.parent / "Task1"
if str(task1_path) not in sys.path:
    sys.path.insert(0, str(task1_path))

from risk_metrics import (
    compute_risk_metrics as task1_compute_risk_metrics,
    compute_scenario_comparison,
    compute_post_crash_value,
    compute_runway,
)


def compute_risk_metrics(portfolio: Mapping[str, Any]) -> Dict[str, Any]:
    """
    Compute risk metrics for a portfolio using Task1 implementation.
    
    Returns severe crash scenario metrics:
    - post_crash_value: Value after severe crash
    - runway_months: Months of runway after crash
    - ruin_test: PASS/FAIL if runway > 12 months
    - largest_risk_asset: Asset with highest risk score
    - concentration_warning: Boolean for >40% in single asset
    """
    return task1_compute_risk_metrics(portfolio)


def compute_all_scenarios(portfolio: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Compute both severe and moderate crash scenarios.
    
    Returns:
    {
        "severe": { metrics for severe crash },
        "moderate": { metrics for moderate crash },
        "current": { metrics for current portfolio }
    }
    """
    scenarios = compute_scenario_comparison(portfolio)
    
    # Also compute current portfolio metrics
    total_value = float(portfolio["total_value_inr"])
    monthly_expenses = float(portfolio["monthly_expenses_inr"])
    current_runway = compute_runway(total_value, monthly_expenses)
    
    scenarios["current"] = {
        "post_crash_value": total_value,
        "runway_months": current_runway,
        "ruin_test": "PASS" if current_runway > 12 else "FAIL",
    }
    
    return scenarios


def get_asset_risk_scores(portfolio: Mapping[str, Any]) -> list:
    """
    Calculate risk score for each asset (allocation_pct * abs(crash_pct)).
    
    Returns list of dicts with asset info and risk scores.
    """
    assets = portfolio.get("assets", [])
    risk_scores = []
    
    for asset in assets:
        allocation_pct = float(asset["allocation_pct"])
        crash_pct = abs(float(asset["expected_crash_pct"]))
        risk_score = allocation_pct * crash_pct
        
        risk_scores.append({
            "name": asset["name"],
            "allocation_pct": allocation_pct,
            "crash_pct": crash_pct,
            "risk_score": risk_score,
        })
    
    return sorted(risk_scores, key=lambda x: x["risk_score"], reverse=True)
