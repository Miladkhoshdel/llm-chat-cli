import subprocess
import sys
from pathlib import Path

from .models import BlackFinding


class BlackExecutionError(RuntimeError):
    """Raised when Black cannot complete successfully."""


class BlackRunner:
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
            "black",
            "--check",
            "--diff",
            "--no-color",
            ".",
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
            raise BlackExecutionError(
                f"Black timed out after {self.timeout} seconds"
            ) from error
        except OSError as error:
            message = f"Could not start Black: {error}"
            raise BlackExecutionError(message) from error

        if result.returncode == 0:
            return []

        if result.returncode != 1:
            self._raise_execution_error(result)

        findings = self.parse_output(result.stdout, root)

        if not findings:
            self._raise_execution_error(result)

        return findings

    @staticmethod
    def parse_output(output, root=None):
        root = Path(root).resolve() if root is not None else None
        findings = []
        seen_paths = set()

        for line in output.splitlines():
            if not line.startswith("+++ "):
                continue

            path_text = line[4:].split("\t", 1)[0]
            path = Path(path_text)

            if root is not None and path.is_absolute():
                try:
                    path = path.relative_to(root)
                except ValueError:
                    pass

            normalized_path = path.as_posix()

            if normalized_path in seen_paths:
                continue

            seen_paths.add(normalized_path)
            findings.append(BlackFinding(path=normalized_path))

        return findings

    @staticmethod
    def _raise_execution_error(result):
        details = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"Black exited with status {result.returncode}"
        )

        raise BlackExecutionError(details)


__all__ = ["BlackExecutionError", "BlackRunner"]
