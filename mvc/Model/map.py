from typing import Union

from mvc.Model.log_curves import Log
from utils.file import dict_from_json


def remove_dot(name: str) -> str:
    return (name + '.')[:(name + '.').index('.')]


def sub_name_order_update(logs: [Log]):
    for sub_log, i in zip(logs[1:], range(1, len(logs))):
        sub_log.name = remove_dot(sub_log.name) + f'.{i}'
        sub_log.main = False


class Map:
    __slots__ = 'columns', 'body_names', '_logs', 'visible_names', \
                'interval_data', 'max_x', 'max_y', 'max_z', 'path', 'owc'

    def __init__(self, path: str = None):
        self.columns = {}
        self.interval_data = {}
        self.visible_names = self.body_names = []
        self.max_x, self.max_y, self.max_z = 0, 0, 0
        self._logs = {}  # {name(str): [Log]}
        self.owc = {}   # {name(str): float}
        self.path = path
        if path:
            self.__load_map(path)

    def add_owc(self):
        pass

    def pop_owc(self):
        pass



    def pop_logs(self, name: str, index: int):
        log_name = self._logs[name][index].name
        self._logs[name].pop(index)
        sub_logs = list(filter(lambda i: i.name.__contains__(f'{log_name}.'), self._logs[name]))
        if len(sub_logs) > 0:
            new_main_log = min(self._logs[name], key=lambda i: i.name)
            new_main_log.name = log_name

    @property
    def logs(self):
        return self._logs.copy()

    def load_map(self, path: str):
        self.__init__(path)

    def get_logs(self, name: str) -> []:
        logs = self._logs.get(name)
        return [] if logs is None else logs

    def add_logs(self, name: str, log: Log):
        logs = self._logs.get(name)
        if logs is None:
            self._logs[name] = []

        self._logs[name].append(log)
        logs = list(filter(lambda i: remove_dot(i.name) == remove_dot(log.name), self._logs[name]))
        sub_name_order_update(logs)

    def __load_map(self, path: str):
        self.interval_data = data = dict_from_json(path)
        for body_name in data:
            if body_name == 'logs':
                for name_body, logs in data['logs'].items():
                    self._logs[name_body] = []
                    for log in logs:
                        self._logs[name_body].append(Log())
                        self._logs[name_body][-1].load_from_dict(log)
            else:
                self.body_names.append(body_name)
                for x, y in [(x1, y1) for x1 in data[body_name] for y1 in data[body_name][x1]]:
                    self.max_x, self.max_y = max(self.max_x, int(x)), max(self.max_y, int(y))
                    for s_e in data[body_name][x][y]:
                        for z in range(s_e['s'], s_e['e'] + 1):
                            self.get_column(x, y).append((z, body_name))
                            self.max_z = z if z > self.max_x else z

        self.visible_names = self.body_names.copy()

    def get_column(self, x: int, y: int) -> [(int, str)]:
        x, y = str(x), str(y)
        if not self.columns.get(x):
            self.columns[x] = {}
        if not self.columns[x].get(y):
            self.columns[x][y] = []
        return self.columns[x][y]

    # def add_dot(self, x: int, y: int, z: int, name: str):
    #     self.get_column(x, y).append((z, name))

    def get_interval_column(self, x: Union[int, str], y: Union[int, str], body_name: str) -> [dict]:
        try:
            interval_column = self.interval_data[body_name][str(x)][str(y)]
            """
            body_name = 'Sand|A|O'
            body_name_OWK_param = 'O|W'
            body_name_without_param = 'Sand|A'
            interval_column = self.interval_data[body_name_without_param][str(x)][str(y)]
            
            
            
            if owc.get(body_name) is not None:
                owk_index = 0
                for s_e, i in zip(interval_column, range(len(interval_column))): 
                    if s_e['s'] <= owc[body_name] <= s_e['e']:
                        owk_index = i
                        o_s_e = {'s': s_e['s'], 'e': owc[body_name]}
                        w_s_e = {'s': owc[body_name], s_e['s']}
                if body_name_OWK_param == 'O'
                    interval_column = interval_column[:index]+[o_s_e] 
                if body_name_OWK_param == 'W'
                    interval_column = [w_s_e] + interval_column[index:]
            """
            print(body_name, interval_column)
            return self.interval_data[body_name][str(x)][str(y)]
        except KeyError or IndexError:
            return {}

    def save(self):
        self.interval_data['logs'] = {}
        for name, logs in self._logs.items():
            self.interval_data['logs'][name] = []
            for log in logs:
                self.interval_data['logs'][name].append(log.get_as_dict())
        return self.interval_data
