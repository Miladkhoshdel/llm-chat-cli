from math import isfinite

from decouple import config


def get_required_config(name, cast):
    raw_value = config(name, default=None)

    if raw_value is None or not str(raw_value).strip():
        raise ValueError(f"{name} is missing or empty in .env")

    try:
        value = config(name, cast=cast)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} has an invalid value: {error}") from error

    return value.strip() if isinstance(value, str) else value


def read_input(prompt):
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        return None


def read_number(prompt, number_type, minimum, maximum=None):
    while True:
        raw_value = read_input(prompt)

        if raw_value is None:
            return None

        try:
            value = number_type(raw_value)
        except ValueError:
            print("Please enter a valid number.")
            continue

        if not isfinite(value):
            print("Please enter a finite number.")
            continue

        if value < minimum or (maximum is not None and value > maximum):
            if maximum is None:
                print(f"Value must be at least {minimum}.")
            else:
                print(f"Value must be between {minimum} and {maximum}.")
            continue

        return value


__all__ = ["get_required_config", "read_input", "read_number"]
