import json
import random

import os
from os.path import isfile


def save_dict_as_json(data: dict, path: str = os.getcwd(), filename: str = 'lay_name' + str(random.randint(1, 1000))):
    if path.__contains__('.json'):
        path_save = path
    elif filename.__contains__('.json'):
        path_save = filename
    else:
        path_save = path + '/lay_name.json'.replace('lay_name', filename)
    path_save.replace('//', '/')

    try:
        json_file = open(path_save, mode='x')
    except FileExistsError:
        json_file = open(path_save, mode='w')
    json.dump(data, json_file)
    json_file.close()
    return path_save


def dict_from_json(filename: str) -> dict:
    if isfile(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return {}




