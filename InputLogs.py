import os
import sys
from traceback import format_exception

from PyQt5.QtWidgets import QApplication

from mvc.View.input_log_view import InputLogView

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

