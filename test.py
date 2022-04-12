import sys
from numbers import Number

from PyQt5.QtWidgets import QApplication

from mvc.View.setiings_view import SettingsView

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = SettingsView()
    w.show()
    sys.exit(app.exec_())