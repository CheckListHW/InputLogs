from functools import partial
from os import environ

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QHBoxLayout, QFrame, QRadioButton, QButtonGroup

from mvc.Model.log_curves import Log
from mvc.Model.map import Map
from utils.file import FileEdit, mass_from_xlsx


class ChooseLog(QMainWindow):
    def __init__(self, name: str, map: Map):
        super(ChooseLog, self).__init__()
        uic.loadUi(environ['project'] + '/ui/choose_log_window.ui', self)
        self.map = map
        self.master_name = name
        self.nameLogLabel.setText(self.nameLogLabel.text().replace('`name`', name))

        self.handlers()
        self.update()

    def handlers(self):
        self.addIntervalButton.clicked.connect(self.add_log_interval)
        self.chooseLogFile.clicked.connect(self.choose_log_from_xlsx)

    def add_log_interval(self):
        name, min_value, max_value = self.nameLineEdit.text(), self.minValueSpinBox.value(), self.maxValueSpinBox.value()
        self.map.logs[self.master_name].append(Log(name=name, min=min_value, max=max_value))
        self.update()

    def delete_log(self, i: int):
        self.map.logs[self.master_name].pop(i)
        self.update()

    def change_main(self, logs: [Log], log: Log):
        for l in logs:
            l.main = False if l is not log else True

    def create_frames_log(self):
        radio_group = QButtonGroup(self)
        logs = self.map.logs[self.master_name]
        for log, i in zip(logs, range(len(self.map.logs[self.master_name]))):
            y = QFrame()
            x = QHBoxLayout(y)

            del_btn = QPushButton('-')
            del_btn.setMaximumWidth(30)
            del_btn.clicked.connect(partial(self.delete_log, i))

            main_radio = QRadioButton()
            main_radio.clicked.connect(partial(self.change_main, logs, log))

            main_radio.setEnabled(not log.name.__contains__('.'))
            radio_group.addButton(main_radio)

            x.addWidget(main_radio)
            x.addWidget(del_btn)
            x.addWidget(QLabel(log.get_text()))
            x.addStretch()

            self.logsScrollArea.addWidget(y, i, 0)

    def update(self):
        for i in reversed(range(self.logsScrollArea.count())):
            self.logsScrollArea.itemAt(i).widget().setParent(None)
        self.create_frames_log()

    def choose_log_from_xlsx(self):
        text = FileEdit(self).open_file('xlsx')
        for k, v in mass_from_xlsx(text).items():
            text += f'{k}\n{v}\n'
            self.map.logs[self.master_name].append(Log(name=k, x=v))
        self.fileTextBrowser.setText(text)
        self.update()
