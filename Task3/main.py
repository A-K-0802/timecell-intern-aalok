import argparse
import json
import math
from rich.console import Console

from input_loader import load_portfolio
from risk_metrics import compute_risk_metrics
from prompt_builder import build_prompt
from llm_client import call_gemini
from parser import parse_structured_output
from utils import log_info, log_json
from config import DEFAULT_TONE

console = Console()


def _validate_portfolio_basic(portfolio: dict) -> None:
    # basic checks
    if "total_value_inr" not in portfolio or "monthly_expenses_inr" not in portfolio:
        raise ValueError("portfolio missing required numeric keys")
    if "assets" not in portfolio or not isinstance(portfolio["assets"], list):
        raise ValueError("portfolio['assets'] must be a list")
    total_alloc = sum(float(a.get("allocation_pct", 0)) for a in portfolio["assets"])
    if total_alloc < 90 or total_alloc > 110:
        console.print(f"[yellow]Warning:[/yellow] allocations sum to {total_alloc}%.")


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Portfolio Explainer")
    parser.add_argument("--input-mode", choices=["python", "json"], default="python")
    parser.add_argument("--file", help="path to json or python input file")
    parser.add_argument("--tone", choices=["beginner", "experienced", "expert"], default=DEFAULT_TONE)
    parser.add_argument("--raw-only", action="store_true", help="only print raw LLM output")
    args = parser.parse_args(argv)

    portfolio = load_portfolio(args.input_mode, args.file)
    _validate_portfolio_basic(portfolio)

    # reuse existing Task1 compute_risk_metrics implementation
    metrics = compute_risk_metrics(portfolio)

    prompt = build_prompt(portfolio, metrics, tone=args.tone)

    console.rule("=== RAW LLM RESPONSE ===")
    try:
        raw = call_gemini(prompt)
        console.print(raw)
    except Exception as exc:
        console.print(f"[red]LLM call failed:[/red] {exc}")
        return 2

    if args.raw_only:
        return 0

    console.rule("=== PARSED OUTPUT ===")
    try:
        parsed = parse_structured_output(raw)
    except Exception as exc:
        console.print(f"[red]Failed to parse LLM output:[/red] {exc}")
        # retry attempt: ask for JSON-only
        try:
            retry_prompt = prompt + "\nRespond with exact JSON only, nothing else."
            raw2 = call_gemini(retry_prompt)
            console.print("[yellow]Retry raw response:[/yellow]")
            console.print(raw2)
            parsed = parse_structured_output(raw2)
        except Exception as exc2:
            console.print(f"[red]Retry parse failed:[/red] {exc2}")
            return 3

    # display parsed
    if isinstance(parsed, dict):
        for key in ("summary", "good_thing", "improvement", "verdict"):
            value = parsed.get(key, "")
            console.print(f"{key.capitalize()}: {value}")
    else:
        console.print(str(parsed))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
