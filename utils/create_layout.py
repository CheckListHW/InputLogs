from PyQt5.QtWidgets import QGridLayout, QWidget, QHBoxLayout, QFrame


def clear_layout(layout: QGridLayout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)


def create_frame(layout: QGridLayout, widgets: [[QWidget]]):
    clear_layout(layout)
    for frame_widgets, i in zip(widgets, range(len(widgets))):
        y = QFrame()
        x = QHBoxLayout(y)

        for widget in frame_widgets:
            x.addWidget(widget)

        x.addStretch()
        layout.addWidget(y, i, 0)
