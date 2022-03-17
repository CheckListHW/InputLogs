from os import environ

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from mvc.Controller.plot_controller import PlotController, PlotMapController, PlotLogController
from mvc.Model.map import Map
from mvc.View.choose_log_view import ChooseLog
from utils.file import FileEdit


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

        self.map_controller = PlotMapController(self.mapPlotWidget)
        self.map_controller.on_choose_column_observer.append(self.redraw_and_log)
        self.log_controller = PlotLogController(self.logPlotWidget)
        self.main_controller = InputLogController([self.map_controller, self.log_controller])

        self.handlers()
        self.redraw()
        self.update_info()

    def update_info(self):
        self.chooseLayerComboBox.clear()
        self.chooseLayerComboBox.addItem('All')
        for name in self.data_map.body_names:
            self.chooseLayerComboBox.addItem(name)
        self.redraw()

    def handlers(self):
        self.openFileAction.triggered.connect(self.open_file)
        self.chooseLayerComboBox.activated.connect(self.choose_layer)
        self.chooseLogButton.clicked.connect(self.choose_log)
        self.startButton.clicked.connect(self.start)
        self.saveButton.clicked.connect(self.save_file)

    def save_file(self):
        self.data_map.save()

    def start(self):
        print('start')

    def open_file(self):
        path = FileEdit(self).open_file()
        self.data_map.load_map(path)
        self.update_info()

    def choose_log(self):
        self.window = ChooseLog(self.chooseLayerComboBox.currentText(), self.data_map)
        self.window.show()

    def redraw(self):
        self.main_controller.draw_all(self.data_map)

    def redraw_and_log(self, x: float, y: float):
        self.log_controller.draw_log(self.data_map, x, y)

    def choose_layer(self):
        if self.chooseLayerComboBox.currentText() == 'All':
            self.chooseLogButton.setEnabled(False)
            self.data_map.visible_names = self.data_map.body_names
        else:
            self.chooseLogButton.setEnabled(True)
            self.data_map.visible_names = self.chooseLayerComboBox.currentText()

        self.redraw()
