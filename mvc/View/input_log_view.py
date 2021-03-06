import os
import time
from functools import partial
from os import environ
from threading import Thread

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QPushButton

from mvc.View.setiings_view import SettingsView
from utils.log.log_file import read_log
from mvc.Controller.plot_controller import PlotController, PlotMapController, PlotLogController
from mvc.Model.map import Map
from mvc.View.attach_log_view import AttachLogView
from mvc.View.create_core_sample_view import CreateCoreSampleView
from mvc.View.create_log_view import CreateLog
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
        self.text_log = ''
        self.file_edit = FileEdit(parent=self)
        self.data_map = Map()
        self.debug()

        self.map_controller = PlotMapController(self.mapPlotWidget)
        self.map_controller.on_choose_column_observer.append(self.redraw_log)
        self.log_controller = PlotLogController(self.logPlotWidget)
        self.main_controller = InputLogController([self.map_controller, self.log_controller])

        self.handlers()
        self.update_info()
        self.log_select()
        x = Thread(target=partial(CreateCoreSampleView, self.data_map))
        x.start()
        Thread(target=self.update_log).start()

    def update_log(self):
        x = QPushButton()
        x.clicked.connect(self.__set_log)
        while self.isVisible():
            time.sleep(3)
            x.click()

    def __set_log(self):
        text = str(read_log())
        if len(text) > 500:
            if text[-500:] != str(self.logText.toPlainText())[-500:]:
                text = text[-500:]
        else:
            if text != str(self.logText.toPlainText()):
                text = text
        self.set_log(text)

    def set_log(self, text: str):
        self.logText.setText(text)

    def debug(self):
        path = os.environ['project'] + '/base.json'
        self.data_map.load_map(path)
        self.file_edit.file_used = path

    def update_info(self):
        self.chooseLayerComboBox.clear()
        self.chooseLayerComboBox.addItem('All')

        for name in sorted(self.data_map.body_names):
            self.chooseLayerComboBox.addItem(name)

        self.logSelectComboBox.clear()
        for log_name in sorted(self.data_map.main_logs_name()):
            self.logSelectComboBox.addItem(log_name)

        self.redraw()

    def handlers(self):
        self.openFileAction.triggered.connect(self.open_file)
        self.saveFileAction.triggered.connect(self.save_file)
        self.exportSettingsAction.triggered.connect(partial(self.open_window, SettingsView))

        self.chooseLayerComboBox.activated.connect(self.choose_layer)
        self.chooseLogButton.clicked.connect(partial(self.open_window, CreateLog))
        self.owcButton.clicked.connect(partial(self.open_window, OwcEditView))
        self.attachLogButton.clicked.connect(partial(self.open_window, AttachLogView))
        self.createCoreSampleButton.clicked.connect(partial(self.open_window, CreateCoreSampleView))
        self.logSelectComboBox.activated.connect(self.log_select)

        self.actionTNavigator_inc.triggered.connect(partial(self.export, 'tnav'))
        self.actionXLSX.triggered.connect(partial(self.export, 'xlsx'))
        self.actionCSV.triggered.connect(partial(self.export, 'csv'))

    def export(self, type_file: str = 'csv'):
        file_path = FileEdit(self).create_file(extension='')
        if file_path:
            Thread(target=partial(self.__export, type_file, file_path)).start()

    def __export(self, type_file: str, file_path: str):
        if type_file == 'csv':
            self.data_map.export.to_csv(file_path + 'csv')
        elif type_file == 'xlsx':
            self.data_map.export.to_xlsx(file_path + 'xlsx')
        elif type_file == 'tnav':
            self.data_map.export.to_t_nav(file_path + 'inc')
        else:
            self.data_map.export.to_csv(file_path)

    def log_select(self):
        self.data_map.change_log_select(self.logSelectComboBox.currentText())
        self.redraw()

    def open_window(self, window: QMainWindow.__class__):
        if hasattr(self, 'sub_window'):
            self.sub_window.close()
            self.update_info()
        self.sub_window: QMainWindow = window(self.data_map)
        self.sub_window.show()

    def save_file(self):
        self.file_edit.save_file(self.data_map.save())

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
