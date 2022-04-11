from functools import partial
from os import environ

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel

from mvc.Model.log_curves import Log, ExpressionLog
from mvc.Model.map import Map
from mvc.View.trend_view import TrendView
from utils.create_layout import create_frame, clear_layout
from utils.file import FileEdit, mass_from_xlsx


class CreateLog(QMainWindow):
    def __init__(self, data_map: Map):
        super(CreateLog, self).__init__()
        uic.loadUi(environ['project'] + '/ui/create_log_window.ui', self)
        print('s')
        self.data_map = data_map
        self.oil_water_name = ''
        self.handlers()
        self.update()
        self.excelFrame.hide()

    def handlers(self):
        self.addIntervalButton.clicked.connect(self.add_log_interval)
        self.chooseLogFile.clicked.connect(self.choose_log_from_xlsx)
        self.oilCurveCheckBox.clicked.connect(partial(self.change_name_oil_water_type, 'O'))
        self.waterCurveCheckBox.clicked.connect(partial(self.change_name_oil_water_type, 'W'))

        input_validator = QRegExpValidator(QRegExp("[^| ]{1,}"), self.nameLineEdit)
        self.nameLineEdit.setValidator(input_validator)

        for name in [''] + sorted(self.data_map.main_body_names()):
            self.layerNameComboBox.addItem(name)

        self.addCalculatedButton.clicked.connect(self.add_calculated_curve)

        self.curvesNameComboBox.textActivated.connect(self.add_curves_to_formula)

    def add_curves_to_formula(self):
        self.formulaLineEdit.setText(self.formulaLineEdit.text() + '{' + self.curvesNameComboBox.currentText() + '}')

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

    def get_log_name(self):
        name = self.nameLineEdit.text()
        log_name = (name + '|' + self.layerNameComboBox.currentText() + '|' + self.oil_water_name + '|')
        while log_name.__contains__('||'):
            log_name = log_name.replace('||', '|')
        return log_name

    def add_log_interval(self):
        log_name = self.get_log_name()
        if len(log_name) > 0:
            min_value, max_value = self.minValueSpinBox.value(), self.maxValueSpinBox.value()

            self.data_map.add_logs(Log(name=log_name, min=min_value, max=max_value))
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
        self.curvesNameComboBox.clear()

        for curve_name in sorted(self.data_map.main_logs_name_owc()):
            self.curvesNameComboBox.addItem(curve_name)
        self.create_frames_log()

    def add_calculated_curve(self):
        expr_log = ExpressionLog({log.name: log.x for log in self.data_map.all_logs}, self.formulaLineEdit.text())
        if expr_log():
            self.expressionValidLabel.setText(self.formulaLineEdit.text() + ' ok')
            label_change_color(self.expressionValidLabel, 'green')
            l = Log(name=self.get_log_name(), x=expr_log.x)
            l.text_expression = self.formulaLineEdit.text()
            self.data_map.add_logs(l)
        else:
            label_change_color(self.expressionValidLabel, 'red')
            self.expressionValidLabel.setText(self.formulaLineEdit.text() + ' error')
        self.update()

    def choose_log_from_xlsx(self):
        text = FileEdit(self).open_file('xlsx')
        for k, v in mass_from_xlsx(text).items():
            text += f'{k}\n{v}\n'
            self.data_map.add_logs(Log(name=k, x=v))
        self.fileTextBrowser.setText(text)
        self.update()


def label_change_color(lbl: QLabel, color: str):
    pal = lbl.palette()
    pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(color))
    lbl.setPalette(pal)
