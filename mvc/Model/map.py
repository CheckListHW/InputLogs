from typing import Union

import numpy as np
from scipy.interpolate import interp1d

from mvc.Model.log_curves import Log
from utils.file import dict_from_json, save_dict_as_json, FileEdit


class Map:
    __slots__ = 'columns', 'body_names', 'logs', 'visible_names', \
                'interval_data', 'max_x', 'max_y', 'max_z', 'path'

    def __init__(self, path: str = None):
        self.columns = {}
        self.interval_data = {}
        self.visible_names = self.body_names = []
        self.max_x, self.max_y, self.max_z = 0, 0, 0
        self.logs = {}  # {name: []} {str: [Log]}
        self.path = path
        if path:
            self.__load_map(path)

    def load_map(self, path: str):
        self.__init__(path)

    def get_logs(self, name: str) -> []:
        logs = self.logs.get(name)
        return [] if logs is None else logs

    def add_logs(self, name: str, log: Log):
        logs = self.logs.get(name)
        if logs is None:
            self.logs[name] = []
        remove_dot: () = lambda i: (i + '.')[:(i + '.').index('.')]
        name_len = len(list(filter(lambda i: remove_dot(i.name) == remove_dot(log.name), self.logs[name])))
        if name_len >= 1:
            log.name = remove_dot(log.name) + f'.{name_len}'
            log.main = False
        self.logs[name].append(log)

    def __load_map(self, path: str):
        self.interval_data = data = dict_from_json(path)
        for body_name in data:
            if body_name == 'logs':
                for name_body, logs in data['logs'].items():
                    self.logs[name_body] = []
                    for log in logs:
                        self.logs[name_body].append(Log())
                        self.logs[name_body][-1].load_from_dict(log)
            else:
                self.body_names.append(body_name)
                for x, y in [(x1, y1) for x1 in data[body_name] for y1 in data[body_name][x1]]:
                    self.max_x, self.max_y = max(self.max_x, int(x)), max(self.max_y, int(y))
                    for s_e in data[body_name][x][y]:
                        for z in range(s_e['s'], s_e['e'] + 1):
                            self.add_dot(x, y, int(z), body_name)
                            self.max_z = z if z > self.max_x else z

        self.visible_names = self.body_names.copy()

    def get_column(self, x: int, y: int) -> [(int, str)]:
        x, y = str(x), str(y)
        if not self.columns.get(x):
            self.columns[x] = {}
        if not self.columns[x].get(y):
            self.columns[x][y] = []
        return self.columns[x][y]

    def add_dot(self, x: int, y: int, z: int, name: str):
        self.get_column(x, y).append((z, name))

    def get_interval_column(self, x: Union[int, str], y: Union[int, str], body_name: str) -> [dict]:
        try:
            return self.interval_data[body_name][str(x)][str(y)]
        except KeyError or IndexError:
            return {}

    def save(self):
        self.interval_data['logs'] = {}
        for name, logs in self.logs.items():
            self.interval_data['logs'][name] = []
            for log in logs:
                self.interval_data['logs'][name].append(log.get_as_dict())
        return self.interval_data
