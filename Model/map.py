from typing import Optional, Union

from tools.dict_from_json import dict_from_json


class Map:
    __slots__ = 'columns', 'body_names', 'visible_names', 'interval_data', 'max_x', 'max_y'

    def __init__(self, path: str = None):
        self.columns = {}
        self.interval_data = {}
        self.visible_names = self.body_names = []
        self.max_x = 0
        self.max_y = 0
        if path:
            self.load_map(path)

    def load_map(self, path: str):
        self.interval_data = data = dict_from_json(path)
        for body_name in data:
            self.body_names.append(body_name)
            for x in data[body_name]:
                for y in data[body_name][x]:
                    for s_e in data[body_name][x][y]:
                        for z in range(s_e['s'], s_e['e'] + 1):
                            x1, y1 = int(x), int(y)
                            self.max_x = x1 if self.max_x < x1 else self.max_x
                            self.max_y = y1 if self.max_y < y1 else self.max_y
                            self.add_dot(x1, y1, int(z), body_name)

        self.visible_names = self.body_names.copy()

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
