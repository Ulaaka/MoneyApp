import sys, shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QPushButton, QSizePolicy, QLabel, QDateEdit, QVBoxLayout
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QPieSeries, QLineSeries, QValueAxis
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

        self.func_mapping = {
            "Summary" : self.create_summary_graph,
            "Weekly Trend" : self.create_weekly_graph,
            "Monthly Trend" : self.create_monthly_graph,
            "Yearly Trend" : self.create_yearly_graph,
            "Distribution" : self.create_distribution_graph
        }

        self.transfer_toggle_dic = {
            "Income" : True,
            "Expense": False,
            "All": None
        }

        self.max_toggle_dic = {
            False: {
                "Highest" : False,
                "Lowest" : True
            },
            True: {
                "Highest" : True,
                "Lowest" : False
            }
        }
        self.stats_signals_connect()
        self.show_graph(self.graph_name)

    def stats_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.dateEdit_2.setCalendarPopup(True)
        parent_window.ui.dateEdit.setCalendarPopup(True)
        parent_window.ui.transaction_type_box.currentTextChanged.connect(self.update_graph)
        parent_window.ui.value_box.currentTextChanged.connect(self.update_graph)
        parent_window.ui.dateEdit.dateChanged.connect(self.update_graph)
        parent_window.ui.dateEdit_2.dateChanged.connect(self.update_graph)
        parent_window.ui.download_chart_button.clicked.connect(self.download_graph)
        if parent_window.ui.charts_widget.layout() is None:
            layout = QVBoxLayout()
            parent_window.ui.charts_widget.setLayout(layout)

    def show_graph(self, graph):
        parent_window = self._parent
        self.graph_name = graph
        state = True if graph == "Summary" else False
        # only active for Summary graph
        parent_window.ui.value_box.setEnabled(state)
        self.update_graph()

    def delete_prev_graph(self):
        if self.set_graph_view is not None:
            self.set_graph_view.deleteLater()
            self.set_graph_view = None

    def update_graph(self):
        parent_window = self._parent
        self.delete_prev_graph()

        if self.graph_name in self.func_mapping:
            graph_func = self.func_mapping[self.graph_name]()
        else:
            return

        # create display widget
        self.set_graph_view = QChartView(graph_func)
        self.set_graph_view.setRenderHint(QPainter.Antialiasing)
        self.set_graph_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        parent_window.ui.charts_widget.layout().addWidget(self.set_graph_view)

    def get_date(self):
        parent_window = self._parent
        date_low_str = parent_window.ui.dateEdit.date().toPyDate().strftime("%Y-%m-%d")
        date_up_str = parent_window.ui.dateEdit_2.date().toPyDate().strftime("%Y-%m-%d")
        return date_low_str, date_up_str


    def get_combo_text(self):
        parent_window = self._parent
        transaction_type_text = parent_window.ui.transaction_type_box.currentText()
        mode_text = parent_window.ui.value_box.currentText()
        return transaction_type_text, mode_text


    def download_graph(self):
        pass

    def create_summary_graph(self):
        parent_window = self._parent

        transaction_type_txt, value_txt = self.get_combo_text()
        result= self.get_date()

        graph = QChart()
        graph.legend().hide()
        graph_series = QBarSeries()
        if transaction_type_txt == "All":
            try:
                in_max_toggle = self.max_toggle_dic[True][value_txt]
                out_max_toggle = self.max_toggle_dic[False][value_txt]
            except:
                in_max_toggle = None
                out_max_toggle = None

            income = self.query.total_transfer_or_extreme_value(parent_window.userID, accountID=parent_window.accountID, transfer_toggle=True, max_toggle=in_max_toggle, date_lower=result[0], date_upper=result[1])
            expense = self.query.total_transfer_or_extreme_value( parent_window.userID, accountID=parent_window.accountID, transfer_toggle=False, max_toggle=out_max_toggle, date_lower=result[0], date_upper=result[1])

            int_bar = QBarSet("Income")
            out_bar = QBarSet("Expense")
            int_bar.append(int(income))
            out_bar.append(int(expense))

            graph_series.append(int_bar)
            graph_series.append(out_bar)

            graph.setTitle("Income vs Expense")
        else:
            transfer_toggle = self.transfer_toggle_dic[transaction_type_txt]
            max_toggle = self.max_toggle_dic[transfer_toggle]
            going = self.query.total_transfer_or_extreme_value(parent_window.userID, accountID=parent_window.accountID, transfer_toggle=transfer_toggle, max_toggle=max_toggle, date_lower=result[0], date_upper=result[1])

            name = "Income" if transfer_toggle is True else "Expense"
            going_bar = QBarSet(name)
            going_bar.append(float(going))
            graph_series.append(going_bar)
            graph.setTitle(name)

        return graph

    def create_weekly_graph(self):
        pass

    def create_monthly_graph(self):
        pass

    def create_yearly_graph(self):
        pass

    def create_distribution_graph(self):
        pass