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
class Upload_page():
    def __init__(self, parent):
        self._parent = parent
        self.set_chart_view = None
        self.chart_name = None
        self.set_filter = None
        self.graphs_buttons = []

        self.dictionary = {
        }