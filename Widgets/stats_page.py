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
class Stats_page():
    def __init__(self, parent):
        self._parent = parent
        self.set_chart_view = None

        self.accountID = parent.accountID
        # active chart name
        self.chart_name = None
        # graph to filters
        self.active_filters = None
        # active graph buttons
        self.active_buttons = []
        # dates
        self.upper_date = None
        self.lower_date = None
        self.stats_signals_connect()

    def stats_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.dateEdit_2.setCalendarPopup(True)
        parent_window.ui.dateEdit.setCalendarPopup(True)