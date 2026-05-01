# Task 4 - Portfolio Visualizer and AI Advisor (CLI)

## Overview

Task4 is a CLI integration layer that combines:
- Task1 risk metric functions for deterministic portfolio crash analysis
- Task3-style Gemini prompting and structured advice parsing

It prints portfolio and risk summaries in terminal tables, and saves all plots as PNG files in an output folder.

No code in Task1 or Task3 is modified.

---

## Reason for this solution

A lot of users may not be comfortable in working with terminal/CLI based outputs so, working with plots and graphs is a great way for users to visualize the problems within a portfolio. It reduces friction between the user and the product and makes the output easier to understand.

## What It Does

1. Loads a portfolio from JSON or Python file.
2. Computes severe/moderate/current risk scenarios using Task1 logic.
3. Generates five visualizations and saves them to an output directory.
4. Optionally calls Gemini to produce structured advice.
5. Prints results in a clean CLI format.

---

## File Structure

```text
Task4/
   README.md
   main.py
   config.py
   input_loader.py
   risk_analysis.py
   visualizer.py
   ai_advisor.py
   utils.py
   requirements.txt
   outputs/                 # generated at runtime
```

---

## CLI Arguments

```bash
python main.py [options]

Options:
   --input-mode {python,json,string}          default: python
   --input-file INPUT_FILE                     path for json/python mode
   --tone {beginner,experienced,expert}       default: beginner
   --output-dir OUTPUT_DIR                     default: ./outputs
   --no-ai                                     skip Gemini advice
   --compare-scenarios                         show detailed scenario comparison
```

Notes:
- `--input-mode python` auto-resolves to Task1 `python_dict_input.py` when `--input-file` is not provided.
- `--input-mode string` is wired in loader logic, but current CLI does not expose a direct JSON-string argument.

---

## Available Flags

This section lists all supported flags, their purpose, accepted values, and examples.

- `--input-mode {python,json,string}`
   - Purpose: Choose input source type.
   - Values: `python` (default), `json`, `string`.
   - Notes: `python` will look for a `portfolio` dict in a Python file (defaults to Task1/python_dict_input.py). `string` expects a JSON string (loader supports it programmatically).
   - Example: `--input-mode json`

- `--input-file INPUT_FILE`
   - Purpose: Path to the input file when using `--input-mode json` or `--input-mode python`.
   - Example: `--input-file sample_portfolio.json`

- `--tone {beginner,experienced,expert}`
   - Purpose: Control the language/tone of the AI advice.
   - Default: `beginner`.
   - Example: `--tone experienced`

- `--output-dir OUTPUT_DIR`
   - Purpose: Directory where PNG visualizations will be saved.
   - Default: `./outputs`.
   - Example: `--output-dir ./my_plots`

- `--no-ai`
   - Purpose: Skip calling the Gemini LLM and only produce metrics + plots.
   - Use when you don't have an API key or want a fast local run.
   - Example: `--no-ai`

- `--compare-scenarios`
   - Purpose: Request the program to compute and show severe, moderate, and current scenarios side-by-side.
   - Example: `--compare-scenarios`

Additional runtime configuration:

- `GEMINI_API_KEY` (environment variable)
   - Purpose: Provide Gemini/Google API key used by `ai_advisor.py`.
   - Usage (Windows PowerShell): `setx GEMINI_API_KEY "your_key_here"` or `set GEMINI_API_KEY=your_key_here` for current session.

Examples (copyable):

```bash
# Compute metrics and save plots only
python main.py --input-mode json --input-file sample_portfolio.json --no-ai

# Compute metrics, plots and request AI advice
set GEMINI_API_KEY=your_key_here
python main.py --input-mode json --input-file sample_portfolio.json --tone beginner

# Use Python-file input and save plots to custom directory
python main.py --input-mode python --input-file Task1/python_dict_input.py --output-dir ./reports --no-ai
```

---

## Quick Start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run without AI (metrics + plots only)

```bash
python main.py --input-mode json --input-file sample_portfolio.json --no-ai
```

### 3) Run with AI advice

Set environment variable first:

```bash
set GEMINI_API_KEY=your_api_key_here
python main.py --input-mode json --input-file sample_portfolio.json --tone beginner
```

### 4) Save plots to a custom folder

```bash
python main.py --input-mode json --input-file sample_portfolio.json --no-ai --output-dir ./test_output
```

---

## Generated Visualizations

The tool saves five PNG files:

- `asset_allocation.png`
- `runway_comparison.png`
- `risk_scores.png`
- `post_crash_value.png`
- `concentration_risk.png`

---

## Integration Details

### Task1 reuse (no edits)
- Imports Task1 `risk_metrics` functions in `risk_analysis.py`.
- Reuses deterministic metric and scenario logic.

### Task3-style advice (no edits)
- Uses Gemini call + structured JSON parsing pattern in `ai_advisor.py`.
- Expected response schema:

```json
{
   "summary": "...",
   "good_thing": "...",
   "improvement": "...",
   "verdict": "Aggressive | Balanced | Conservative"
}
```

---

## Dependencies

- Python 3.9+
- matplotlib
- pydantic
- rich
- google-generativeai
- python-dotenv

Install via:

```bash
pip install -r requirements.txt
```

---

## Current Status

- Implemented and runnable end-to-end.
- Verified CLI output and plot generation with sample portfolio.
- Verified custom output directory behavior.
- Verified `--no-ai` path for environments without API key.

---

## Constraints and Notes

- This task only changes files inside Task4.
- Task1 and Task3 source code remain untouched.
- Windows console compatibility is handled by ASCII-safe log symbols.
