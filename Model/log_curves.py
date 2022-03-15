import numpy as np

from tools.json_in_out import JsonInOut


class Log(JsonInOut):
    __slots__ = 'min', 'max', 'name', 'master_name', 'main', '_x'

    def __init__(self, **kwargs):
        self.min = 0
        self.max = 0
        self.name = ''
        self.master_name = ''
        self.main = True
        self._x = []

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def get_text(self) -> str:
        return f'{self.name} (min = {self.min}, max = {self.max}, x = {True if self._x else False})'

    @property
    def x(self):
        if self._x:
            return self._x
        a, b = self.min, self.max
        x = np.random.normal(0, 0.5, size=500)
        max_x, min_x = max(x), min(x)
        y = (x * (abs(a - b) * 2 / abs(min_x - max_x))) + abs(a - b) / 2
        return [i for i in y if a < i < b]

    @x.setter
    def x(self, value):
        self._x = value
