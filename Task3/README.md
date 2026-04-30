# Task 3 — AI-Powered Portfolio Explainer

Mini AI pipeline that:

- loads a portfolio from a Python file or JSON,
- computes precomputed risk metrics,
- sends a structured prompt to Google Gemini,
- prints the raw LLM response and a parsed, deterministic JSON explanation.

See the main entrypoint at [Task3/main.py](Task3/main.py).

**Requirements**
- Python 3.9+
- Install dependencies:

```bash
pip install python-dotenv pydantic rich google-generativeai
```

**Configuration**
- Provide your Gemini API key via an environment variable `GEMINI_API_KEY` (preferred) or a workspace-level dotenv file.

**How to run**
- Run with Python from the `Task3` directory:

```bash
python main.py --input-mode python
python main.py --input-mode json --file sample_portfolio.json
```

**Files of interest**
- `main.py`: CLI orchestration and pipeline flow ([Task3/main.py](Task3/main.py)).
- `input_loader.py`: loads Python or JSON portfolios ([Task3/input_loader.py](Task3/input_loader.py)).
- `risk_metrics.py`: precomputed metrics reused from Task1 ([Task3/risk_metrics.py](Task3/risk_metrics.py)).
- `prompt_builder.py`: builds the LLM prompt ([Task3/prompt_builder.py](Task3/prompt_builder.py)).
- `llm_client.py`: Gemini client wrapper ([Task3/llm_client.py](Task3/llm_client.py)).
- `parser.py`: extracts and validates JSON from LLM output ([Task3/parser.py](Task3/parser.py)).

**Prompt style & rules**
- The system uses a strict, JSON-only prompt style: the prompt defines a role, audience (tone), the
	portfolio data and precomputed `metrics`, and explicit instructions to return only valid JSON.
- The expected JSON schema is:

```json
{
	"summary": "...",
	"good_thing": "...",
	"improvement": "...",
	"verdict": "Aggressive | Balanced | Conservative"
}
```
- Key prompt-engineering guidelines applied in `prompt_builder.py`:
	- Use precomputed numeric signals (don't ask the LLM to compute math).
	- Force deterministic output by setting `temperature=0` and instructing JSON-only output.
	- Provide an optional `tone` (audience) so language can be beginner/experienced/expert.

**CLI flags**
- `--input-mode`: `python` (default) or `json`. Selects loader.
- `--file`: Path to the input file. For `python` mode defaults to `python_dict_input.py` if omitted.
- `--tone`: `beginner` | `experienced` | `expert` (controls wording in prompt).
- `--raw-only`: print only the raw LLM response and exit.

Example:

```bash
python main.py --input-mode json --file sample_portfolio.json --tone beginner
```

**Output**
- The CLI prints two sections:
	- `=== RAW LLM RESPONSE ===`: the verbatim text returned by Gemini.
	- `=== PARSED OUTPUT ===`: the extracted JSON fields (`summary`, `good_thing`, `improvement`, `verdict`).

**Error handling & retries**
- If parsing fails, the CLI will re-request strict JSON from the LLM once and attempt parsing again.
- If `GEMINI_API_KEY` is missing or the `google-generativeai` client isn't installed, `llm_client.py` raises
	a clear error explaining the problem.

**Design notes**
- Metrics are computed locally (`risk_metrics.py`) and injected into prompts — this keeps outputs
	consistent and prevents the model from doing numeric calculations.
- The parser first attempts `json.loads()` then extracts a JSON blob when the LLM emits extra text.

If you want, I can add a small smoke-test script that runs the loader and metric functions without calling Gemini.
