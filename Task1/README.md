# Task 1 - Risk Metrics Analysis

This folder contains a standalone Python solution for the portfolio crash-risk problem.

## Files

- `risk_metrics.py`: core implementation, bonus scenario comparison, and CLI chart output
- `solution.py`: convenience import surface for the required functions
- `main.py`: thin entry point so the task can be run directly

## How to run

From the `Task1` folder:

```bash
python main.py
```

Optional flags:

- `--input-file path.json` reads the portfolio from a JSON file
- `--python-input` reads `python_dict_input.py` by default, or `--python-input path.py` can be used for a different Python file
- `--compare-scenarios` prints severe and moderate crash metrics side by side
- `--chart` prints a simple command-line allocation bar chart

## How to input custom portfolios

The script supports three input methods, in this order of precedence:

1. `--input-file`
	- Reads a portfolio JSON file from disk.
	- Example:

	```bash
	python main.py --input-file portfolio.json
	```

2. `--python-input`
	- Reads a Python file that contains a variable named `portfolio`.
	- The file is parsed safely and the dictionary is not executed as code.
	- If you do not provide a path, the program uses `python_dict_input.py` in the `Task1` folder.
	- Example:

	```bash
	python main.py --python-input
	```

3. JSON string argument
	- Pass the portfolio directly as a single JSON string argument.
	- Use valid JSON syntax: double quotes, no trailing commas, no numeric separators like `_`.
	- Example:

	```bash
	python main.py '{"total_value_inr":10000000,"monthly_expenses_inr":80000,"assets":[{"name":"BTC","allocation_pct":30,"expected_crash_pct":-80},{"name":"NIFTY50","allocation_pct":40,"expected_crash_pct":-40},{"name":"GOLD","allocation_pct":20,"expected_crash_pct":-15},{"name":"CASH","allocation_pct":10,"expected_crash_pct":0}]}'
	```

4. Interactive prompt
	- If no input file and no JSON string are provided, the program prompts with `portfolio = `.
	- Paste the JSON and press Enter.

The optional `--compare-scenarios` and `--chart` flags work with all input methods.

## AI usage

ChatGPT was prompted to analyze the problem statement and create a roadmap for the problem statement, the prompt also explicitly mentioned that the output given by GPT will be checked and its important for GPT to give its best and save its reputation

Copilot was used to help structure the solution, keep the logic modular, and document the implementation.

## Notes

- The solution handles empty assets, zero monthly expenses, and general input validation.
- Allocation percentages are validated strictly and must stay within the inclusive range 0 to 100.
- The required `compute_risk_metrics(portfolio)` function returns the severe crash metrics dictionary.


## Explaination of TASK1

Loom link - https://www.loom.com/share/dffb030ef5ea421eb2b815591c8c5b01