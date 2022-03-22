import numpy as np
from scipy.interpolate import interp1d

from resourses.limits import MAX_TREND_RATIO
from utils.ceil import ceil
from utils.json_in_out import JsonInOut


class Log(JsonInOut):
    __slots__ = '_min', '_max', 'name', 'master_name', 'main', '_x', '_trend', 'f_trend', 'dispersion'

    def __init__(self, **kwargs):
        self._min = None
        self._max = None
        self.name = ''
        self.master_name = ''
        self.main = True
        self._trend: [(float, float)] = {0: 0, 1: 0}
        self._x = []
        self.dispersion = 0.85

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    @property
    def trend(self):
        f_trend = self.f_trend_init()
        trend = [(ceil(f_trend(i)), i) for i in np.arange(0, 1, 0.001)]
        return trend

    @property
    def trend_point(self) -> ([float], [float]):
        return [float(i) for i in self._trend.values()], [float(i) for i in self._trend.keys()]

    def f_trend_init(self):
        trend_data = [(float(x1), float(y1)) for y1, x1 in self._trend.items()]
        if len(trend_data) > 2:
            x, y = [y for _, y in trend_data], [x for x, _ in trend_data]
            return interp1d(x, y, kind='quadratic')
        else:
            return lambda i: 0

    def add_trend_point(self, point: (float, float)):
        x1, y1 = point
        y1 = 1 if y1 > 0.95 else 0 if y1 < 0.05 else y1
        self._trend[f'{y1}'] = x1

    def del_trend_point(self, point: (float, float)):
        if len(self._trend) < 3:
            return
        x, y = point

        keys = set(self._trend.keys()).symmetric_difference({'0', '1'})
        nearst = [(y1, abs(y - float(y1))) for y1 in keys]

        self._trend.pop(min(nearst, key=lambda i: i[1])[0])

    def get_text(self) -> str:
        return f'{self.name} (min = {self.min}, max = {self.max}, x = {True if self._x else False})'

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        self._min = value if value != self.max else self._max - 1
        self.__max_min_valid()

    def __max_min_valid(self):
        if self._max is not None and self._min is not None:
            self._max, self._min = max(self._max, self.min), min(self._max, self.min)

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value: float):
        self._max = value if value != self.min else self._min + 1
        self.__max_min_valid()

    @property
    def x(self):
        if self._x:
            return self._x

        a, b, tr, avg, des = self.min, self.max, [x for x, _ in self.trend], (self.max + self.min)/2, self.dispersion
        max_trend, min_trend = max(tr), min(tr)
        spacing = abs(max_trend) + abs(min_trend)
        center = 0 if spacing == 0 else (avg - avg / (spacing + 1))


        f_trend = self.f_trend_init()
        f_rand: () = lambda v: np.random.uniform(a + (v - a) * des, b - (b - v) * des)
        f_offset: () = lambda i, y1: y1 + avg * ceil(f_trend(i))

        y = [avg]
        print(y[-1], avg, f_trend(0))

        for _ in range(500):
            y.append(f_rand(y[-1]))

        y = [y1 / (1 + spacing) + center for y1 in y]

        len_y = len(y)
        y = [f_offset(i / len_y, y1) for i, y1 in zip(range(len_y), y)]
        print(max(y))
        return y# [i for i in y if a < i < b]

    @x.setter
    def x(self, value):
        self._x = value
