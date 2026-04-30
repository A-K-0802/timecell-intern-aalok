# Task3 Test Fixtures

This folder contains reusable fixtures for exercising Task3 without calling Gemini for every check.

## Layout
- `inputs/`: portfolio payloads for the loader, validator, and prompt builder.
- `outputs/`: raw LLM response samples for parser and schema checks.
- `cases.json`: manifest describing the intent of each fixture.

## Coverage goals
- Normal portfolios with different risk profiles.
- Edge portfolios with unusual cash buffers, expense pressure, and large values.
- Bad input payloads that should fail loader or validation checks.
- Model outputs with valid JSON, markdown fences, extra prose, wrong verdicts, missing fields, and no JSON at all.

## Suggested use
- Feed `inputs/*.json` into the loader and prompt builder.
- Feed `outputs/*.txt` into `parse_structured_output`.
- Use `cases.json` as the source of truth for automation.

## Runner
Run the fixture runner from the `Task3` directory:

```bash
python .\TEST\runner.py
```

Useful flags:
- `--focus input`: run only the portfolio input cases.
- `--focus output`: run only the parser/output cases.
- `--manifest PATH`: point the runner at a different cases manifest.
- `--stop-on-fail`: stop at the first failing case.

How it works:
- Input cases are loaded through the same JSON loader used by Task3, then passed into `compute_risk_metrics()` and `build_prompt()` to catch invalid portfolio shapes, bad types, and prompt-building regressions.
- Output cases are read as raw model text, passed into `parse_structured_output()`, and then checked against the expected JSON fields and allowed verdict values.
- The runner prints a pass/fail line for each case and exits with a non-zero code if any case fails, so it can be used in a CI or local smoke-test workflow.
