from typing import Optional, Union

from tools.dict_from_json import dict_from_json


class Map:
    __slots__ = 'columns', 'body_names', 'interval_data'

    def __init__(self):
        self.columns = {}
        self.interval_data = {}
        self.body_names = []

    def load_map(self, path: str):
        self.interval_data = data = dict_from_json(path)
        for body_name in data:
            self.body_names.append(body_name)
            for x in data[body_name]:
                for y in data[body_name][x]:
                    for s_e in data[body_name][x][y]:
                        for z in range(s_e['s'], s_e['e'] + 1):
                            self.add_dot(int(x), int(y), int(z), body_name)

    def get_column(self, x: int, y: int) -> [(int, str)]:
        if not self.columns.get(x):
            self.columns[x] = {}
        if not self.columns[x].get(y):
            self.columns[x][y] = []
        return self.columns[x][y]

    def add_dot(self, x: int, y: int, z: int, name: str):
        self.get_column(x, y).append((z, name))

    # def get_body_column(self, x: int, y: int, body_name: str):
    #     return [z for z, name in self.get_column(x, y) if name == body_name]

    # def get_interval_column(self, x: Union[int, str], y: Union[int, str], body_name: str) -> [dict]:
    #     try:
    #         return self.interval_data[body_name][str(x)][str(y)]
    #     except KeyError or IndexError:
    #         return {}
