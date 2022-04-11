import os
import sys

from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QWidget, QScrollArea

from mvc.View.list_scroll_widget import ListScrollWidgets, Window

os.environ['project'] = os.getcwd()


if __name__ == '__main__':
    x = {1, 2}.union({1}).symmetric_difference({4})
    print(x)
    # app = QApplication(sys.argv)
    # parent = QWidget()
    # parent.show()
    # parent.setLayout(QHBoxLayout(parent))
    # scroll = ListScrollWidgets(parent)
    # parent.layout().addWidget(scroll)
    # for i in range(5):
    #     widgets = [QLabel("hello") for _ in range(20)]
    #     scroll.add_scroll(widgets, str('-'.join([str(i) for _ in range(6)])))
    # sys.exit(app.exec_())

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     scroll = Window()
#     scroll.show()
#     sys.exit(app.exec_())