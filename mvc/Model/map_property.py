import random
from typing import Union, Optional

import numpy as np

from mvc.Model.log_curves import Log
from utils.file import dict_from_json
from utils.gisaug.augmentations import DropRandomPoints, Stretch
from utils.realistic_transition import realistic_transition

interval = [[float], str, [float]]
# [('core_sample_name', 'lithology_name', 'log_name', 'percent_safety(in 0...1)'  , 'null_val')]
CoreSample = (str, str, str, str)


def cut_along(name: str, symbol: str) -> str:
    name = name + symbol
    return name[:name.index(symbol)]


def sub_name_order_update(logs: [Log]):
    for sub_log, i in zip(logs[1:], range(1, len(logs))):
        sub_log.name = cut_along(sub_log.name, '.') + f'.{i}'
        sub_log.main = False


def last_char_is(name: str, sym: str) -> str:
    return name + ("" if name[-1] == sym else sym)


class ColumnIntervals:
    def __init__(self):
        self.intervals: [interval] = []
        self.__min: Optional[float] = None
        self.__max: Optional[float] = None

    def __getitem__(self, item: int):
        return self.intervals[item]

    def __setitem__(self, key: int, value: interval):
        self.intervals[key] = value

    @property
    def min(self):
        if self.__min is not None:
            return self.__min
        x = [a for b in [x1 for x1, _, _ in self.intervals] for a in b]
        return min(x) if x else 0

    @property
    def max(self):
        if self.__max is not None:
            return self.__max
        x = [a for b in [x1 for x1, _, _ in self.intervals] for a in b]
        return max(x) if x else 1

    @property
    def count(self) -> int:
        return len(self.intervals)

    def set_max(self, value: Optional[float]):
        if self.__max is None:
            self.__max = value
        elif value is not None:
            self.__max = max([value, self.__max])

    def set_min(self, value: Optional[float]):
        if self.__min is None:
            self.__min = value
        elif value is not None:
            self.__min = min([value, self.__min])

    def append(self, value: interval):
        self.intervals.append(value)


