import random
from typing import Union, Optional

from mvc.Model.log_curves import Log
from utils.file import dict_from_json


def cut_along(name: str, symbol: str) -> str:
    name = name + symbol
    return name[:name.index(symbol)]


def sub_name_order_update(logs: [Log]):
    for sub_log, i in zip(logs[1:], range(1, len(logs))):
        sub_log.name = cut_along(sub_log.name, '.') + f'.{i}'
        sub_log.main = False


def last_char_is(name: str, sym: str) -> str:
    return name + ("" if name[-1] == sym else sym)


class Map:
    __slots__ = 'columns', 'body_names', 'logs', '_visible_names', \
                'interval_data', 'max_x', 'max_y', 'max_z', 'path', 'owc', 'all_logs'

    def __init__(self, path: str = None):
        self.columns, self.interval_data = {}, {}
        self._visible_names, self.body_names, self.all_logs = [], [], []
        self.max_x, self.max_y, self.max_z = 0, 0, 0
        self.logs = {}  # {name(str): [Log]}
        self.owc = {}  # {name(str): float}
        self.path = path
        if path:
            self.__load_map(path)

    @property
    def visible_names(self) -> [str]:
        return self._visible_names.copy() + self.visible_owc_names()

    @visible_names.setter
    def visible_names(self, value: [str]):
        self._visible_names = value

    def visible_owc_names(self):
        return [a for b in [[k + 'O|', k + 'W|'] for k in self.owc.keys() if k in self._visible_names] for a in b]

    def sub_logs(self, log_name: str) -> [Log]:
        return [log for log in self.all_logs if cut_along(log.name, '.') == log_name]

    def attach_log_to_layer(self, log_name: str, lay_name: str):
        o_or_w = 'O|' if lay_name.__contains__('|O') else 'W|' if lay_name.__contains__('|W') else ''

        for name in [i for i in self.body_names if cut_along(lay_name, '|') == cut_along(i, '|')]:
            validate_name = f'{name}{"" if name[-1] == "|" else "|"}{o_or_w}'
            self.logs[validate_name] = list(set(self.sub_logs(log_name) + self.get_logs(lay_name)))

    def attach_list(self):
        s = []
        for k, v in self.logs.items():
            for n in set(cut_along(n.name, '.') for n in v):
                s.append((k, n))
        return s

    def detach_log_to_layer(self, log_name: str, lay_name: str):
        self.logs[lay_name] = list(set(self.get_logs(lay_name)) - set(self.sub_logs(log_name)))

    def get_logs_by_name(self, name: str) -> Optional[Log]:
        logs = [l for l in self.all_logs if l.name == name]
        return None if len(logs) == 0 else logs[0]

    def logs_without_sub(self) -> [Log]:
        return [l for l in self.all_logs if not l.name.__contains__('.')]

    def main_logs_name(self) -> [str]:
        return list({cut_along(cut_along(l.name, '|'), '.') for l in self.all_logs})

    def main_names(self) -> [str]:
        m_names = set([l[:l.index('|') + 1] for l in self.body_names])
        for k in self.owc.keys():
            name = k[:k.index("|") + 1]
            m_names.discard(name)
            m_names.add(f'{name}O|')
            m_names.add(f'{name}W|')
        return sorted(list(m_names))

    def set_owc(self, name: str, value: int):
        if value in [0, '0', None]:
            return
        self.owc[name] = value

    def pop_owc(self, name: str):
        if self.owc.get(name):
            self.owc.pop(name)

    def change_log_select(self, main_name: str):
        print(main_name)
        cut_to_main: () = lambda name: cut_along(cut_along(name, '.'), '|')
        print([f'{log.name}: {log.main}' for log in self.all_logs])
        print([setattr(log, 'main', True) for log in self.all_logs if cut_to_main(log.name) == main_name])
        print([setattr(log, 'main', False) for log in self.all_logs if cut_to_main(log.name) != main_name])
        print([f'{log.name}: {log.main}' for log in self.all_logs])

    def pop_logs(self, log_name: str):
        indexes = [i for i in range(len(self.all_logs)) if self.all_logs[i].name == log_name]

        if indexes:
            self.all_logs.pop(indexes[0])
        sub_logs = list(filter(lambda i: i.name.__contains__(f'{log_name}.'), self.all_logs))

        if len(sub_logs) > 0:
            new_main_log = min(self.all_logs, key=lambda i: i.name)
            new_main_log.name = log_name

        self.logs = {k: [log for log in self.logs[k] if log in self.all_logs] for k, v in self.logs.items()}
        # for lay_name in list(self.logs.keys()):
        #     self.logs[lay_name] = [log for log in self.logs[lay_name] if log in self.all_logs]

    def load_map(self, path: str):
        self.__init__(path)

    def __load_map(self, path: str):
        self.interval_data = data = dict_from_json(path)
        if self.interval_data.get('logs'):
            self.all_logs = [Log(data_dict=log) for log in data['logs']]
        if self.interval_data.get('owc'):
            self.owc = data['owc']
        if self.interval_data.get('attach_logs'):
            self.logs = {k: [self.get_logs_by_name(log) for log in v if self.get_logs_by_name(log) is not None]
                         for k, v in data['attach_logs'].items()}

        self.body_names = []
        for b_name in [k for k in data.keys() if k not in ['logs', 'owc', 'attach_logs']]:
            body_name = last_char_is(b_name, '|')
            data[body_name] = data.pop(b_name)
            self.body_names.append(body_name)
            for x, y in [(x1, y1) for x1 in data[body_name] for y1 in data[body_name][x1]]:
                self.max_x, self.max_y = max(self.max_x, int(x)), max(self.max_y, int(y))
                self.max_z = max([s_e['e'] for s_e in data[body_name][x][y]] + [self.max_z])

        self._visible_names = self.body_names.copy()

    def get_logs(self, name: str) -> []:
        return [] if self.logs.get(name) is None else self.logs.get(name)

    def get_one_log(self, name: str) -> Optional[Log]:
        logs_name = self.get_logs(name)
        x = [l.name for l in logs_name if l.main]
        if x:
            s_logs = self.sub_logs(x[0])
            return s_logs[random.randint(0, len(s_logs) - 1)]
        else:
            return None

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

                for s_e, i in zip(interval_column, range(len(interval_column))):
                    if s_e['s'] <= self.owc[body_name] <= s_e['e']:
                        interval_column_o.append({'name': body_name_o, 's': s_e['s'], 'e': self.owc[body_name] - 1})
                        interval_column_w.append({'name': body_name_w, 's': self.owc[body_name], 'e': s_e['e']})
                    elif interval_column_w is []:
                        interval_column_o.append({'name': body_name_o, 's': s_e['s'], 'e': s_e['e']})
                    else:
                        interval_column_w.append({'name': body_name_w, 's': s_e['s'], 'e': s_e['e']})
                return interval_column_o + interval_column_w
            else:
                return [{'name': last_char_is(body_name, '|'), 's': col['s'], 'e': col['e']} for col in
                        self.interval_data[body_name][str(x)][str(y)]]

        except KeyError or IndexError:
            return []

    def save(self):
        self.interval_data['logs'] = [log.get_as_dict() for log in self.all_logs]
        self.interval_data['attach_logs'] = {k: [log.name for log in logs] for k, logs in self.logs.items()}
        self.interval_data['owc'] = self.owc
        return self.interval_data
