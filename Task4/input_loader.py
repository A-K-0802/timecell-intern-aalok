"""Portfolio input loader for Task4."""

import json
import ast
from typing import Any, Dict
from pathlib import Path


def load_from_json_file(path: str) -> Dict[str, Any]:
    """Load portfolio from JSON file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e


def load_from_python_file(path: str) -> Dict[str, Any]:
    """Load portfolio from Python file (expects a 'portfolio' variable)."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Python file not found: {path}")
    
    try:
        source = p.read_text(encoding="utf-8")
        module = ast.parse(source, filename=str(p))
        
        for statement in module.body:
            if isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name) and target.id == "portfolio":
                        value = ast.literal_eval(statement.value)
                        if isinstance(value, dict):
                            return value
        
        raise ValueError("Python file must define a 'portfolio' dictionary variable")
    except SyntaxError as e:
        raise ValueError(f"Syntax error in {path}: {e}") from e


def load_from_json_string(json_str: str) -> Dict[str, Any]:
    """Load portfolio from JSON string."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON string: {e}") from e


def load_portfolio(
    input_mode: str = "python",
    file_path: str | None = None,
    json_string: str | None = None,
) -> Dict[str, Any]:
    """
    Load portfolio from various sources.
    
    Args:
        input_mode: 'python', 'json', or 'string'
        file_path: Path to input file (for 'python' or 'json' modes)
        json_string: JSON string (for 'string' mode)
    
    Returns:
        Portfolio dictionary
    """
    if input_mode == "python":
        if file_path:
            path = file_path
        else:
            # Try Task1/python_dict_input.py first, then Task4/python_dict_input.py
            task1_path = Path(__file__).parent.parent / "Task1" / "python_dict_input.py"
            task4_path = Path(__file__).parent / "python_dict_input.py"
            
            if task1_path.exists():
                path = str(task1_path)
            elif task4_path.exists():
                path = str(task4_path)
            else:
                path = "python_dict_input.py"
        
        return load_from_python_file(path)
    
    elif input_mode == "json":
        if not file_path:
            raise ValueError("--input-file is required for json input mode")
        return load_from_json_file(file_path)
    
    elif input_mode == "string":
        if not json_string:
            raise ValueError("JSON string is required for string input mode")
        return load_from_json_string(json_string)
    
    else:
        raise ValueError(f"Unsupported input mode: {input_mode}")
