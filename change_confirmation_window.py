from change_confirmation import Ui_change_confirmation
from PyQt5.QtWidgets import QDialog, QCompleter, QMessageBox, QApplication
from PyQt5.QtCore import Qt,pyqtSignal
from queries import query_processor

class Change_confirmation_page(QDialog):
    def __init__(self, code, parent):
        super().__init__(parent)
        pass
