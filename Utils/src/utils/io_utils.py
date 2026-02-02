import json
from typing import Any


def read_json(file: str) -> dict[str, Any]:
    """
    Reads given json file.

    Args:
        config (str): File to read.

    Returns:
        dict[str]: Json dictionary returned from file.
    """
    with open(file) as json_data:
        data = json.load(json_data)
        json_data.close()

    return data


def write_json(file: str, data: dict[str, Any]):
    """
    Writes data to json file.

    Args:
        file (str): File to write to.
        data (dict[str]): Dictionary to write.
    """
    with open(file, "w") as json_file:
        json.dump(data, json_file, indent=4)
