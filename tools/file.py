from os import getcwd
from typing import Final, Optional

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QInputDialog

from tools.filedialog import save_dict_as_json


class FileEdit:
    # Messages
    create_file_default: Final = 'Введите название файла:'
    create_file_error: Final = 'Не удалось создать файл,  \nфайл с таким именем уже существует'

    def __init__(self, parent: QMainWindow, file_used=''):
        self.parent = parent
        self.file_used = file_used

    def save_file(self, data: dict):
        if not self.file_used:
            self.create_file()
        save_dict_as_json(data=data, filename=self.file_used)

    def open_file(self, file_extension='json'):
        self.file_used, _ = QFileDialog.getOpenFileName(self.parent, '', getcwd(), f'Json Files (*.{file_extension})')
        return self.file_used

    def create_file(self, message=None) -> Optional[str]:
        if not message:
            message = self.create_file_default

        filename, ok = QInputDialog.getText(self.parent, 'Input Dialog', str(message))
        if ok and filename and filename != '':
            path = QFileDialog.getExistingDirectory(self.parent, getcwd())
            self.file_used = save_dict_as_json({}, path, filename)
            return self.file_used

        return None
