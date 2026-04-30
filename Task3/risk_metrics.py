from __future__ import annotations

import math
from typing import Any, Dict, Iterable, Mapping


def _as_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be numeric") from exc


def _validate_portfolio(portfolio: Mapping[str, Any]) -> None:
    required_keys = ("total_value_inr", "monthly_expenses_inr", "assets")
    missing_keys = [key for key in required_keys if key not in portfolio]
    if missing_keys:
        raise ValueError(f"portfolio is missing required keys: {', '.join(missing_keys)}")

    assets = portfolio["assets"]
    if not isinstance(assets, list):
        raise ValueError("portfolio['assets'] must be a list")

    _as_float(portfolio["total_value_inr"], "total_value_inr")
    _as_float(portfolio["monthly_expenses_inr"], "monthly_expenses_inr")

    for index, asset in enumerate(assets):
        if not isinstance(asset, Mapping):
            raise ValueError(f"asset at index {index} must be a mapping")
        for key in ("name", "allocation_pct", "expected_crash_pct"):
            if key not in asset:
                raise ValueError(f"asset at index {index} is missing '{key}'")

        allocation_pct = _as_float(asset["allocation_pct"], f"assets[{index}].allocation_pct")
        if allocation_pct < 0 or allocation_pct > 100:
            asset_name = str(asset.get("name", index))
            raise ValueError(f"Invalid allocation for {asset_name}")

        _as_float(asset["expected_crash_pct"], f"assets[{index}].expected_crash_pct")


def compute_post_crash_value(portfolio: Mapping[str, Any], crash_multiplier: float = 1.0) -> float:
    total_value = _as_float(portfolio["total_value_inr"], "total_value_inr")
    assets = portfolio.get("assets", [])

    post_crash_value = 0.0
    for asset in assets:
        allocation_pct = _as_float(asset["allocation_pct"], "allocation_pct")
        crash_pct = _as_float(asset["expected_crash_pct"], "expected_crash_pct")
        asset_value = total_value * (allocation_pct / 100.0)
        adjusted_crash_pct = crash_pct * crash_multiplier
        post_crash_asset_value = asset_value * (1.0 + adjusted_crash_pct / 100.0)
        post_crash_value += max(0.0, post_crash_asset_value)

    return max(0.0, post_crash_value)


def compute_runway(post_crash_value: float, monthly_expenses_inr: Any) -> float:
    monthly_expenses = _as_float(monthly_expenses_inr, "monthly_expenses_inr")
    if monthly_expenses < 0:
        raise ValueError("monthly_expenses_inr cannot be negative")
    if monthly_expenses == 0:
        return math.inf
    return max(0.0, post_crash_value) / monthly_expenses


def compute_ruin_test(runway_months: float) -> str:
    return "PASS" if runway_months > 12 else "FAIL"


def find_largest_risk_asset(assets: Iterable[Mapping[str, Any]]) -> str | None:
    largest_asset_name: str | None = None
    largest_risk_score = float("-inf")

    for asset in assets:
        allocation_pct = _as_float(asset["allocation_pct"], "allocation_pct")
        crash_pct = abs(_as_float(asset["expected_crash_pct"], "expected_crash_pct"))
        risk_score = allocation_pct * crash_pct
        if risk_score > largest_risk_score:
            largest_risk_score = risk_score
            largest_asset_name = str(asset["name"])

    return largest_asset_name


def check_concentration(assets: Iterable[Mapping[str, Any]]) -> bool:
    return any(_as_float(asset["allocation_pct"], "allocation_pct") > 40 for asset in assets)


def compute_risk_metrics(portfolio: Mapping[str, Any]) -> Dict[str, Any]:
    _validate_portfolio(portfolio)

    assets = portfolio["assets"]
    post_crash_value = compute_post_crash_value(portfolio, crash_multiplier=1.0)
    runway_months = compute_runway(post_crash_value, portfolio["monthly_expenses_inr"])

    return {
        "post_crash_value": post_crash_value,
        "runway_months": runway_months,
        "ruin_test": compute_ruin_test(runway_months),
        "largest_risk_asset": find_largest_risk_asset(assets),
        "concentration_warning": check_concentration(assets),
    }
