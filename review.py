import argparse

from openai import OpenAIError

from code_review import BlackExecutionError, CodeReviewer, Flake8ExecutionError
from llm import LLM, load_settings


def build_parser():
    parser = argparse.ArgumentParser(
        description="Run Flake8 and Black, then explain findings with an LLM."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Python project directory to review (default: current directory)",
    )
    return parser


def print_usage(usage):
    print("\n-----")
    print(f"Prompt tokens:     {usage.prompt_tokens}")
    print(f"Completion tokens: {usage.completion_tokens}")
    print(f"Reasoning tokens:  {usage.reasoning_tokens}")
    print(f"Total tokens:      {usage.total_tokens}")
    print(f"Cost:              {usage.cost}")
    print("-----")


def print_findings_count(findings):
    if findings:
        print(f"Static checks found {len(findings)} issue(s).\n")


def print_stream_text(text):
    print(text, end="", flush=True)


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        settings = load_settings()
    except ValueError as error:
        print(f"Configuration error: {error}")
        return 1

    reviewer = CodeReviewer(LLM(settings))

    try:
        findings, response = reviewer.review(
            args.directory,
            on_text=print_stream_text,
            on_findings=print_findings_count,
        )
    except ValueError as error:
        print(f"Invalid review target: {error}")
        return 1
    except Flake8ExecutionError as error:
        print(f"Flake8 failed: {error}")
        return 1
    except BlackExecutionError as error:
        print(f"Black failed: {error}")
        return 1
    except OpenAIError as error:
        print(f"LLM request failed: {error}")
        return 1

    if not findings:
        print("No Flake8 or Black findings.")
        return 0

    if response.content and not response.content.endswith("\n"):
        print()

    if response.finish_reason == "length":
        print("\nWarning: the LLM explanation may be incomplete.")

    if settings.show_usage and response.usage:
        print_usage(response.usage)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
