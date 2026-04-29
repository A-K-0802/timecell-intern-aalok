"""Task 2 entry point: fetch and print asset prices."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from datafetch import fetch_crypto_data, fetch_stock_data
from formatter import render_table
from logger import get_logger

ASSETS = (
	{"type": "crypto", "name": "BTC", "id": "bitcoin", "currency": "USD"},
	{"type": "crypto", "name": "ETH", "id": "ethereum", "currency": "USD"},
	{"type": "stock", "name": "NIFTY50", "id": "^NSEI", "currency": "INR"},
)


def fetch_all_assets(fetched_at: datetime) -> list[dict[str, object]]:
	logger = get_logger()
	timestamp_text = fetched_at.strftime("%Y-%m-%d %H:%M:%S IST")

	results: list[dict[str, object]] = []
	for asset in ASSETS:
		if asset["type"] == "crypto":
			result = fetch_crypto_data(str(asset["name"]), str(asset["id"]), fetched_at, str(asset["currency"]))
		else:
			result = fetch_stock_data(str(asset["name"]), str(asset["id"]), fetched_at)

		if result is None:
			logger.error("Using N/A row for %s after fetch failure", asset["name"])
			results.append(
				{
					"asset": asset["name"],
					"price": "N/A",
					"currency": asset["currency"],
					"timestamp": timestamp_text,
				}
			)
			continue

		results.append(result)

	return results


def main() -> None:
	logger = get_logger()
	fetched_at = datetime.now(ZoneInfo("Asia/Kolkata"))
	print(f"Asset Prices — fetched at {fetched_at.strftime('%Y-%m-%d %H:%M:%S IST')}")
	print(render_table(fetch_all_assets(fetched_at)))
	logger.info("Task 2 run completed")


if __name__ == "__main__":
	main()
