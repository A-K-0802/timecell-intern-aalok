"""Task 2 entry point: fetch and print asset prices."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import datetime
from zoneinfo import ZoneInfo

from datafetch import fetch_crypto_data, fetch_stock_data
from formatter import render_table
from logger import get_logger

DEFAULT_SELECTION = ("bitcoin", "ethereum", "nifty50")

CRYPTO_CATALOG = {
	"bitcoin": {"name": "BTC", "id": "bitcoin", "currency": "USD"},
	"btc": {"name": "BTC", "id": "bitcoin", "currency": "USD"},
	"ethereum": {"name": "ETH", "id": "ethereum", "currency": "USD"},
	"eth": {"name": "ETH", "id": "ethereum", "currency": "USD"},
	"dogecoin": {"name": "DOGE", "id": "dogecoin", "currency": "USD"},
	"doge": {"name": "DOGE", "id": "dogecoin", "currency": "USD"},
	"solana": {"name": "SOL", "id": "solana", "currency": "USD"},
	"sol": {"name": "SOL", "id": "solana", "currency": "USD"},
}

STOCK_CATALOG = {
	"nifty50": {"name": "NIFTY50", "id": "^NSEI", "currency": "INR"},
	"nsei": {"name": "NIFTY50", "id": "^NSEI", "currency": "INR"},
	"sensex": {"name": "SENSEX", "id": "^BSESN", "currency": "INR"},
	"reliance": {"name": "RELIANCE", "id": "RELIANCE.NS", "currency": "INR"},
	"tcs": {"name": "TCS", "id": "TCS.NS", "currency": "INR"},
}


def parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Fetch live prices for crypto assets and stocks/indexes using free public APIs.",
	)
	parser.add_argument(
		"--crypto",
		action="append",
		nargs="+",
		default=[],
		metavar="ASSET",
		help="Repeatable list of crypto assets or CoinGecko ids (for example: bitcoin dogecoin).",
	)
	parser.add_argument(
		"--stock",
		action="append",
		nargs="+",
		default=[],
		metavar="TICKER",
		help="Repeatable list of stock/index tickers (for example: ^NSEI RELIANCE.NS).",
	)
	parser.add_argument(
		"--list-assets",
		action="store_true",
		help="Show the supported friendly asset aliases and exit.",
	)
	return parser.parse_args(argv)


def print_supported_assets() -> None:
	print("Supported crypto aliases:")
	for alias, spec in CRYPTO_CATALOG.items():
		print(f"  {alias:<12} -> {spec['name']} ({spec['id']}, {spec['currency']})")

	print()
	print("Supported stock/index aliases:")
	for alias, spec in STOCK_CATALOG.items():
		print(f"  {alias:<12} -> {spec['name']} ({spec['id']}, {spec['currency']})")


def _normalize_crypto_asset(raw_value: str) -> dict[str, str]:
	lookup = CRYPTO_CATALOG.get(raw_value.lower())
	if lookup is not None:
		return lookup

	return {
		"name": raw_value.upper(),
		"id": raw_value.lower(),
		"currency": "USD",
	}


def _normalize_stock_asset(raw_value: str) -> dict[str, str]:
	lookup = STOCK_CATALOG.get(raw_value.lower())
	if lookup is not None:
		return lookup

	currency = "INR" if raw_value.endswith(".NS") or raw_value.endswith(".BO") or raw_value.startswith("^") else "USD"
	return {
		"name": raw_value.replace(".NS", "").replace(".BO", "").replace("^", "").upper(),
		"id": raw_value,
		"currency": currency,
	}


def build_asset_selection(args: argparse.Namespace) -> list[dict[str, str]]:
	if args.list_assets:
		return []

	selected_assets: list[dict[str, str]] = []
	selected_crypto = [item for group in args.crypto for item in group]
	selected_stock = [item for group in args.stock for item in group]

	if not selected_crypto and not selected_stock:
		selected_crypto = [asset for asset in DEFAULT_SELECTION if asset in CRYPTO_CATALOG]
		selected_stock = [asset for asset in DEFAULT_SELECTION if asset in STOCK_CATALOG]

	for crypto_value in selected_crypto:
		selected_assets.append({"type": "crypto", **_normalize_crypto_asset(crypto_value)})

	for stock_value in selected_stock:
		selected_assets.append({"type": "stock", **_normalize_stock_asset(stock_value)})

	return selected_assets


def validate_selection(assets: list[dict[str, str]], logger) -> bool:
	if not assets:
		return True

	if len(assets) < 3:
		logger.error("Please provide at least 3 assets in total.")
		return False

	has_crypto = any(asset["type"] == "crypto" for asset in assets)
	has_stock = any(asset["type"] == "stock" for asset in assets)
	if not has_crypto or not has_stock:
		logger.error("Please include at least one crypto asset and at least one stock/index asset.")
		return False

	return True


def fetch_all_assets(fetched_at: datetime, assets: list[dict[str, str]]) -> list[dict[str, object]]:
	logger = get_logger()
	timestamp_text = fetched_at.strftime("%Y-%m-%d %H:%M:%S IST")

	results: list[dict[str, object]] = []
	for asset in assets:
		if asset["type"] == "crypto":
			result = fetch_crypto_data(asset["name"], asset["id"], fetched_at, asset["currency"])
		else:
			result = fetch_stock_data(asset["name"], asset["id"], fetched_at)

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


def main(argv: Sequence[str] | None = None) -> int:
	logger = get_logger()
	args = parse_arguments(argv)
	if args.list_assets:
		print_supported_assets()
		return 0

	assets = build_asset_selection(args)
	if not validate_selection(assets, logger):
		return 1

	fetched_at = datetime.now(ZoneInfo("Asia/Kolkata"))
	print(f"Asset Prices — fetched at {fetched_at.strftime('%Y-%m-%d %H:%M:%S IST')}")
	print(render_table(fetch_all_assets(fetched_at, assets)))
	logger.info("Task 2 run completed")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
