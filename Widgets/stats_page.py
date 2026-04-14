import sys, shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate
from Widgets.live_output_window import Live_output_window
from FILE_handling import file_handling
from Widgets.stream import Stream
from Widgets.thread_worker import Thread_worker
from decouple import config
from queries import query_processor
from Widgets.home_page import Home_page
from datetime import date
from queries import query_processor
class Stats_page():
    def __init__(self, parent):
        self._parent = parent

        self.active_buttons = []
        self.query = query_processor()
        self.userID = parent.userID
        self.accountID = parent.accountID
        self.account_name = parent.account_name
        self.set_chart_view = None
        self.set_chart = "Summary"
        self.graph_buttons = []

        self.show_chart(self.set_chart)
        self.stats_signals_connect()

    def stats_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.dateEdit_2.setCalendarPopup(True)
        parent_window.ui.dateEdit.setCalendarPopup(True)
        parent_window.transaction_type_box.currentTextChanged.connect(self.update_graph)
        parent_window.value_box.currentTextChanged.connect(self.update_graph)
        parent_window.dateEdit.dateChanged.connect(self.update_graph)
        parent_window.dateEdit_2.dateChanged.connect(self.update_graph)
        parent_window.download_chart_button.clicked.connect(self.download_graph)

    def show_chart(self):
        pass

    def update_graph(self):
        pass

    def download_graph(self):
        pass