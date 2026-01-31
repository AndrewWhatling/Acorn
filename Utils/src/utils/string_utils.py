import re


def to_camel_case(name: str) -> str:

    cleaned = re.sub(r'[^A-Za-z0-9]+', ' ', name)
    return ''.join(word.capitalize() for word in cleaned.split())