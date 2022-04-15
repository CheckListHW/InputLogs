from functools import partial
from random import random

import pandas as pd

from mvc.Model.log_curves import Log, sort_expression_logs, expression_parser
from mvc.Model.map_property import CoreSample, cut_along, MapProperty
from utils.a_thread import AThread
from utils.log.log_file import print_log


class ExportLogs:
    def __init__(self, data_map: MapProperty):
        self.data_map = data_map
        self.export_threads = []

    def export_on_thread(self, export_method: callable, path: str):
        export_thread = AThread()
        export_thread.finished.connect(lambda: print_log('Finish export Excel'))
        export_thread.callback = partial(export_method, path)
        export_thread.start()
        self.export_threads.append(export_thread)

    def to_xlsx(self, path: str):
        self.export_on_thread(self.__to_xlsx, path)

    def __to_xlsx(self, path: str):
        save_to_excel(self.export(), path)

    def to_csv(self, path: str):
        self.export_on_thread(self.__to_csv, path)

    def __to_csv(self, path: str):
        save_to_csv(self.export(), path)

    def to_t_nav(self, path: str):
        self.export_on_thread(self.__to_t_nav, path)

    def __to_t_nav(self, path: str):
        save_to_t_nav(self.export(), path)

    def export(self):
        print_log('Start transform data')
        data_map = MapProperty(data=self.data_map.save())
        print(data_map.owc)

        data = {}
        for log_name in data_map.main_logs_name_non_expression():
            data_map.change_log_select(log_name)
            for x, y in [(x1, y1) for x1 in range(data_map.max_x + 1) for y1 in range(data_map.max_y + 1)]:
                column = data_map.get_column_curve(x, y)
                for x1, n, y1 in (column.intervals if column else []):
                    for i in range(len(x1)):
                        ceil_name = f'{x}-{y}-{y1[i]}'
                        if not data.get(ceil_name):
                            data[ceil_name] = {'i': x + 1, 'j': y + 1, 'index': y1[i], 'Lithology': n}
                        data[ceil_name][log_name] = x1[i]

        data = add_height_above_fwl(data, data_map.owc)
        data = index_to_depth(data, lambda i: i * self.data_map.step_depth + self.data_map.initial_depth)
        data = add_log_expression_in_export(data, data_map.attach_logs)
        data = edit_lithology_name_in_data(data)
        data = add_log_sample_in_export(data, data_map.core_samples, self.data_map.percent_safe_core)

        print_log('Data ready')
        return data


def index_to_depth(data: {}, depth: ()) -> {}:
    for values in data.values():
        values['old_index'] = values['index']
        values['index'] = depth(values['index'])
    return data


def add_height_above_fwl(data: {}, owc: [{str: float}]) -> {}:
    owc_names = owc.keys()
    for values in data.values():
        if values['Lithology'] in owc_names:
            owc_level = owc[values['Lithology']]
            if values['index'] < owc_level:
                values['HeightAboveFWL'] = owc_level - values['index']

    return data


def edit_lithology_name_in_data(data: {}) -> {}:
    for values in data.values():
        values['Lithology'] = cut_along(values['Lithology'], '|')
    return data


def add_log_expression_in_export(data: dict, logs: {str: [Log]}) -> dict:
    expressions = {}
    expression_logs = list({l for l in [a for b in logs.values() for a in b]
                            if expression_parser(l.text_expression) is not None})

    sorted_expression_logs = sort_expression_logs(expression_logs)

    texts_expressions = []
    for lay_name, v in logs.items():
        for log in v:
            if expression_parser(log.text_expression) is None:
                continue

            log_name = log.name
            expressions[log_name] = {} if not expressions.get(log_name) else expressions[log_name]
            expressions[log_name][lay_name] = expression_parser(log.text_expression)
            texts_expressions.append(log.text_expression)

    for log in sorted_expression_logs:
        log_name_expression = log.name
        short_log_name_expression = log_name_expression[:log_name_expression.index('|')]
        exps = expressions[log_name_expression]
        for k, v in data.items():
            try:
                if exps.get(data[k]['Lithology']):
                    data[k][short_log_name_expression] = exps[data[k]['Lithology']](v)
                if data[k].get(short_log_name_expression) is None:
                    data[k][short_log_name_expression] = -9999
            except KeyError or AttributeError:
                print_log(f'{log_name_expression} ; {v.keys()} ; {v["Lithology"]}')
                break

    return data


def add_log_sample_in_export(data: dict, core_samples: [CoreSample], percent: float) -> dict:
    for k in data.keys():
        check_percent = random() > percent
        for name_core_sample, log_name, lithology, null_value in core_samples:
            data[k][name_core_sample] = null_value
            if check_percent:
                continue
            if data[k]['Lithology'] != lithology:
                continue
            if data[k].get(log_name) is None:
                continue
            data[k][name_core_sample] = data[k][log_name] * ((random() - 0.5) / 10 + 1)
    return data


def prepare_dataframe_to_save(data: dict) -> pd.DataFrame:
    columns_name = set([a for b in [list(v.keys()) for v in data.values()] for a in b])
    return pd.DataFrame([row for _, row in data.items()], columns=columns_name)


def save_to_t_nav(data: [], path: str):
    print_log('Start save TNavigator(.inc)')
    data_str = ''
    df = prepare_dataframe_to_save(data).sort_values(by=['index', 'j']).drop(['i', 'j', 'index', 'Lithology'], axis=1)
    for data_name, column in df.items():
        data_str += f'{data_name} '
        for value, i in zip(column, range(len(column))):
            if i % 7 == 0:
                data_str += '\n'
            try:
                value = round(float(value), 5)
            except:
                pass
            data_str += f"1*{value} "
        data_str += '/ \n'

    file = open(path, 'w+')
    file.write(data_str)
    file.close()
    print_log('Export to TNavigator (.inc) is finish save to:' + path)
    print_log(f'Numer of ceil: {len(df)}')


def save_to_excel(data: [], path: str):
    print_log('Start save Excel (.xlsx)')
    prepare_dataframe_to_save(data).to_excel(path, sheet_name='all')
    print_log('Export to Excel(.xlsx) is finish save to:' + path)


def save_to_csv(data: [], path: str):
    print_log('Start save .csv')
    prepare_dataframe_to_save(data).to_csv(path)
    print_log('Export to .csv is finish save to:' + path)
