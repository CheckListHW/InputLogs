from functools import partial
from os import environ

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QLabel, QSpinBox, QPushButton

from mvc.Model.map import Map
from utils.create_layout import create_frame, clear_layout


class OwcEditView(QMainWindow):
    def __init__(self, data_map: Map):
        super(OwcEditView, self).__init__()
        uic.loadUi(environ['project'] + '/ui/owc_edit_window.ui', self)
        self.data_map = data_map
        self.main_layer_name = ''
        self.handlers()
        self.update_info()

    def handlers(self):
        self.layerChooseComboBox.activated.connect(self.select_layer)
        self.addOwcButton.clicked.connect(self.update_info)

    def update_info(self):
        self.layerChooseComboBox.clear()
        names = set([name[:name.index('|')] for name in self.data_map.body_names])
        for name in names:
            self.layerChooseComboBox.addItem(name)

        self.owc_input_update()
        self.owc_info_update()

    def set_owc(self, name: str, value: ()):
        self.data_map.set_owc(name, value())
        self.owc_info_update()

    def pop_owc(self, name: str):
        self.data_map.pop_owc(name)
        self.update_info()

    def owc_info_update(self):
        for i in reversed(range(self.owcInfoGridLayout.count())):
            self.owcInfoGridLayout.itemAt(i).widget().setParent(None)

        widgets = []
        for k, v in self.data_map.owc.items():
            del_btn = QPushButton('❌')
            del_btn.clicked.connect(partial(self.pop_owc, k))

            widgets.append([del_btn, QLabel(f'{k}: owc = {v}')])

        create_frame(self.owcInfoGridLayout, widgets)

    def owc_input_update(self):
        clear_layout(self.owcInputGridLayout)

        names = [name for name in self.data_map.body_names if name[:name.index('|')] == self.main_layer_name]
        widgets = []
        for name in names:
            owc_value = self.data_map.owc.get(name)

            input_value = QSpinBox()
            input_value.setMinimumWidth(70)
            input_value.setMaximum(49999)
            input_value.setValue(0 if owc_value is None else owc_value)
            input_value.editingFinished.connect(partial(self.set_owc, name, input_value.value))

            widgets.append([QLabel(name), input_value])

        create_frame(self.owcInputGridLayout, widgets)

    def select_layer(self):
        self.main_layer_name = self.layerChooseComboBox.currentText()
        self.update_info()
