from PyQt5.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout, QScrollArea


class ListScrollWidgets(QScrollArea):
    def __init__(self, parent: QWidget):
        super(ListScrollWidgets, self).__init__(parent)
        if self.parent().layout() is None:
            self.parent().setLayout(QVBoxLayout(self))
        # self.parent().layout().setContentsMargins(0, 0, 0, 0)

        self.parent().layout().addWidget(self)
        self.scroll_layout = QHBoxLayout(self)
        self.scroll = QWidget(self)
        self.scroll.setLayout(self.scroll_layout)
        self.scroll.layout().setContentsMargins(0, 0, 0, 0)
        self.scroll.layout().setSpacing(0)
        # self.scroll.setFixedHeight(400)

        self.setWidgetResizable(True)
        self.setWidget(self.scroll)

    def add_scroll(self, widgets: [QWidget]):
        widgets_frame = QWidget()
        widgets_frame.setLayout(QVBoxLayout(widgets_frame))

        for widget in widgets:
            widget.setFixedHeight(40)
            widgets_frame.layout().addWidget(widget)

        widgets_frame.layout().setContentsMargins(0, 0, 0, 0)
        widgets_frame.setFixedWidth(200)
        widgets_frame.layout().addStretch()

        self.scroll_layout.addWidget(widgets_frame)
