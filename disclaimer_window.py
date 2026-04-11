import os
from decouple import config
from PyQt5.QtWidgets import QDialog
from disclaimer_widget import Ui_Disclaimer
from queries import query_processor
from FILE_handling import file_handling

class Disclaimer_window(QDialog):
    def __init__(self, fileID, parent):
        super().__init__(parent)
        self.ui = Ui_Disclaimer()
        self.fileID = fileID
        self.accountID = parent.accountID
        self.key = parent.key
        self.query = query_processor()
        self.file_handle = file_handling(self.accountID,  self.key)
        self.ui.setupUi(self)
        self.signal_connect()

    def signal_connect(self):
        self.ui.proceed_button.clicked.connect(self.proceed_button_clicked)
        self.ui.cancel_button.clicked.connect(self.cancel_button_clicked)

    def proceed_button_clicked(self):
        hashed_name = self.query.get_hashed_name(self.accountID, fileID=self.fileID)
        self.query.delete_file(self.fileID)
        self.file_handle.delete_encrypted_file(self.accountID, hashed_name)
        self.parent().file_manager.show_files()
        self.parent().show_table()
        self.close()

    def cancel_button_clicked(self):
        self.close()
