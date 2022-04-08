import math
import random
from typing import Optional

import numpy as np
from PyQt5.QtWidgets import QGridLayout
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseEvent, MouseButton
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from mvc.Model.log_curves import Log
from mvc.Model.map import Map
from resourses.limits import MAX_TREND_RATIO
from utils.gisaug.augmentations import Stretch, DropRandomPoints


def draw_polygon(x: float, y: float, ax: Axes, size=1.0, color: str = None):
    int_x, int_y = int(x), int(y)
    x1, y1 = [int_x, int_x + size, int_x + size, int_x, int_x], [int_y, int_y, int_y + size, int_y + size, int_y]
    ax.fill(x1, y1, color=color)


def draw_bar(ax: Axes, x: float, y: float, size_x: float = None, size_y: float = None, color: str = None, alpha=1.0):
    x1, y1 = [x, x + size_x, x + size_x, x, x], [y, y, y + size_y, y + size_y, y]
    ax.fill(x1, y1, color=color, alpha=alpha)


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
        if x is not None and x > 0:
            self.ax.set_xlim(0, x)
        if y is not None and y > 0:
            self.ax.set_ylim(0, y)

    def clear_plot(self):
        for artist in self.ax.get_lines() + self.ax.collections:
            artist.remove()
        self.ax.clear()

    def re_draw(self, data_map: Map):
        self.draw()


class PlotTrendController(PlotController):
    def __init__(self, parent):
        super(PlotTrendController, self).__init__(parent=parent)
        self.mpl_connect('button_press_event', self.on_click)
        self.on_click_observer: [(float, float, MouseButton)] = []

    def on_click_notify(self, x: float, y: float, button: MouseButton):
        for observer in self.on_click_observer:
            observer(x, y, button)

    def on_click(self, event: MouseEvent):
        x, y = event.xdata, event.ydata
        if x is not None and y is not None:
            self.on_click_notify(x, y, event.button)

    def draw_trend(self, log: Log):
        self.clear_plot()
        self.ax.set_xlim(-MAX_TREND_RATIO, MAX_TREND_RATIO)
        self.ax.set_ylim(0, 1)

        x, y = [x for x, _ in log.trend], [y for _, y in log.trend]
        self.ax.plot(x, y, linewidth=5)
        xs, ys = log.trend_point
        self.ax.scatter(xs, ys)
        self.ax.invert_yaxis()
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
        visible_names = data_map.visible_names
        names = []
        for x1, y1 in [(x1, y1) for x1 in range(data_map.max_x + 1) for y1 in range(data_map.max_y + 1)]:
            for col in data_map.get_column(x1, y1):
                name = col['name']
                names.append(name)
                if name in visible_names:
                    draw_polygon(x1, y1, ax=self.ax, size=1, color=self.colors.get_color(name))
                    break


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

        col_interval = data_map.get_column_curve(self.x, self.y)

        if col_interval:
            x = [a for b in [x for x, _, _ in col_interval.intervals] for a in b]
            y = [a for b in [y for _, _, y in col_interval.intervals] for a in b]
            self.ax.plot(x, y, color='black')

            min_axes_x, max_axes_x, pre_max_y = col_interval.min, col_interval.max, 0

            for x, name, y in col_interval.intervals:
                max_y, min_y, color = max(y), min(y), ColorName.get_color(name)
                connect_to_pre_interval = 1 if min_y > pre_max_y else 0
                draw_bar(self.ax, min_axes_x, min_y - connect_to_pre_interval, size_x=max_axes_x - min_axes_x,
                         size_y=max_y - min_y + connect_to_pre_interval, color=color, alpha=0.2)

                pre_max_y = max_y

            self.ax.set_xlim(min_axes_x, max_axes_x)
            self.ax.invert_yaxis()
        self.draw()


