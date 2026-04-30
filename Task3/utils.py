from rich.console import Console
from rich.markdown import Markdown
from typing import Any

console = Console()


def log_info(msg: str) -> None:
    console.print(msg)


def log_json(obj: Any) -> None:
    import json

    console.print_json(data=json.loads(json.dumps(obj, default=str)))
