from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDoubleSpinBox

from mvc.Model.map import Map


class SettingsView(QWidget):
    def __init__(self, data_map: Map):
        super(SettingsView, self).__init__()
        self.setWindowTitle('Settings')
        self.data_map = data_map
        self.label_name_width = 70
        self.input_value_width = 150
        self.setLayout(QVBoxLayout(self))

        # self.file_name_line_edit = QLineEdit()
        # self.add_row_property('File name', self.file_name_line_edit)

        self.initial_depth_spin_box = QDoubleSpinBox()
        self.initial_depth_spin_box.setMaximum(5000)
        self.initial_depth_spin_box.setValue(self.data_map.initial_depth)
        self.add_row_property('Initial Depth', self.initial_depth_spin_box)

        self.step_depth_spin_box = QDoubleSpinBox()
        self.step_depth_spin_box.setValue(self.data_map.step_depth)
        self.add_row_property('Depth step', self.step_depth_spin_box)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save)
        self.cancel_button = QPushButton('cancel')

        dialog = QWidget(self)
        dialog.setLayout(QHBoxLayout())
        dialog.layout().addWidget(self.save_button)
        dialog.layout().addWidget(self.cancel_button)
        self.layout().addWidget(dialog)

    def save(self):
        self.data_map.initial_depth = self.initial_depth_spin_box.value()
        self.data_map.step_depth = self.step_depth_spin_box.value()
        self.close()

    def add_row_property(self, name, value_input: QWidget):
        file_w = QWidget(self)
        file_w.setLayout(QHBoxLayout())

        lbl = QLabel(f'{name}: ')
        lbl.setFixedWidth(self.label_name_width)

        value_input.setFixedWidth(self.input_value_width)

        file_w.layout().addWidget(lbl)
        file_w.layout().addWidget(value_input)

        file_w.layout().addStretch()

        self.layout().addWidget(file_w)
