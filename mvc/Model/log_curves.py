import re
from typing import Optional, Callable

import numpy as np
from scipy.interpolate import interp1d

from utils.ceil import ceil
from utils.json_in_out import JsonInOut


class Log(JsonInOut):
    __slots__ = '_min', '_max', 'name', 'main', '_x', '_trend', 'f_trend', 'dispersion', 'text_expression'

    def __init__(self, data_dict: dict = None, **kwargs):
        self._min = None
        self._max = None
        self.name = ''
        self.main = True
        self._trend: {str: float} = {'0': 0, '1': 0}
        self._x = []
        self.text_expression: str = ''
        self.dispersion = 0.85

        if data_dict:
            self.load_from_dict(data_dict)

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

        keys = set(self._trend.keys()) - {'0', '1'}
        nearst = [(y1, abs(y - float(y1))) for y1 in keys]

        self._trend.pop(min(nearst, key=lambda i: i[1])[0])

    def get_text(self) -> str:
        min_max = {f"(min = {self.min}, max = {self.max})" if self.max or self.min else self.text_expression}
        return f'{self.name} {min_max} {".xlsx" if self._x else ""} {"⚡" if len(self._trend) > 2 else ""}'

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
    def x(self) -> [float]:
        if self._x:
            return self._x
        if self.max is not None and self.min is not None:
            return self.trend_x()
        else:
            return [0 for _ in range(500)]

    @x.setter
    def x(self, value: [float]):
        self._x = value

    def trend_x(self):
        a, b, avg, des = self.min, self.max, (self.max + self.min) / 2, self.dispersion

        f_trend = self.f_trend_init()
        f_rand: () = lambda v: np.random.uniform(a + (v - a) * des, b - (b - v) * des)
        f_offset: () = lambda i, y1: y1 + avg * ceil(f_trend(i))
        f_y_limit: () = lambda y: y if a <= y <= b else f_y_limit(a + a - y) if a > y else f_y_limit(b - (y - b))

        y, len_y = [avg], 500
        for _ in range(len_y - 1):
            y.append(f_rand(y[-1]))

        return [f_y_limit(f_offset(i / len_y, y1)) for i, y1 in zip(range(len_y), y)]

    @x.setter
    def x(self, value):
        self._x = value


def expression_array_parser(expression: str, logs_name: [str]) -> Optional[Callable]:
    for l_n in logs_name:
        replacement_var = f"c['{l_n}'][int(len(c['{l_n}'])*i/len_x)]"
        expression = expression.replace('{' + l_n + '}', replacement_var)
    try:
        return eval(f'lambda c, i, len_x: {expression}')
    except SyntaxError:
        return lambda i: None


def expression_parser(expression: str) -> Optional[Callable]:
    for l_n in re.findall(r'[{].*?[}]', expression):
        expression = expression.replace(l_n, f"c['{l_n[1:l_n.index('|')]}']")
    try:
        return eval(f'lambda c: {expression}')
    except SyntaxError:
        return None


class ExpressionLog:
    __slots__ = 'x'

    def __init__(self, logs: {str: [float]}, text_expression: str):
        self.x = [None for _ in range(500)]
        expression = expression_array_parser(text_expression, [str(k) for k in logs])
        len_x = len(self.x)
        try:
            self.x = [expression(logs, i, len_x) for i in range(len(self.x))]
        except:
            pass

    def __call__(self, *args, **kwargs) -> bool:
        return self.valid_expression()

    def valid_expression(self) -> bool:
        return bool(not self.x.__contains__(None))


def sort_expression_logs(logs: [Log]) -> [(str, str)]:
    expressions = [(log.name, log.text_expression, log) for log in logs]

    cut_excess: () = lambda i: i[:i.index('|')].replace(' ', '').replace('{', '').replace('}', '')
    extract_vars: () = lambda i: re.findall(r'[{].*?[}]', i)

    unsorted_expressions = [(cut_excess(exp[0]), [cut_excess(i) for i in extract_vars(exp[1])], exp[2]) for exp in expressions]
    old, sorted_expressions = [], []

    while unsorted_expressions:
        old = sorted_expressions.copy()
        for i in unsorted_expressions:
            if not [uns_exp for uns_exp in i[1] if uns_exp in [uns_exp[0] for uns_exp in unsorted_expressions]]:
                sorted_expressions.append(i)
        unsorted_expressions = [i for i in unsorted_expressions if i not in sorted_expressions]
        if old == sorted_expressions:
            return expressions
    return [log for _, _, log in sorted_expressions]