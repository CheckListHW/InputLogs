from functools import partial
from os import environ

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QLabel, QCheckBox, QPushButton

from mvc.Model.map import Map
from utils.create_layout import create_frame, clear_layout


class AttachLogView(QMainWindow):
    def __init__(self, data_map: Map):
        super(AttachLogView, self).__init__()
        uic.loadUi(environ['project'] + '/ui/attach_log_window.ui', self)
        self.data_map = data_map
        self.attach_layers = set([])
        self.attach_logs = set([])
        self.handlers()
        self.update()
        self.create_frames_info()

    def handlers(self):
        self.addButton.clicked.connect(self.start_attach_logs)

    def start_attach_logs(self):
        for lay_name, log_name in [(lay, log) for lay in self.attach_layers for log in self.attach_logs]:
            self.data_map.attach_log_to_layer(log_name, lay_name)

        self.attach_layers = set([])
        self.attach_logs = set([])
        self.create_frames_info()

    def create_frames_info(self):
        clear_layout(self.infoGridLayout)
        widgets, names = [], []

        for lay_name, log_name in self.data_map.attach_list():
            log = self.data_map.get_logs_by_name(log_name)

            del_btn = QPushButton('❌')
            del_btn.setMaximumWidth(30)
            del_btn.clicked.connect(partial(self.detach_log, lay_name, log_name))
            widgets.append([del_btn, QLabel(f'{lay_name}: {log_name if log is None else log.get_text()}')])

        create_frame(self.infoGridLayout, widgets)
        self.update()

    def create_frames_layers(self):
        widgets = []
        for name in self.data_map.main_body_names_owc():
            layer_check = QCheckBox()
            layer_check.setMaximumWidth(30)
            layer_check.clicked.connect(partial(self.add_layer, layer_check.checkState, name))
            widgets.append([layer_check, QLabel(name)])

        create_frame(self.layersGridLayout, widgets)

    def create_frames_logs(self):
        widgets = []
        for log in self.data_map.logs_without_sub():
            log_check = QCheckBox()
            log_check.setMaximumWidth(30)
            log_check.clicked.connect(partial(self.add_logs, log_check.checkState, log.name))
            widgets.append([log_check, QLabel(log.get_text())])

        create_frame(self.logsGridLayout, widgets)

    def add_logs(self, state: (), name: str):
        if state():
            self.attach_logs.add(name)
        else:
            self.attach_logs = self.attach_logs - {name}

    def add_layer(self, state: (), name: str):
        if state():
            self.attach_layers.add(name)
        else:
            self.attach_layers = self.attach_layers - {name}

    def detach_log(self, lay_name: str, log_name: str):
        self.data_map.detach_log_to_layer(log_name, lay_name)
        self.create_frames_info()

    def update(self):
        clear_layout(self.logsGridLayout)
        clear_layout(self.layersGridLayout)
        self.create_frames_logs()
        self.create_frames_layers()
