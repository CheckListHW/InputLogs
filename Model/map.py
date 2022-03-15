from typing import Optional, Union

from Model.log_curves import Log
from tools.file import dict_from_json, mass_from_xlsx, save_dict_as_json


class Map:
    __slots__ = 'columns', 'body_names', 'logs', 'visible_names', \
                'interval_data', 'max_x', 'max_y', 'max_z', 'path'

    def __init__(self, path: str = None):
        self.columns = {}
        self.interval_data = {}
        self.visible_names = self.body_names = []
        self.max_x = 0
        self.max_y = 0
        self.max_z = 0
        self.logs = {}  # {name: []} {str: [Log]}
        self.path = path
        if path:
            self.load_map(path)

    def load_map(self, path: str):
        self.logs = {}
        self.interval_data = data = dict_from_json(path)
        for body_name in data:
            if body_name == 'logs':
                for name_body, logs in data['logs'].items():
                    self.logs[name_body] = []
                    for log in logs:
                        self.logs[name_body].append(Log())
                        self.logs[name_body][-1].load_from_dict(log)
                continue
            self.body_names.append(body_name)
            self.logs[body_name] = []
            for x, y in [(x1, y1) for x1 in data[body_name] for y1 in data[body_name][x1]]:
                self.max_x = int(x) if self.max_x < int(x) else self.max_x
                self.max_y = int(y) if self.max_y < int(y) else self.max_y
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

    # def load_curves(self, path):
    #     logs = mass_from_xlsx(path)
    #     for k, v in logs.items():
    #         self.logs[k] = Log(name=k, )

    # def get_body_column(self, x: int, y: int, body_name: str):
    #     return [z for z, name in self.get_column(x, y) if name == body_name]

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


        save_dict_as_json(self.interval_data)
