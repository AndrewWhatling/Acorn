import re


def to_camel_case(name: str) -> str:
    """
    Converts a string to camel case.

    Args:
        name (str): String to convert to camel case.

    Returns:
        str: String in camel case.
    """
    cleaned = re.sub(r'[^A-Za-z0-9]+', ' ', name)
    return ''.join(word.capitalize() for word in cleaned.split())