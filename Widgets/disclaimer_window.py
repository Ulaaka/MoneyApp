from PyQt5.QtWidgets import QDialog

from Widgets.disclaimer_generated import Ui_Disclaimer
from Widgets.home_page import HomePage
from db_queries import QueryProcessor
from file_handle import FileHandling

class DisclaimerWindow(QDialog):
    def __init__(self, fileID, parent):
        super().__init__(parent)
        self.ui = Ui_Disclaimer()
        self.fileID = fileID
        self.userID = parent.userID
        self.accountID = parent.accountID
        self.key = parent.key
        self.query = QueryProcessor()
        self.file_handle = FileHandling(self.userID, self.accountID,  self.key)
        self.home_page_handle = HomePage(parent)
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
        self.home_page_handle.show_table()
        self.close()

    def cancel_button_clicked(self):
        self.close()
