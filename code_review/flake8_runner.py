import subprocess
import sys
from pathlib import Path

from .models import Flake8Finding


class Flake8ExecutionError(RuntimeError):
    """Raised when Flake8 cannot complete successfully."""


class Flake8Runner:
    OUTPUT_FORMAT = "%(path)s\t%(row)d\t%(col)d\t%(code)s\t%(text)s"

    def __init__(self, timeout=120):
        self.timeout = timeout

    def run(self, directory):
        root = Path(directory).expanduser().resolve()

        if not root.exists():
            raise ValueError(f"Directory does not exist: {root}")

        if not root.is_dir():
            raise ValueError(f"Path is not a directory: {root}")

        command = [
            sys.executable,
            "-m",
            "flake8",
            ".",
            f"--format={self.OUTPUT_FORMAT}",
            "--extend-exclude=.venv,venv",
        ]

        try:
            result = subprocess.run(
                command,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            raise Flake8ExecutionError(
                f"Flake8 timed out after {self.timeout} seconds"
            ) from error
        except OSError as error:
            raise Flake8ExecutionError(f"Could not start Flake8: {error}") from error

        if result.returncode not in {0, 1}:
            self._raise_execution_error(result)

        findings = self.parse_output(result.stdout)

        if result.returncode == 1 and not findings:
            self._raise_execution_error(result)

        return findings

    @staticmethod
    def parse_output(output):
        findings = []

        for output_line in output.splitlines():
            if not output_line.strip():
                continue

            parts = output_line.split("\t", 4)

            if len(parts) != 5:
                raise Flake8ExecutionError(
                    f"Could not parse Flake8 output: {output_line}"
                )

            path, line, column, code, message = parts

            try:
                line_number = int(line)
                column_number = int(column)
            except ValueError as error:
                raise Flake8ExecutionError(
                    f"Invalid Flake8 location: {output_line}"
                ) from error

            if path.startswith("./"):
                path = path[2:]

            findings.append(
                Flake8Finding(
                    path=path,
                    line=line_number,
                    column=column_number,
                    code=code,
                    message=message,
                )
            )

        return findings

    @staticmethod
    def _raise_execution_error(result):
        details = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Flake8 exited with status {result.returncode}"
        )

        raise Flake8ExecutionError(details)


__all__ = ["Flake8ExecutionError", "Flake8Runner"]

a = "asfkasghfjasfkhghfgxzxcvbnmpoasiuryfgjhbsakfkjmaskjkhvdwgefc fewcvgbhnjilxwmo;KCSIKBHUVAFUHJS.ZHFN,KSAGSKF"
