# Task 2 - Live Asset Price Fetcher

This folder contains a small CLI-based Python script that fetches live prices for crypto assets and stocks/indexes using free public APIs.

## What it does

- Fetches prices for at least 3 assets.
- Requires at least one crypto asset and one stock/index asset.
- Prints a clean table with asset name, price, currency, and fetch timestamp.
- Logs fetch failures and keeps going if one asset fails.

## Files

- `main.py` - CLI entry point and orchestration.
- `datafetch.py` - API calls for CoinGecko and yfinance.
- `formatter.py` - table formatting helpers.
- `logger.py` - logging setup.
- `requirements.txt` - Python dependencies.

## How the CLI works

The script accepts repeatable arguments:

- `--crypto` for crypto assets or CoinGecko ids.
- `--stock` for stock or index tickers.
- `--list-assets` to show the built-in friendly aliases.

If no arguments are provided, the script uses the default set:

- BTC
- ETH
- NIFTY50

## Example usage

Run the default selection:

```bash
python main.py
```

Fetch custom crypto assets:

```bash
python main.py --crypto bitcoin dogecoin
```

Fetch custom stock/index assets:

```bash
python main.py --stock nsei reliance
```

Fetch both together:

```bash
python main.py --crypto bitcoin dogecoin --stock nsei reliance
```

Show the supported friendly aliases:

```bash
python main.py --list-assets
```

## Supported asset alias mapping

The script knows a small alias map so the user does not need to type labels or currencies manually.

- Crypto aliases like `bitcoin`, `btc`, `ethereum`, `eth`, `dogecoin`, `doge`, `solana`, `sol` map to a display label and CoinGecko id.
- Stock/index aliases like `nifty50`, `nsei`, `sensex`, `reliance`, `tcs` map to a display label and yfinance ticker.

If you pass a raw CoinGecko id or ticker that is not in the alias map, the script still tries to use it directly and infers a display label and currency.

## Code flow

1. `main.py` parses CLI arguments with `argparse`.
2. It converts the requested assets into a normalized internal format.
3. It generates one shared IST timestamp for the whole run.
4. It fetches each asset independently using `datafetch.py`.
5. It logs any fetch failure and continues with the remaining assets.
6. `formatter.py` prints the final table with aligned columns.

## Error handling

- If one API fails, the script logs the failure and still prints the rest.
- If the user provides fewer than 3 assets, or skips either crypto or stock/index, the script exits with an error message.
- If no arguments are supplied, the script falls back to the default 3-asset selection.

## Dependencies

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```


## Explaination of TASK 2

Loom link - https://www.loom.com/share/5a084188685744ddaf500a544fb95b67