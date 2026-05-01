# Portfolio Risk Analysis & AI Advisory System


## 📋 Project Overview

This project is a comprehensive portfolio analysis system that integrates financial risk metrics computation, visual analytics, and AI-powered investment advice. It processes investment portfolios and provides both quantitative risk analysis and LLM-generated recommendations.

**Key Features**:
- Deterministic crash-scenario risk calculation
- Multi-asset portfolio allocation analysis
- Five publication-quality visualizations
- Gemini AI-powered portfolio advice
- CLI-based dashboard with rich formatted output
- Windows/Linux compatible

---

## 🎯 Tasks Overview

### Task 1: Risk Metrics Analysis
**Folder**: `Task1/`

Computes portfolio crash risk metrics using deterministic scenarios:
- Calculates portfolio value after severe crashes (-100% multiplier) and moderate crashes (-50% multiplier)
- Computes runway (months of expenses covered) with 12-month survival threshold
- Identifies highest-risk assets and concentration warnings
- Supports multiple input formats (JSON, Python dict, CLI string)
- Includes CLI chart output for asset allocation

**Key Functions**:
- `compute_risk_metrics(portfolio)` - Core metric computation
- `compute_scenario_comparison(portfolio)` - Severe vs. moderate scenarios
- `compute_runway(value, expenses)` - Cash runway calculation

**Run**: `python main.py --input-file sample_portfolio.json`

---

### Task 2: Data Fetching & Formatting (WIP)
**Folder**: `Task2/`

Framework for fetching real-time market data and formatting portfolio data:
- Data loader utilities (`datafetch.py`)
- Formatting and normalization (`formatter.py`)
- Structured logging (`logger.py`)
- Test suite for early-stage validation

**Status**: Supports basic data fetching patterns and formatting.

---

### Task 3: AI-Powered Portfolio Explainer
**Folder**: `Task3/`

Uses Google Gemini API to generate structured portfolio advice:
- Builds rich prompts combining portfolio + precomputed metrics
- Calls Gemini with deterministic temperature (0.0) for consistency
- Parses structured JSON output with fallback extraction
- Supports three audience tones: beginner, experienced, expert
- Returns verdict (Aggressive/Balanced/Conservative) with reasoning

**Key Functions**:
- `build_prompt(portfolio, metrics, tone)` - Prompt engineering
- `call_gemini(prompt)` - LLM API interaction
- `parse_structured_output(text)` - JSON extraction from LLM response

**Run**: `python main.py --input-mode json --file sample_portfolio.json --tone beginner`

---

### Task 4: Portfolio Visualizer & AI Dashboard (CLI)
**Folder**: `Task4/`

Integration layer combining Task1 and Task3 with rich CLI output:
- Loads portfolios from JSON/Python files
- Computes all risk metrics using Task1 logic
- Generates 5 PNG visualizations saved to `outputs/` folder
- Optionally calls Gemini for AI advice
- Displays formatted tables in terminal with Rich library

**Generated Plots**:
1. Asset Allocation (pie chart)
2. Runway Comparison (current/moderate/severe scenarios)
3. Risk Scores (bubble chart)
4. Post-Crash Value (bar chart)
5. Concentration Risk (horizontal bar)

**Run**: `python main.py --input-file sample_portfolio.json --no-ai`

---

## 🚀 Quick Start

### 1. Clone & Navigate
```bash
cd d:\Personal_Projects\Timecell_internship
```

### 2. Install Dependencies (each task)

**Task1**:
```bash
cd Task1
pip install -q pydantic rich
python main.py --input-file sample_portfolio.json
```

**Task3** (requires Gemini API):
```bash
cd Task3
pip install -q python-dotenv pydantic rich google-generativeai
set GEMINI_API_KEY=your_api_key_here
python main.py --input-mode json --file sample_portfolio.json
```

**Task4** (integrated dashboard):
```bash
cd Task4
pip install -r requirements.txt
python main.py --input-mode json --input-file sample_portfolio.json --no-ai
```

### 3. View Results

**Task1**: Console output with metrics + optional ASCII chart

**Task3**: Raw LLM response + parsed JSON advice

**Task4**: 
- Terminal tables with portfolio summary and risk metrics
- PNG plots in `./outputs/` folder

---

## 🔧 Setup Instructions

### Prerequisites
- Python 3.9 or higher
- pip package manager
- (Optional) Google Gemini API key for AI features

### Environment Setup

**Windows PowerShell**:
```powershell
# Set API key for current session
set GEMINI_API_KEY=your_api_key_here

# Or set permanently
setx GEMINI_API_KEY your_api_key_here
```

**Linux/Mac**:
```bash
export GEMINI_API_KEY=your_api_key_here
```

### Install All Dependencies
```bash
# Task1
cd Task1 && pip install -q pydantic rich && cd ..

# Task2
cd Task2 && pip install -q && cd ..

# Task3
cd Task3 && pip install -q python-dotenv pydantic rich google-generativeai && cd ..

# Task4
cd Task4 && pip install -r requirements.txt && cd ..
```

---

## 💡 Usage Examples

### Task 1: Calculate Portfolio Risk
```bash
cd Task1
python main.py --input-file sample_portfolio.json --chart --compare-scenarios
```

### Task 3: Get AI Advice
```bash
cd Task3
python main.py --input-mode json --file sample_portfolio.json --tone experienced
```

### Task 4: Full Dashboard
```bash
cd Task4
# Metrics + plots only (no API needed)
python main.py --input-mode json --input-file sample_portfolio.json --no-ai

# With AI advisor
python main.py --input-mode python --tone beginner

# Custom output directory
python main.py --input-file portfolio.json --output-dir ./reports
```

---

## 📊 Sample Portfolio

All tasks use the same portfolio format:

```json
{
  "total_value_inr": 10000000,
  "monthly_expenses_inr": 80000,
  "assets": [
    {"name": "BTC", "allocation_pct": 30, "expected_crash_pct": -80},
    {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
    {"name": "GOLD", "allocation_pct": 20, "expected_crash_pct": -15},
    {"name": "CASH", "allocation_pct": 10, "expected_crash_pct": 0}
  ]
}
```

Expected outcomes:
- Severe crash post-value: ₹5.70Cr (57% retention)
- Runway: 71.25 months (PASS > 12 month threshold)
- Largest risk asset: BTC
- Concentration: NO warning

---


