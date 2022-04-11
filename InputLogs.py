import os
import sys
from traceback import format_exception

from PyQt5.QtWidgets import QApplication

from mvc.View.input_log_view import InputLogView
from utils.log_file import print_log

os.environ['project'] = os.getcwd()
os.environ['logs_file_path'] = os.environ['project'] + '/logs.txt'

log_out: ()


def console_excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(format_exception(exc_type, exc_value, exc_tb))
    print_log(tb)
    log_out(tb)
    print("error!:", tb)


if __name__ == '__main__':
    f = open(os.environ['logs_file_path'], 'w')
    f.write('')
    f.close()

    app = QApplication(sys.argv)
    sys.excepthook = console_excepthook
    window = InputLogView()
    window.show()
    log_out = window.set_log
    sys.exit(app.exec_())
