import os
import sys
from traceback import format_exception

import numpy as np
from matplotlib import pyplot as plt

from Model.map import Map
from View.input_log_view import InputLogView
from PyQt5.QtWidgets import QApplication

os.environ['project'] = os.getcwd()


def console_excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(format_exception(exc_type, exc_value, exc_tb))
    print("error!:", tb)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.excepthook = console_excepthook
    window = InputLogView()
    window.show()
    sys.exit(app.exec_())

# if __name__ == '__main__':
#     fig = plt.figure()
#     ax = fig.add_subplot(111)
#     data_map = Map()
#     data_map.load_map('C:/Users/KosachevIV/PycharmProjects/InputData/lay_name133.json')
#
#     names = set(name for z, name in data_map.get_column(13, 12))
#     for name, color in zip(names, ['r', 'b', 'g', 'y']):
#         value = [z for z, data_name in data_map.get_column(13, 12) if name == data_name]
#         print(value)
#         for v in value:
#             plt.bar(np.arange(1), 1, color=color, bottom=v)
#
#     plt.show()
