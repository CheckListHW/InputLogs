import json
import os
import random
from os import getcwd
from os.path import isfile
from typing import Final, Optional

import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QInputDialog


def dict_from_json(filename: str) -> dict:
    if isfile(filename):
        with open(filename) as f:
            return json.load(f)
    else:
        return {}


def mass_from_xlsx(path: str) -> dict:
    logs = {}
    xl = pd.ExcelFile(path)
    df = xl.parse(xl.sheet_names[0])
    for name in df.keys():
        logs[name] = list(df[name].values)
    return logs


def save_dict_as_json(data: dict, path: str = os.getcwd()+'/data/', filename: str = 'lay_name' + str(random.randint(1, 1000))):
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


class FileEdit:
    # Messages
    create_file_default: Final = 'Введите название файла:'
    create_file_error: Final = 'Не удалось создать файл,  \nфайл с таким именем уже существует'

    def __init__(self, parent: QMainWindow, file_used=''):
        self.parent = parent
        self.file_used = file_used

    def save_file(self, data: dict):
        if not self.file_used:
            self.create_file()
        save_dict_as_json(data=data, filename=self.file_used)

    def open_file(self, file_extension='json'):
        self.file_used, _ = QFileDialog.getOpenFileName(self.parent, '', getcwd(), f'Json Files (*.{file_extension})')
        return self.file_used



    def create_file(self, message=None) -> Optional[str]:
        if not message:
            message = self.create_file_default

        filename, ok = QInputDialog.getText(self.parent, 'Input Dialog', str(message))
        if ok and filename and filename != '':
            path = QFileDialog.getExistingDirectory(self.parent, getcwd())
            self.file_used = save_dict_as_json({}, path, filename)
            return self.file_used

        return None
