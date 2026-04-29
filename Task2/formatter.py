"""Table formatting helpers for Task 2."""

from __future__ import annotations

from typing import Iterable

from tabulate import tabulate


def format_price(value: object) -> str:
    if value in {None, "N/A"}:
        return "N/A"

    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return "N/A"


def render_table(rows: Iterable[dict[str, object]]) -> str:
    table_rows = []
    for row in rows:
        table_rows.append(
            [
                row.get("asset", "N/A"),
                format_price(row.get("price")),
                row.get("currency", "N/A"),
                row.get("timestamp", "N/A"),
            ]
        )

    return tabulate(table_rows, headers=["Asset", "Price", "Currency", "Timestamp"], tablefmt="grid")