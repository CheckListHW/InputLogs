import math
import random

import numpy as np
from PyQt5.QtWidgets import QWidget, QGridLayout
from matplotlib.backend_bases import MouseEvent
from matplotlib.backends.backend_qt import NavigationToolbar2QT
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

from Model.map import Map


def draw_polygon(x, y, ax, size=1.0, color='brown'):
    int_x, int_y = int(x), int(y)
    ax.fill([int_x, int_x + size, int_x + size, int_x, int_x],
            [int_y, int_y, int_y + size, int_y + size, int_y], color=color)


class ColorName:
    colors = ['blue', 'yellow', 'black', 'brown', 'green']
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
        # self.mainLayout.addWidget(NavigationToolbar2QT(self, parent))

        self.ax = self.figure.add_subplot()

    def re_draw(self, data_map: Map):
        self.draw()

    def plot_prepare(self, x: int, y: int):
        self.ax.set_xlim(0, x)
        self.ax.set_ylim(0, y)

    def clear_plot(self):
        for artist in self.ax.get_lines() + self.ax.collections:
            artist.remove()
        self.ax.clear()


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
        self.on_click_notify(x, y)

    def clear_plot(self):
        draw_polygon(0, 0, self.ax, 100, color='white')
        super(PlotMapController, self).clear_plot()

    def re_draw(self, data_map: Map):
        self.clear_plot()
        self.plot_prepare(data_map.max_x, data_map.max_y)
        for x1 in range(data_map.max_x + 1):
            for y1 in range(data_map.max_y + 1):
                col = data_map.get_column(x1, y1)
                for _, name in col:
                    if name in data_map.visible_names:
                        draw_polygon(x1, y1, ax=self.ax, size=1, color=self.colors.get_color(name))
                        break
        super(PlotMapController, self).re_draw(data_map)


class PlotBarController(PlotController):
    def __init__(self, parent):
        super(PlotBarController, self).__init__(parent=parent)
        self.x, self.y = 0, 0

    def draw_bar(self, data_map: Map, x: float, y: float):
        self.x, self.y = round(x), round(y)
        self.re_draw(data_map)

    def re_draw(self, data_map: Map):
        self.clear_plot()
        names = set(name for z, name in data_map.get_column(self.x, self.y))
        print(self.x, self.y)
        print(data_map.get_column(self.x, self.y))
        for name in names:
            for v in [z for z, data_name in data_map.get_column(self.x, self.y) if name == data_name]:
                self.ax.bar(np.arange(1), 1, color=ColorName.get_color(name), bottom=v)
        super(PlotBarController, self).re_draw(data_map)


class PlotLogController(PlotController):
    def __init__(self, parent):
        super(PlotLogController, self).__init__(parent=parent)
        self.x, self.y = 0, 0

    def draw_plot(self, data_map: Map, x: float, y: float):
        self.x, self.y = x, y
        self.re_draw(data_map)

    def re_draw(self, data_map: Map):
        self.clear_plot()

        self.draw()