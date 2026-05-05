from pathlib import Path
import os

from PyQt5.QtWidgets import QPushButton, QSizePolicy, QWidget, QVBoxLayout, QLabel, QComboBox, QDateEdit, QApplication
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChartView
from Widgets.create_graphs import CreateGraph
from db_queries import QueryProcessor
from datetime import datetime
class GraphPage():
    def __init__(self, parent):
        self._parent = parent
        self.active_buttons = []
        self.query = QueryProcessor()
        self.set_graph_view = None
        self.graph_name = "Summary"
        self.account_currency = None
        self.active_filters = {}
        self.current_date = datetime.today().date()
        self.download_folder_path = Path.home() / "Downloads"
        self.widget_layout = parent.ui.filters_widget.layout()
        self.scroll_layout = parent.ui.scrollAreaWidgetContents.layout()
        self.CreateGraph = CreateGraph(parent, self.active_filters, self.account_currency)

        self.button_to_filers_dic = {
            "Summary" : [{
                "name" : "Transaction Type",
                "type" : "comboBox",
                "value": ["All", "Income", "Expense"]
            },
            {
            "name" : "Mode",
            "type" : "comboBox",
            "value": ["Total", "Highest", "Lowest"]
            },
            {
            "name" : "From",
            "type" : "dateEdit",
            "value": self._parent.start_date
            },
            {
            "name" : "To",
            "type" : "dateEdit",
            "value": self._parent.end_date
            }
            ],
            "Trend" : [
            {
            "name" : "Transaction Type",
            "type" : "comboBox",
            "value": ["All", "Income", "Expense"]
            },
            {
            "name" : "Mode",
            "type" : "comboBox",
            "value": ["Total", "Highest", "Lowest"]
            }
            ],
            "Type Distribution" : [
            {
            "name" : "Accounts",
            "type" : "comboBox",
            "value": self.get_accounts_names()
            },
            {
            "name" : "From",
            "type" : "dateEdit",
            "value": self._parent.start_date
            },
            {
            "name" : "To",
            "type" : "dateEdit",
            "value": self._parent.end_date
            }
            ],
            "Category Distribution" : [
            {
            "name" : "Accounts",
            "type" : "comboBox",
            "value": self.get_accounts_names()
            },
            {
            "name" : "From",
            "type" : "dateEdit",
            "value": self._parent.start_date
            },
            {
            "name" : "To",
            "type" : "dateEdit",
            "value": self._parent.end_date
            }
            ],
            "Possible Subscriptions" : [
            {
            "name" : "Accounts",
            "type" : "comboBox",
            "value": self.get_accounts_names()
            }
            ],
            "Top Income Sources":[
            {
            "name" : "From",
            "type" : "dateEdit",
            "value": self._parent.start_date
            },
            {
            "name" : "To",
            "type" : "dateEdit",
            "value": self._parent.end_date
            }
            ],
            "Top Expense Sources":[
            {
            "name" : "From",
            "type" : "dateEdit",
            "value": self._parent.start_date
            },
            {
            "name" : "To",
            "type" : "dateEdit",
            "value": self._parent.end_date
            }
            ]
        }

        self.func_mapping = {
            "Summary" : self.create_summary_graph,
            "Weekly Trend" : self.create_weekly_graph,
            "Monthly Trend" : self.create_monthly_graph,
            "Yearly Trend" : self.create_yearly_graph,
            "Type Distribution" : self.create_type_distribution_graph,
            "Category Distribution": self.create_category_distribution_graph,
            "Possible Subscriptions": self.create_subscription_graph,
            "Top Income Sources": self.create_top_income_sources,
            "Top Expense Sources": self.create_top_expense_sources
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

    def get_accounts_names(self):
        parent_window = self._parent
        account_names = self.query.compute_account_options(parent_window.userID)
        if not account_names:
            return []
        new_list = []
        for account in account_names:
            if account != parent_window.account_name:
                new_list.append(account)
        new_list.insert(0, parent_window.account_name)
        new_list.append("All")
        return new_list

    def stats_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        parent_window.ui.download_chart_button.clicked.connect(self.download_graph)
        if parent_window.accountID:
            self.account_currency = self.query.get_type_account_currency(parent_window.account_name, parent_window.userID)[1].upper()

        self.wipe_out_layout(self.scroll_layout)

        # populate buttons 
        for graph in list(self.func_mapping.keys()):
            opt_button = QPushButton(graph)
            #opt_button.setStyleSheet("background-color: #12355B;")
            opt_button.setObjectName("graphButton")
            opt_button.setFixedHeight(50)
            opt_button.clicked.connect(lambda clicked, graph_name=graph: self.show_graph(graph_name))
            self.scroll_layout.addWidget(opt_button)
        self.scroll_layout.addStretch()
        parent_window.ui.expand_button.setVisible(False)
        parent_window.ui.frame.setVisible(True)
        parent_window.ui.graphs_label.mousePressEvent = self.graph_label_clicked
        parent_window.ui.expand_button.clicked.connect(self.expand_button_clicked)

    def graph_label_clicked(self, event):
        self._parent.ui.frame.setVisible(False)
        self._parent.ui.expand_button.setVisible(True)

    def expand_button_clicked(self):
        self._parent.ui.frame.setVisible(True)
        self._parent.ui.expand_button.setVisible(False)

    def show_graph(self, graph):
        self.graph_name = graph
        self.update_filters(graph)
        self.update_graph()

    #Source - https://stackoverflow.com/a/70248114
    def wipe_out_layout(self, layout):
        for i in reversed(range(layout.count())):
            if layout.itemAt(i).widget():
                layout.itemAt(i).widget().setParent(None)
            else:
                layout.removeItem(layout.itemAt(i))

    def update_filters(self, graph_name):
        self.wipe_out_layout(self.widget_layout)

        if graph_name in ["Weekly Trend", "Monthly Trend", "Yearly Trend"]:
            graph_name = "Trend"

        for widget_desc in self.button_to_filers_dic[graph_name]:
            self.widget_layout.addWidget(self.create_filter(widget_desc))

    def update_graph(self):
        parent_window = self._parent
        chart_layout = parent_window.ui.charts_widget.layout()
        self.wipe_out_layout(chart_layout)
        self.set_graph_view = None

        # create the graph
        if self.graph_name in self.func_mapping:
            graph_func = self.func_mapping[self.graph_name]()
        else:
            return

        self.set_graph_view = QChartView(graph_func)
        self.set_graph_view.setRenderHint(QPainter.Antialiasing)
        self.set_graph_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chart_layout.addWidget(self.set_graph_view)


    def create_filter(self, widget_desc):
        widget = QWidget()
        vertical = QVBoxLayout(widget)
        vertical.addWidget(QLabel(widget_desc["name"]))

        if widget_desc["type"] == "comboBox":
            add = QComboBox()
            account_list = widget_desc["value"]
            add.addItems(account_list)
            add.setObjectName("stats_combo")
            add.setFixedHeight(25)

            add.currentTextChanged.connect(self.update_graph)
        elif widget_desc["type"] == "dateEdit":
            add = QDateEdit()
            date = widget_desc["value"]
            if date:
                add.setDate(QDate(date.year, date.month, date.day))
            add.setCalendarPopup(True)
            add.setFixedHeight(25)
            add.setObjectName("stats_date")

            add.dateChanged.connect(self.update_graph)

        vertical.addWidget(add)
        self.active_filters[widget_desc["name"]] = add
        filter_layout = self._parent.ui.filters_widget.layout()
        filter_layout.setAlignment(add, Qt.AlignTop)
        return widget

    def download_graph(self):
        filename = f"{self._parent.account_name}_{self.graph_name}_{self.current_date}.png"

        self.set_graph_view.repaint()
        QApplication.processEvents() 
        file_path = os.path.join(self.download_folder_path, filename)
        grabbed = self.set_graph_view.grab()
        grabbed.save(file_path)

    def create_summary_graph(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_summary_graph()
        return graph

    def create_weekly_graph(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_weekly_graph()
        return graph

    def create_monthly_graph(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_monthly_graph()
        return graph

    def create_yearly_graph(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_yearly_graph()
        return graph

    def create_type_distribution_graph(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_type_distribution_graph()
        return graph

    def create_category_distribution_graph(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_category_distribution_graph()
        return graph

    def create_subscription_graph(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_subscription_graph()
        return graph

    def create_top_income_sources(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_top_income_sources()
        return graph

    def create_top_expense_sources(self):
        self.CreateGraph.active_filters = self.active_filters
        graph = self.CreateGraph.create_top_expense_sources()
        return graph