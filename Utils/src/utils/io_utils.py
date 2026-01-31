import json


def read_json(config: str):
    with open(config) as json_data:
        data = json.load(json_data)
        json_data.close()

    return data


def write_json(file, data):
    with open(file, "w") as json_file:
        json.dump(data, json_file, indent=4)
