from functools import partial
from os import environ

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow

from mvc.Controller.plot_controller import PlotController, PlotMapController, PlotLogController
from mvc.Model.map import Map
from mvc.View.attach_log_view import AttachLogView
from mvc.View.create_log_view import ChooseLog
from mvc.View.owc_edit_view import OwcEditView
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
        self.file_edit = FileEdit(parent=self)
        self.data_map = Map()
        self.debug()

        self.map_controller = PlotMapController(self.mapPlotWidget)
        self.map_controller.on_choose_column_observer.append(self.redraw_log)
        self.log_controller = PlotLogController(self.logPlotWidget)
        self.main_controller = InputLogController([self.map_controller, self.log_controller])

        self.handlers()
        self.redraw()
        self.update_info()

    def debug(self):
        self.data_map.load_map('C:/Users/KosachevIV/PycharmProjects/InputLogs/base.json')
        self.file_edit.file_used = 'C:/Users/KosachevIV/PycharmProjects/InputLogs/base.json'

    def update_info(self):
        self.chooseLayerComboBox.clear()
        self.chooseLayerComboBox.addItem('All')

        for name in self.data_map.body_names:
            self.chooseLayerComboBox.addItem(name)

        self.logSelectComboBox.clear()
        for log_name in self.data_map.main_logs_name():
            self.logSelectComboBox.addItem(log_name)

        self.redraw()

    def handlers(self):
        self.openFileAction.triggered.connect(self.open_file)
        self.saveFileAction.triggered.connect(self.save_file)

        self.chooseLayerComboBox.activated.connect(self.choose_layer)
        self.startButton.clicked.connect(self.start)
        self.chooseLogButton.clicked.connect(partial(self.open_window, ChooseLog))
        self.owcButton.clicked.connect(partial(self.open_window, OwcEditView))
        self.attachLogButton.clicked.connect(partial(self.open_window, AttachLogView))
        self.logSelectComboBox.activated.connect(self.log_select)
        # self.saveButton.clicked.connect(self.save_file)

    def log_select(self):
        self.data_map.change_log_select(self.logSelectComboBox.currentText())
        self.redraw()

    def open_window(self, window: QMainWindow.__class__):
        if hasattr(self, 'sub_window'):
            self.sub_window.close()
            self.update_info()
        self.sub_window = window(self.data_map)
        self.sub_window.show()

    def save_file(self):
        self.file_edit.save_file(self.data_map.save())

    def start(self):
        print('start')

    def open_file(self):
        path = self.file_edit.open_file()
        self.data_map.load_map(path)
        self.update_info()

    def redraw(self):
        self.main_controller.draw_all(self.data_map)

    def redraw_log(self, x: float, y: float):
        self.log_controller.draw_log(self.data_map, x, y)

    def choose_layer(self):
        select_layer = self.chooseLayerComboBox.currentText()
        self.data_map.visible_names = self.data_map.body_names if select_layer == 'All' else [select_layer]

        self.redraw()
