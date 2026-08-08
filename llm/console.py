def read_input(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        return None


def print_usage(usage):
    print("\n-----")
    print(f"Prompt tokens:     {usage.prompt_tokens}")
    print(f"Completion tokens: {usage.completion_tokens}")
    print(f"Reasoning tokens:  {usage.reasoning_tokens}")
    print(f"Total tokens:      {usage.total_tokens}")
    print(f"Cost:              {usage.cost}")
    print("-----\n")


__all__ = ["print_usage", "read_input"]
