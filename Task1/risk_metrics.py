"""Risk metrics calculator for a simple portfolio crash analysis.

The module keeps the core math separate from presentation so it can be reused
from scripts, tests, or a CLI entry point.
"""

from __future__ import annotations

import ast
import argparse
import json
import math
from pathlib import Path
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
            asset_name = str(asset["name"])
            raise ValueError(f"Invalid allocation for {asset_name}")

        _as_float(asset["expected_crash_pct"], f"assets[{index}].expected_crash_pct")


def compute_post_crash_value(
    portfolio: Mapping[str, Any],
    crash_multiplier: float = 1.0,
) -> float:
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


def compute_scenario_comparison(portfolio: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    _validate_portfolio(portfolio)

    severe = compute_risk_metrics(portfolio)
    moderate_post_crash_value = compute_post_crash_value(portfolio, crash_multiplier=0.5)
    moderate_runway_months = compute_runway(moderate_post_crash_value, portfolio["monthly_expenses_inr"])

    moderate = {
        "post_crash_value": moderate_post_crash_value,
        "runway_months": moderate_runway_months,
        "ruin_test": compute_ruin_test(moderate_runway_months),
        "largest_risk_asset": severe["largest_risk_asset"],
        "concentration_warning": severe["concentration_warning"],
    }

    return {"severe": severe, "moderate": moderate}


def print_allocation_chart(assets: Iterable[Mapping[str, Any]]) -> None:
    for asset in assets:
        name = str(asset["name"])
        allocation_pct = _as_float(asset["allocation_pct"], "allocation_pct")
        bar = "█" * int(allocation_pct // 2)
        print(f"{name:<10} | {bar} ({allocation_pct:g}%)")


def _sample_portfolio() -> Dict[str, Any]:
    return {
        "total_value_inr": 10_000_000,
        "monthly_expenses_inr": 80_000,
        "assets": [
            {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80},
            {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
            {"name": "GOLD", "allocation_pct": 20, "expected_crash_pct": -15},
            {"name": "CASH", "allocation_pct": 10, "expected_crash_pct": 0},
        ],
    }


def _load_portfolio_from_file(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    with path.open("r", encoding="utf-8-sig") as file_handle:
        return json.load(file_handle)


def _load_portfolio_from_json_string(portfolio_json: str) -> Dict[str, Any]:
    return json.loads(portfolio_json)


def _load_portfolio_from_python_file(file_path: str) -> Dict[str, Any]:
    path = Path(file_path)
    source = path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(path))

    for statement in module.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id == "portfolio":
                    value = ast.literal_eval(statement.value)
                    if not isinstance(value, dict):
                        raise ValueError("portfolio in python input file must be a dictionary")
                    return value

        if isinstance(statement, ast.AnnAssign):
            target = statement.target
            if isinstance(target, ast.Name) and target.id == "portfolio" and statement.value is not None:
                value = ast.literal_eval(statement.value)
                if not isinstance(value, dict):
                    raise ValueError("portfolio in python input file must be a dictionary")
                return value

    raise ValueError("python input file must define a portfolio dictionary")


def _prompt_for_portfolio() -> Dict[str, Any]:
    return json.loads(input("portfolio = "))


def _build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute portfolio crash risk metrics.")
    parser.add_argument(
        "portfolio_json",
        nargs="?",
        help="Optional JSON string containing the portfolio dictionary.",
    )
    parser.add_argument(
        "--input-file",
        help="Path to a JSON file containing the portfolio dictionary.",
    )
    parser.add_argument(
        "--python-input",
        "--python_input",
        dest="python_input",
        nargs="?",
        const="python_dict_input.py",
        help="Path to a Python file that defines a portfolio dictionary named portfolio. Defaults to python_dict_input.py when used without a path.",
    )
    parser.add_argument(
        "--compare-scenarios",
        action="store_true",
        help="Show severe and moderate crash metrics side by side.",
    )
    parser.add_argument(
        "--chart",
        action="store_true",
        help="Print a simple command-line allocation bar chart.",
    )
    return parser


def main() -> None:
    parser = _build_argument_parser()
    args = parser.parse_args()

    if args.input_file:
        portfolio = _load_portfolio_from_file(args.input_file)
    elif args.python_input:
        portfolio = _load_portfolio_from_python_file(args.python_input)
    elif args.portfolio_json is not None:
        portfolio = _load_portfolio_from_json_string(args.portfolio_json)
    else:
        portfolio = _prompt_for_portfolio()

    if args.chart:
        print_allocation_chart(portfolio["assets"])
        print()

    if args.compare_scenarios:
        print(
            json.dumps(
                compute_scenario_comparison(portfolio),
                indent=2,
                default=lambda value: "Infinity" if math.isinf(value) else value,
            )
        )
    else:
        print(
            json.dumps(
                compute_risk_metrics(portfolio),
                indent=2,
                default=lambda value: "Infinity" if math.isinf(value) else value,
            )
        )


if __name__ == "__main__":
    main()