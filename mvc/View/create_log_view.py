from functools import partial
from os import environ

from PyQt5 import uic
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QCheckBox

from mvc.Model.log_curves import Log
from mvc.Model.map import Map
from mvc.View.trend_view import TrendView
from utils.create_layout import create_frame, clear_layout
from utils.file import FileEdit, mass_from_xlsx


class ChooseLog(QMainWindow):
    def __init__(self, data_map: Map):
        super(ChooseLog, self).__init__()
        uic.loadUi(environ['project'] + '/ui/create_log_window.ui', self)
        self.data_map = data_map
        self.oil_water_name = ''
        self.handlers()
        self.update()

    def handlers(self):
        self.addIntervalButton.clicked.connect(self.add_log_interval)
        self.chooseLogFile.clicked.connect(self.choose_log_from_xlsx)
        self.oilCurveCheckBox: QCheckBox = self.oilCurveCheckBox
        self.oilCurveCheckBox.clicked.connect(partial(self.change_name_oil_water_type, 'O'))
        self.waterCurveCheckBox.clicked.connect(partial(self.change_name_oil_water_type, 'W'))

        input_validator = QRegExpValidator(QRegExp("[^| ]{1,}"), self.nameLineEdit)
        self.nameLineEdit.setValidator(input_validator)

    def change_name_oil_water_type(self, name: str):
        if name == 'O' and self.oilCurveCheckBox.isChecked():
            self.oil_water_name = '|O|'
            self.waterCurveCheckBox.setCheckState(False)
        elif name == 'W' and self.waterCurveCheckBox.isChecked():
            self.oil_water_name = '|W|'
            self.oilCurveCheckBox.setCheckState(False)
        else:
            self.oil_water_name = ''

    def open_trend_window(self, log: Log):
        if hasattr(self, 'trend_window'):
            self.trend_window.close()

        self.trend_window = TrendView(log)
        self.trend_window.show()
        self.trend_window.closeEvent = lambda _: self.update()

    def add_log_interval(self):
        name, min_value, max_value = self.nameLineEdit.text(), self.minValueSpinBox.value(), self.maxValueSpinBox.value()
        if len(name) <= 0:
            return
        self.data_map.add_logs(Log(name=name+self.oil_water_name, min=min_value, max=max_value))
        self.update()

    def delete_log(self, name: str):
        self.data_map.pop_logs(name)
        self.update()

    def create_frames_log(self):
        widgets = []
        for log in self.data_map.all_logs:
            widgets.append([])
            del_btn = QPushButton('❌')
            del_btn.setMaximumWidth(30)
            del_btn.clicked.connect(partial(self.delete_log, log.name))
            widgets[-1].append(del_btn)

            if not log.get_text().__contains__('xlsx'):
                trend_btn = QPushButton('⚡')
                trend_btn.setMaximumWidth(30)
                trend_btn.clicked.connect(partial(self.open_trend_window, log))
                widgets[-1].append(trend_btn)

            widgets[-1].append(QLabel(log.get_text()))

        create_frame(self.logsScrollArea, widgets)

    def update(self):
        clear_layout(self.logsScrollArea)
        self.create_frames_log()

    def choose_log_from_xlsx(self):
        text = FileEdit(self).open_file('xlsx')
        for k, v in mass_from_xlsx(text).items():
            text += f'{k}\n{v}\n'
            self.data_map.add_logs(Log(name=k, x=v))
        self.fileTextBrowser.setText(text)
        self.update()
