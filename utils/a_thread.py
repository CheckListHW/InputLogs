from PyQt5.QtCore import QThread


class AThread(QThread):
    def __init__(self):
        super().__init__()
        self.callback: () = lambda: None

    def run(self):
        self.callback()
