import sys, shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QPushButton, QSizePolicy, QLabel, QDateEdit
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QPieSeries QLineSeries, QValueAxis # type: ignore
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
        self.set_graph_view = None
        self.graph_name = "Summary"
        self.graph_buttons = []

        self.show_graph(self.graph_name)
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

    def show_graph(self, graph):
        parent_window = self._parent
        self.set_graph_view = graph
        state = True if graph == "Summary" else False
        parent_window.ui.value_box.setEnabled(state)
        self.update_graph()

    def delete_prev_graph(self):
        if self.set_graph_view is not None:
            self.set_graph_view.deleteLater()
            self.set_graph_view = None

    def update_graph(self):
        parent_window = self._parent
        self.delete_prev_graph()

        if self.graph_name == "Summary":
            chart = self.create_summary_graph()
        elif self.graph_name == "Weekly Trend":
            chart = self.create_weekly_graph()
        elif self.graph_name == "Monthly Trend":
            chart = self.create_monthly_graph()
        elif self.graph_name == "Yearly Trend":
            chart = self.create_yearly_graph()
        elif self.graph_name == "Distribution":
            chart = self.create_distribution_graph()
        else:
            return

        # create display widget
        self.set_graph_view = QChartView(chart)
        self.set_graph_view.setRenderHint(QPainter.Antialiasing)
        self.set_graph_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # display on charts section
        parent_window.ui.charts_widget.addWidget(self.set_graph_view)

    def download_graph(self):
        pass

    def create_summary_graph(self):
        pass

    def create_weekly_graph(self):
        pass

    def create_monthly_graph(self):
        pass

    def create_yearly_graph(self):
        pass

    def create_distribution_graph(self):
        pass