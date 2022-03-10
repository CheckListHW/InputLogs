import json
from os.path import isfile


def dict_from_json(filename: str) -> dict:
    if isfile(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return {}