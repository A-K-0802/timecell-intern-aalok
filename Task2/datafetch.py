"""Data fetching helpers for Task 2."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import requests
import yfinance as yf

from logger import get_logger

LOGGER = get_logger()


def _format_timestamp(timestamp: datetime) -> str:
    return timestamp.strftime("%Y-%m-%d %H:%M:%S IST")


def _build_row(asset: str, price: float, currency: str, timestamp: str) -> dict[str, Any]:
    return {
        "asset": asset,
        "price": round(price, 2),
        "currency": currency,
        "timestamp": timestamp,
    }


def fetch_stock_data(asset_name: str, ticker_symbol: str, timestamp: datetime) -> Optional[dict[str, Any]]:
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.fast_info
        price = info.get("lastPrice")
        currency = info.get("currency")

        if price is None:
            history = ticker.history(period="1d", interval="1m")
            if history.empty:
                raise ValueError(f"No market data returned for {ticker_symbol}")
            price = float(history["Close"].iloc[-1])

        if not currency:
            currency = "INR" if ticker_symbol.endswith(".NS") or ticker_symbol.startswith("^") else "USD"

        LOGGER.info("Fetched stock/index %s (%s)", asset_name, ticker_symbol)
        return _build_row(asset_name, float(price), currency, _format_timestamp(timestamp))
    except Exception as exc:
        LOGGER.error("Failed to fetch stock/index %s (%s): %s", asset_name, ticker_symbol, exc)
        return None


def fetch_crypto_data(asset_name: str, coin_id: str, timestamp: datetime, currency: str = "USD") -> Optional[dict[str, Any]]:
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin_id, "vs_currencies": currency.lower()},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()

        if coin_id not in payload or currency.lower() not in payload[coin_id]:
            raise ValueError(f"No price found for {coin_id}")

        price = float(payload[coin_id][currency.lower()])
        LOGGER.info("Fetched crypto %s (%s)", asset_name, coin_id)
        return _build_row(asset_name, price, currency, _format_timestamp(timestamp))
    except Exception as exc:
        LOGGER.error("Failed to fetch crypto %s (%s): %s", asset_name, coin_id, exc)
        return None
