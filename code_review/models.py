from dataclasses import dataclass


@dataclass(frozen=True)
class Flake8Finding:
    path: str
    line: int
    column: int
    code: str
    message: str


@dataclass(frozen=True)
class BlackFinding:
    path: str
    line: int | None = None
    column: int | None = None
    code: str = "BLACK"
    message: str = "file would be reformatted"
