import math
import random
from typing import Optional

import numpy as np
from PyQt5.QtWidgets import QGridLayout
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from mvc.Model.map import Map
from utils.gisaug.augmentations import Stretch, DropRandomPoints


def draw_polygon(x, y, ax, size=1.0, color=None):
    int_x, int_y = int(x), int(y)
    x1, y1 = [int_x, int_x + size, int_x + size, int_x, int_x], [int_y, int_y, int_y + size, int_y + size, int_y]
    if color is None:
        ax.fill(x1, y1)
    else:
        ax.fill(x1, y1, color=color)


class ColorName:
    colors = ['blue', 'black', 'brown', 'green', 'yellow']
    data_name_colors = {}  # Name: color

    @staticmethod
    def add_color(color=None):
        if not color:
            ColorName.colors += ["#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])]

    @staticmethod
    def get_color(name: str) -> str:
        if ColorName.data_name_colors.get(name) is not None:
            return ColorName.data_name_colors[name]
        else:
            for color in ColorName.colors:
                if not (color in ColorName.data_name_colors.values()):
                    ColorName.data_name_colors[name] = color
                    return ColorName.data_name_colors[name]
        ColorName.add_color()


class PlotController(FigureCanvasQTAgg):
    def __init__(self, parent):
        FigureCanvasQTAgg.__init__(self, Figure(tight_layout=True))
        self.colors = ColorName
        self.mainLayout = QGridLayout(parent)
        self.mainLayout.addWidget(self)

        self.ax = self.figure.add_subplot()

    def plot_prepare(self, x: Optional[int], y: Optional[int]):
        if x is not None:
            self.ax.set_xlim(0, x)
        if y is not None:
            self.ax.set_ylim(0, y)

    def clear_plot(self):
        for artist in self.ax.get_lines() + self.ax.collections:
            artist.remove()
        self.ax.clear()

    def re_draw(self, data_map: Map):
        self.draw()


class PlotMapController(PlotController):
    def __init__(self, parent):
        super(PlotMapController, self).__init__(parent=parent)
        self.mpl_connect('button_press_event', self.on_click)
        self.on_choose_column_observer: [()] = []

    def plot_prepare(self, x: int, y: int):
        x_size = math.floor((x + 5) / 5) * 5
        y_size = math.floor((y + 5) / 5) * 5
        self.ax.xaxis.set_major_locator(MultipleLocator(x_size / 5))
        self.ax.yaxis.set_major_locator(MultipleLocator(y_size / 5))

        self.ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        self.ax.yaxis.set_minor_locator(AutoMinorLocator(5))

        self.ax.grid(which='major', color='#CCCCCC', linestyle='--')
        self.ax.grid(which='minor', color='#CCCCCC', linestyle=':')

        super(PlotMapController, self).plot_prepare(x_size, y_size)

    def on_click_notify(self, x: float, y: float):
        for observer in self.on_choose_column_observer:
            observer(x, y)

    def on_click(self, event: MouseEvent):
        x, y = event.xdata, event.ydata
        if x is not None and y is not None:
            self.on_click_notify(x, y)

    def clear_plot(self):
        draw_polygon(0, 0, self.ax, 100, color='white')
        super(PlotMapController, self).clear_plot()

    def re_draw(self, data_map: Map):
        self.draw_plot(data_map)
        self.draw()

    def draw_plot(self, data_map: Map):
        self.clear_plot()
        self.plot_prepare(data_map.max_x, data_map.max_y)
        for x1, y1 in [(x1, y1) for x1 in range(data_map.max_x + 1) for y1 in range(data_map.max_y + 1)]:
            for _, name in data_map.get_column(x1, y1):
                if name in data_map.visible_names:
                    draw_polygon(x1, y1, ax=self.ax, size=1, color=self.colors.get_color(name))
                    break


def get_random_logs(names: [str], target_name=None) -> [str]:
    names_struct = {}
    for name in names:
        main_name = name[:name.index('.')] if name.__contains__('.') else name
        names_struct[main_name] = [] if names_struct.get(main_name) is None else names_struct[main_name]
        names_struct[main_name].append(name)

    if target_name is None:
        return [random.choice(sub_names) for sub_names in names_struct.values()]
    return [random.choice(sub_names) for key, sub_names in names_struct.items() if key == target_name]


def realistic_transition(y1: [float], y2: [float]) -> ([float], [float]):
    y1min, y2min, y1max, y2max = min(y1), min(y2), max(y1), max(y2)
    drop_point_per = 0.1 * (max(y1max, y2max) - min(y1min, y2min)) / max(y1max - y1min, y2max - y2min)
    save_point_per = 1 - drop_point_per if drop_point_per < 0.5 else 0.5
    y_a, y_b = list(Stretch.stretch_curve(y1, save_point_per)), list(Stretch.stretch_curve(y2, save_point_per))

    average, start_value = y_b[0] - y_a[-1], y_a[-1]
    len_dist = len(y1) + len(y2) - len(y_a) - len(y_b) + 1

    step: () = lambda ind, l: average * ((random.random() / 2) * (1 - ind / l) + ind / l)
    middle = [start_value + step(ind, len_dist) for ind in range(1, len_dist)]
    y = y_a + middle + y_b

    offset_value = int(len(y) / 2)

    y_a = Stretch.stretch_curve_by_count(y[0:offset_value], len(y1))
    y_b = Stretch.stretch_curve_by_count(y[offset_value:], len(y2))
    return list(y_a), list(y_b)


class PlotLogController(PlotController):
    def __init__(self, parent):
        super(PlotLogController, self).__init__(parent=parent)
        self.mainLayout.addWidget(NavigationToolbar2QT(self, parent))
        self.x, self.y = 0, 0

    def re_draw(self, data_map: Map):
        self.draw_log(data_map, self.x, self.y)

    def draw_log(self, data_map: Map, x: float, y: float):
        self.clear_plot()
        self.plot_prepare(None, data_map.max_z)
        self.x, self.y = int(x), int(y)
        if not len(data_map.logs.keys()):
            return

        layer, columns = [], []

        for name in set(name for z, name in data_map.get_column(self.x, self.y)):
            for column in data_map.get_interval_column(self.x, self.y, name):
                columns.append((name, column))

        sort_columns = sorted(columns, key=lambda i: i[1]['s'])

        col_interval = []

        for name, column in sort_columns:
            if not len(data_map.logs[name]):
                continue

            log_name = sorted(data_map.logs[name], key=lambda i: i.main)[-1].name
            target_log_name = get_random_logs([log.name for log in data_map.logs[name]], log_name)[0]
            log = [log for log in data_map.logs[name] if log.name == target_log_name][0]

            color = ColorName.get_color(name)
            interval = range(int(column['s']), int(column['e']) + 1)
            if len(interval) > 1:
                curve = DropRandomPoints(0.95)(np.array(log.x))
                curve = Stretch.stretch_curve_by_count(curve, len(interval))

                layer.append({name: (curve, interval)})
                self.ax.bar(np.arange(1), len(interval), bottom=int(column['s']), color=color)
                col_interval.append((curve, name, interval))

        if len(col_interval) < 1:
            return

        col_pre = col_interval[0]

        curve_use_per = 0.2 + random.random() * 0.4

        for i in range(1, len(col_interval)):
            curve_p, name_p, interval_p = col_pre
            curve_n, name_n, interval_n = col_interval[i]

            min_len = min(len(interval_p), len(interval_n))
            start, end = len(interval_p) - int(min_len * curve_use_per), int(min_len * curve_use_per)
            y_a, y_b = realistic_transition(curve_p[start:], curve_n[:end])
            col_interval[i - 1] = (list(curve_p[:start]) + y_a, name_p, interval_p)
            col_interval[i] = (y_b + list(curve_n[end:]), name_n, interval_n)

            col_pre = col_interval[i]

        for x, name, y in col_interval:
            self.ax.plot(x, y, color=ColorName.get_color(name))
            self.ax.invert_yaxis()

        self.draw()
