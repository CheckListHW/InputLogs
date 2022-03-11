from os import environ

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QComboBox

from Model.map import Map
from Controller.plot_controller import PlotController, PlotMapController, PlotBarController, PlotLogController
from tools.file import FileEdit


class InputLogController:
    def __init__(self, controllers: [PlotController]):
        self.controllers = controllers

    def draw_all(self, data_map: Map):
        for controller in self.controllers:
            controller.re_draw(data_map)


class InputLogView(QMainWindow):
    def __init__(self):
        super(InputLogView, self).__init__()
        uic.loadUi(environ['project'] + '/ui/log_input_form.ui', self)
        self.data_map = Map()
        self.data_map.load_map('C:/Users/KosachevIV/PycharmProjects/InputLogs/data_files/lay_name30.json')
        self.data_map.load_curves('C:/Users/KosachevIV/PycharmProjects/InputLogs/data_files/test.xlsx')

        self.map_controller = PlotMapController(self.mapPlotWidget)
        self.map_controller.on_choose_column_observer.append(self.redraw_bar_and_log)
        self.bar_chart_controller = PlotBarController(self.barChartPlotWidget)
        self.log_controller = PlotLogController(self.logPlotWidget)
        self.main_controller = InputLogController(
            [self.map_controller, self.bar_chart_controller, self.log_controller])

        self.handlers()
        self.redraw()
        self.update_info()

    def update_info(self):
        for name in self.data_map.body_names:
            self.chooseLayerComboBox.addItem(name)
        self.chooseLayerComboBox.addItem('All')

    def handlers(self):
        self.openFileAction.triggered.connect(self.open_file)
        self.chooseLayerComboBox.activated.connect(self.choose_layer)
        self.chooseLogButton.clicked.connect(self.choose_log)
        self.startButton.clicked.connect(self.start)

    def start(self):
        print('start')

    def open_file(self):
        path = FileEdit(self).open_file()
        self.data_map.load_map(path)

    def choose_log(self):
        path = FileEdit(self).open_file('xlsx')
        print(path)

    def redraw(self):
        self.main_controller.draw_all(self.data_map)

    def redraw_bar_and_log(self, x: float, y: float):
        self.bar_chart_controller.draw_bar(self.data_map, x, y)
        self.log_controller.draw_plot(self.data_map, x, y)

    def choose_layer(self):
        if self.chooseLayerComboBox.currentText() == 'All':
            self.data_map.visible_names = self.data_map.body_names
        else:
            self.data_map.visible_names = self.chooseLayerComboBox.currentText()

        self.redraw()
