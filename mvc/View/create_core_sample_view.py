from functools import partial
from os import environ
from typing import Union

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QDoubleSpinBox, QComboBox, QLabel, QPushButton

from mvc.Model.map import Map
from mvc.Model.map_property import CoreSample
from utils.create_layout import create_frame


class CreateCoreSampleView(QMainWindow):
    def __init__(self, data_map: Map):
        super(CreateCoreSampleView, self).__init__()
        uic.loadUi(environ['project'] + '/ui/create_core_sample_window.ui', self)
        self.data_map = data_map
        self.before_start()
        self.handlers()
        self.update_info()

    def before_start(self):
        for log_name in self.data_map.main_logs_name():
            self.logComboBox.addItem(log_name)

        for lithology_name in self.data_map.main_body_names():
            self.lithologyComboBox.addItem(lithology_name.replace('|', ''))

    def handlers(self):
        self.lithologyComboBox: QComboBox = self.lithologyComboBox
        self.logComboBox: QComboBox = self.logComboBox
        self.nameLineEdit: QLineEdit = self.nameLineEdit
        self.nullValueLineEdit: QLineEdit = self.nullValueLineEdit
        self.addButton.clicked.connect(self.add_core_sample)
        self.percentSafeSpinBox: QDoubleSpinBox = self.percentSafeSpinBox
        self.percentSafeSpinBox.valueChanged.connect(self.percent_safe_change)

    def percent_safe_change(self):
        self.data_map.percent_safe_core = self.percentSafeSpinBox.value()
        self.set_percent_lbl(self.data_map.percent_safe_core)

    def add_core_sample(self):
        name = self.nameLineEdit.text()
        log_name = self.logComboBox.currentText()
        lithology_name = self.lithologyComboBox.currentText()
        null_value = self.nullValueLineEdit.text()
        self.data_map.add_core_sample((name, log_name, lithology_name, null_value))
        self.update_info()

    def pop_core_sample(self, core_sample: CoreSample):
        self.data_map.pop_core_sample(core_sample)
        self.update_info()

    def set_percent_lbl(self, value: Union[str, int, float]):
        self.percentLbl.setText(f'{round(value * 100, 1)}%')

    def update_info(self):
        widgets = []
        self.percentSafeSpinBox.setValue(self.data_map.percent_safe_core)
        self.set_percent_lbl(self.data_map.percent_safe_core)
        for c_s in self.data_map.core_samples:
            del_btn = QPushButton('❌')
            del_btn.setMaximumWidth(30)
            del_btn.clicked.connect(partial(self.pop_core_sample, c_s))
            q_label = QLabel(f'Name:{c_s[0]}  Log:{c_s[1]}  Lithology:{c_s[2]}  Null:{c_s[3]}')
            widgets.append([del_btn, q_label])

        create_frame(self.coreSmaplesLayout, widgets)
        self.update()
