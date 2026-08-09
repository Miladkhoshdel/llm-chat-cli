from dataclasses import dataclass


@dataclass(frozen=True)
class Flake8Finding:
    path: str
    line: int
    column: int
    code: str
    message: str
