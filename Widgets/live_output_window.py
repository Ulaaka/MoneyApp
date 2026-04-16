import sys, os
from decouple import config
from PyQt5.QtWidgets import QDialog, QMessageBox
from FILE_handling import file_handling
from Widgets.live_output_widget import Ui_live_output_window
from BASE_Classes import cryptography
from queries import query_processor
class Live_output_window(QDialog):
    def __init__(self, parent, saved_print):
        super().__init__(parent)
        self._parent = parent
        self.key = parent.key
        self.accountID = parent.accountID
        self.userID = parent.userID
        self.saved_print = saved_print

        self.ui = Ui_live_output_window()
        self.crypto = cryptography()
        self.file_handle = file_handling(self.userID, self.accountID, self.key)
        self.query = query_processor()

        self.ui.setupUi(self)
        self.live_output_signals_connection()

    def live_output_signals_connection(self):
        self.setObjectName('live_output_window')
        self.ui.textBrowser.setOpenLinks(False)
        self.ui.textBrowser.textChanged.connect(self.adjust_text_edit)
        self.ui.textBrowser.anchorClicked.connect(self.link_click)

    def adjust_text_edit(self):
        text = self.ui.textBrowser.document()
        text.adjustSize()
        self.ui.textBrowser.setMinimumHeight(int(text.size().height()))

    # Action when the link in the text is clicked
    def link_click(self, event):
        flag = False
        pressed_file_name = event.toString()
        original_filename = pressed_file_name.split(":")[1]

        result = self.file_handle.view_file(original_filename)
        if not result:
            QMessageBox.warning(self._parent, "Error", "File can not be restored")

    # when the file window close
    def closeEvent(self, event):
        for file in self.file_handle.temp_files:
            self.file_handle.delete_temp_file(file)
        event.accept()
        sys.stdout = self.saved_print