class MapProperty:
    __slots__ = 'columns', 'body_names', 'attach_logs', '_visible_names', 'core_samples', 'settings', \
                'interval_data', 'max_x', 'max_y', 'max_z', 'path', 'owc', \
                'all_logs', 'export', 'percent_safe_core', 'initial_depth', 'step_depth'

    def __init__(self, path: str = None, data: dict = None):
        self.columns, self.interval_data = {}, {}
        self._visible_names, self.body_names, self.all_logs = [], [], []
        self.max_x, self.max_y, self.max_z = 0, 0, 0
        self.attach_logs, self.owc = {}, {}  # {name(str): [Log]}, {name(str): float}
        self.core_samples: [CoreSample] = []
        self.percent_safe_core = 0.3
        self.step_depth = 0.4
        self.initial_depth = 2000

        self.path = path

        if path:
            data = dict_from_json(path)
        if data:
            self.__load_map(data)

    @property
    def visible_names(self) -> [str]:
        return self._visible_names.copy() + self.visible_owc_names()

    @visible_names.setter
    def visible_names(self, value: [str]):
        self._visible_names = value

    def load_map(self, path: str):
        self.__init__(path)

    def __load_map(self, data: dict):
        self.interval_data = data
        if data.get('settings'):
            self.percent_safe_core = data['settings']['percent_safe_core']
            if data['settings'].get('initial_depth'):
                self.initial_depth = data['settings']['initial_depth']
            if data['settings'].get('step_depth'):
                self.step_depth = data['settings']['step_depth']
        if data.get('all_logs'):
            self.all_logs = [Log(data_dict=log) for log in data['all_logs']]
        if data.get('owc'):
            self.owc = data['owc']
        if data.get('core_samples'):
            self.core_samples = [tuple(i) for i in data['core_samples']]

        if self.interval_data.get('attach_logs'):
            self.attach_logs = {
                k: [self.get_logs_by_name(log) for log in v if self.get_logs_by_name(log) is not None]
                for k, v in data['attach_logs'].items()}

        self.body_names = []
        for b_name in [k for k in data.keys() if k not in self.__slots__]:
            body_name = last_char_is(b_name, '|')
            data[body_name] = data.pop(b_name)
            self.body_names.append(body_name)
            for x, y in [(x1, y1) for x1 in data[body_name] for y1 in data[body_name][x1]]:
                self.max_x, self.max_y = max(self.max_x, int(x)), max(self.max_y, int(y))
                self.max_z = max([s_e['e'] for s_e in data[body_name][x][y]] + [self.max_z])

        self._visible_names = self.body_names.copy()

    def save(self):
        self.interval_data['all_logs'] = [log.get_as_dict() for log in self.all_logs]
        self.interval_data['attach_logs'] = {k: [log.name for log in logs] for k, logs in self.attach_logs.items()}
        self.interval_data['owc'] = self.owc
        self.interval_data['core_samples'] = self.core_samples
        self.interval_data['settings'] = {'percent_safe_core': self.percent_safe_core,
                                          'step_depth': self.step_depth,
                                          'initial_depth': self.initial_depth,
                                          }
        return self.interval_data

    def visible_owc_names(self):
        return [a for b in [[k + 'O|', k + 'W|'] for k in self.owc.keys() if k in self._visible_names] for a in b]

    def get_logs_by_name(self, name: str) -> Optional[Log]:
        logs = [l for l in self.all_logs if l.name == name]
        return None if len(logs) == 0 else logs[0]

    def add_core_sample(self, core_sample: CoreSample):
        name, log_name, lithology_name, null_value = core_sample
        self.core_samples.append((name, log_name, lithology_name, null_value))
        self.core_samples = list(set(self.core_samples))

    def pop_core_sample(self, core_sample: CoreSample):
        self.core_samples = [c_s for c_s in self.core_samples if c_s != core_sample]

    def sub_logs(self, log_name: str) -> [Log]:
        return [log for log in self.all_logs if cut_along(log.name, '.') == cut_along(log_name, '.')]

    def attach_log_to_layer(self, log_name: str, lay_name: str):
        o_or_w = 'O|' if lay_name.__contains__('|O') else 'W|' if lay_name.__contains__('|W') else ''

        for name in [i for i in self.body_names if cut_along(lay_name, '|') == cut_along(i, '|')]:
            validate_name = f'{name}{"" if name[-1] == "|" else "|"}{o_or_w}'
            self.attach_logs[validate_name] = list(set(self.sub_logs(log_name) + self.get_logs(validate_name)))

    def attach_list(self):
        s = []
        for k, v in self.attach_logs.items():
            for n in set(cut_along(n.name, '.') for n in v):
                s.append((k, n))
        return s

    def detach_log_to_layer(self, log_name: str, lay_name: str):
        self.attach_logs[lay_name] = list(set(self.get_logs(lay_name)) - set(self.sub_logs(log_name)))

    def logs_without_sub(self) -> [Log]:
        return [l for l in self.all_logs if not l.name.__contains__('.')]

    def main_logs_name(self) -> [str]:
        return list({cut_along(l, '|') for l in self.main_logs_name_owc()})

    def main_logs_name_non_expression(self) -> [str]:
        names = [l.name for l in [i for i in self.all_logs if i.text_expression == ''] if not l.name.__contains__('.')]
        return list({cut_along(l, '|') for l in names})

    def main_logs_name_owc(self) -> [str]:
        return list({cut_along(l.name, '.') for l in self.all_logs})

    def main_body_names_owc(self) -> [str]:
        m_names = set(self.main_body_names())
        for k in self.owc.keys():
            name = k[:k.index("|") + 1]
            # m_names.discard(name)
            m_names.add(f'{name}O|')
            m_names.add(f'{name}W|')
        return sorted(list(m_names))

    def main_body_names(self):
        return list(set([cut_along(l, '|') + '|' for l in self.body_names]))

    def set_owc(self, name: str, value: int):
        if value in [0, '0', None]:
            return
        self.owc[name] = value

    def pop_owc(self, name: str):
        if self.owc.get(name):
            self.owc.pop(name)

    def change_log_select(self, main_name: str):
        cut_to_main: () = lambda name: cut_along(cut_along(name, '.'), '|')
        [setattr(log, 'main', cut_to_main(log.name) == main_name) for log in self.all_logs]

    def pop_logs(self, log_name: str):
        indexes = [i for i in range(len(self.all_logs)) if self.all_logs[i].name == log_name]

        if indexes:
            self.all_logs.pop(indexes[0])
        sub_logs = list(filter(lambda i: i.name.__contains__(f'{log_name}.'), self.all_logs))

        if len(sub_logs) > 0:
            new_main_log = min(self.all_logs, key=lambda i: i.name)
            new_main_log.name = log_name

        self.attach_logs = {k: [log for log in self.attach_logs[k] if log in self.all_logs] for k, v in
                            self.attach_logs.items()}
        # for lay_name in list(self.logs.keys()):
        #     self.logs[lay_name] = [log for log in self.logs[lay_name] if log in self.all_logs]

    def get_logs(self, name: str) -> []:
        return [] if self.attach_logs.get(name) is None else self.attach_logs.get(name)

    def get_one_log(self, name: str) -> Optional[Log]:
        x = [l.name for l in self.get_logs(name) if l.main]
        if x:
            if self.sub_logs(x[0]):
                return random.choice(self.sub_logs(x[0])) if x else None

    def add_logs(self, log: Log):
        self.all_logs.append(log)
        logs = list(filter(lambda i: cut_along(i.name, '.') == cut_along(log.name, '.'), self.all_logs))
        sub_name_order_update(logs)

    def get_column(self, x: Union[int, str], y: Union[int, str]) -> [{str: [dict]}]:
        return [a for b in [self.get_colum_body(x, y, name) for name in self.body_names] for a in b]

    def get_colum_body(self, x: Union[int, str], y: Union[int, str], body_name: str) -> {str: [dict]}:
        try:
            if self.owc.get(body_name) is not None:
                interval_column = self.interval_data[body_name][str(x)][str(y)]
                interval_column_w, interval_column_o = [], []
                body_name_o = last_char_is(body_name, '|') + 'O|'
                body_name_w = last_char_is(body_name, '|') + 'W|'

                if self.get_one_log(body_name_o) and self.get_one_log(body_name_w):
                    for s_e, i in zip(interval_column, range(len(interval_column))):
                        if s_e['s'] <= self.owc[body_name] <= s_e['e']:
                            interval_column_o.append({'name': body_name_o, 's': s_e['s'], 'e': self.owc[body_name] - 1})
                            interval_column_w.append({'name': body_name_w, 's': self.owc[body_name], 'e': s_e['e']})
                        elif interval_column_w is []:
                            interval_column_o.append({'name': body_name_o, 's': s_e['s'], 'e': s_e['e']})
                        else:
                            interval_column_w.append({'name': body_name_w, 's': s_e['s'], 'e': s_e['e']})
                    return interval_column_o + interval_column_w
            return [{'name': last_char_is(body_name, '|'), 's': col['s'], 'e': col['e']} for col in
                    self.interval_data[body_name][str(x)][str(y)]]

        except KeyError or IndexError:
            return []

    def get_column_curve(self, x: int, y: int) -> Optional[ColumnIntervals]:
        if not len(self.attach_logs.keys()):
            return None

        col_intervals = ColumnIntervals()
        sort_column = sorted(self.get_column(x, y), key=lambda i: i['s'])

        for name, s, e in [i.values() for i in sort_column]:
            log = self.get_one_log(name)
            if not log:
                continue
            interval = range(int(s), int(e) + 1)
            if len(interval) >= 1:
                curve = DropRandomPoints(0.95)(np.array(log.x))
                curve = Stretch.stretch_curve_by_count(curve, len(interval))

                col_intervals.append((curve, name, interval))
                col_intervals.set_min(log.min)
                col_intervals.set_max(log.max)

        if not col_intervals.count:
            return None

        col_pre, curve_use_per = col_intervals[0], 0.1 + random.random() * 0.05

        for i in range(1, col_intervals.count):
            curve_p, name_p, interval_p = col_pre
            curve_n, name_n, interval_n = col_intervals[i]
            min_len = min(len(interval_p), len(interval_n))
            start, end = len(interval_p) - int(min_len * curve_use_per), int(min_len * curve_use_per)
            y_a, y_b = realistic_transition(curve_p[start:], curve_n[:end])
            col_intervals[i - 1] = (list(curve_p[:start]) + y_a, name_p, interval_p)
            col_pre = col_intervals[i] = (y_b + list(curve_n[end:]), name_n, interval_n)

        return col_intervals

