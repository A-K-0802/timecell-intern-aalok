import json
from typing import Any, Dict
from pathlib import Path


def load_from_json_file(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    return json.loads(p.read_text(encoding="utf-8-sig"))


def load_from_python_file(path: str) -> Dict[str, Any]:
    # Expect a file that defines a variable named `portfolio` as a dict
    import ast

    p = Path(path)
    source = p.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(p))
    for statement in module.body:
        if isinstance(statement, ast.Assign):
            for target in statement.targets:
                if isinstance(target, ast.Name) and target.id == "portfolio":
                    value = ast.literal_eval(statement.value)
                    if isinstance(value, dict):
                        return value
    raise ValueError("python input file must define a portfolio dictionary named 'portfolio'")


def load_portfolio(input_mode: str = "python", file: str | None = None) -> Dict[str, Any]:
    if input_mode == "python":
        path = file or "Task3/python_dict_input.py"
        return load_from_python_file(path)
    elif input_mode == "json":
        if not file:
            raise ValueError("--file is required for json input mode")
        return load_from_json_file(file)
    else:
        raise ValueError("unsupported input mode: %s" % input_mode)
