from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable


ROOT = Path(__file__).resolve().parent.parent
TEST_ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from input_loader import load_from_json_file
from prompt_builder import build_prompt
from risk_metrics import compute_risk_metrics
from parser import parse_structured_output


ALLOWED_VERDICTS = {"Aggressive", "Balanced", "Conservative"}
REQUIRED_OUTPUT_KEYS = {"summary", "good_thing", "improvement", "verdict"}


def load_cases(manifest_path: Path) -> list[Dict[str, Any]]:
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("cases manifest must be a JSON array")
    return data


def resolve_case_path(relative_path: str) -> Path:
    path = (TEST_ROOT / relative_path).resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def validate_output_schema(parsed: Dict[str, Any]) -> list[str]:
    issues: list[str] = []
    missing = sorted(REQUIRED_OUTPUT_KEYS - set(parsed))
    if missing:
        issues.append(f"missing keys: {', '.join(missing)}")

    verdict = parsed.get("verdict")
    if verdict not in ALLOWED_VERDICTS:
        issues.append(f"invalid verdict: {verdict!r}")

    for key in REQUIRED_OUTPUT_KEYS - {"verdict"}:
        value = parsed.get(key)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"{key} must be a non-empty string")

    return issues


def run_input_case(case: Dict[str, Any]) -> tuple[bool, str]:
    path = resolve_case_path(case["path"])
    expected_category = case.get("expected_category", "")

    try:
        portfolio = load_from_json_file(str(path))
        metrics = compute_risk_metrics(portfolio)
        prompt = build_prompt(portfolio, metrics)
    except Exception as exc:
        if expected_category == "invalid":
            return True, f"expected failure: {exc}"
        return False, f"unexpected failure: {exc}"

    if expected_category == "invalid":
        return False, "expected the case to fail, but load/metrics/prompt all succeeded"

    prompt_size = len(prompt)
    return True, f"loaded and built prompt ({prompt_size} chars); metrics keys={sorted(metrics)}"


def run_output_case(case: Dict[str, Any]) -> tuple[bool, str]:
    path = resolve_case_path(case["path"])
    expected_category = case.get("expected_category", "")
    raw_text = path.read_text(encoding="utf-8")

    try:
        parsed = parse_structured_output(raw_text)
    except Exception as exc:
        if expected_category == "parse_error":
            return True, f"expected parse failure: {exc}"
        return False, f"unexpected parse failure: {exc}"

    if not isinstance(parsed, dict):
        return False, f"parser returned unexpected type: {type(parsed).__name__}"

    issues = validate_output_schema(parsed)
    if expected_category == "parseable_json":
        if issues:
            return False, "; ".join(issues)
        return True, "parsed and passed strict output checks"

    if expected_category == "schema_error":
        if issues:
            return True, "; ".join(issues)
        return False, "expected schema issues, but output passed strict checks"

    if expected_category == "parse_error":
        return False, "expected parser to fail, but it returned structured data"

    return False, f"unknown expected category: {expected_category!r}"


def iter_selected_cases(cases: Iterable[Dict[str, Any]], focus: str) -> Iterable[Dict[str, Any]]:
    if focus == "all":
        return cases
    return [case for case in cases if case.get("type") == focus]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Task3 fixture smoke tests")
    parser.add_argument("--manifest", default=str(TEST_ROOT / "cases.json"), help="path to the fixture manifest")
    parser.add_argument("--focus", choices=["all", "input", "output"], default="all", help="limit cases to one fixture type")
    parser.add_argument("--stop-on-fail", action="store_true", help="stop after the first failing case")
    args = parser.parse_args()

    cases = load_cases(Path(args.manifest))
    selected_cases = list(iter_selected_cases(cases, args.focus))

    total = len(selected_cases)
    passed = 0

    print(f"Running Task3 fixtures from {args.manifest}")
    print(f"Selected cases: {total}\n")

    for index, case in enumerate(selected_cases, start=1):
        case_id = case.get("id", f"case-{index}")
        case_type = case.get("type", "unknown")
        print(f"[{index}/{total}] {case_id} ({case_type})")

        if case_type == "input":
            ok, message = run_input_case(case)
        elif case_type == "output":
            ok, message = run_output_case(case)
        else:
            ok, message = False, f"unknown case type: {case_type!r}"

        status = "PASS" if ok else "FAIL"
        print(f"  {status}: {message}\n")

        if ok:
            passed += 1
        elif args.stop_on_fail:
            break

    print(f"Summary: {passed}/{total} passed")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())