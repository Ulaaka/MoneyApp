from PyQt5.QtWidgets import QPushButton, QSizePolicy
from PyQt5.QtCore import QDate, Qt, QMargins
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QHorizontalBarSeries
from queries import query_processor

class Stats_page():
    def __init__(self, parent):
        self._parent = parent

        self.active_buttons = []
        self.query = query_processor()
        self.set_graph_view = None
        self.graph_name = "Summary"
        self.copy_list = []

        self.func_mapping = {
            "Summary" : self.create_summary_graph,
            "Weekly Trend" : self.create_weekly_graph,
            "Monthly Trend" : self.create_monthly_graph,
            "Yearly Trend" : self.create_yearly_graph,
            "Distribution" : self.create_distribution_graph,
            "Possible Subscriptions": self.create_subscription_graph
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
        parent_window.ui.dateEdit.setDate(QDate(parent_window.start_date.year, parent_window.start_date.month, parent_window.start_date.day))
        parent_window.ui.dateEdit_2.setDate(QDate(parent_window.end_date.year, parent_window.end_date.month, parent_window.end_date.day))
        parent_window.ui.scrollAreaWidgetContents.setStyleSheet("background-color: #fff;")

        parent_window.ui.dateEdit_2.setCalendarPopup(True)
        parent_window.ui.dateEdit.setCalendarPopup(True)

        parent_window.ui.transaction_type_box.currentTextChanged.connect(self.update_graph)
        parent_window.ui.value_box.currentTextChanged.connect(self.update_graph)
        parent_window.ui.dateEdit.dateChanged.connect(self.update_graph)
        parent_window.ui.dateEdit_2.dateChanged.connect(self.update_graph)
        parent_window.ui.download_chart_button.clicked.connect(self.download_graph)

        self.wipe_out_layout(parent_window.ui.scrollAreaWidgetContents.layout())

        for graph in list(self.func_mapping.keys()):
            opt_button = QPushButton(graph)
            opt_button.setStyleSheet("background-color: #313a46;")
            opt_button.setObjectName("email_change_button")
            opt_button.setFixedHeight(30)
            opt_button.clicked.connect(lambda clicked, graph_name=graph: self.show_graph(graph_name))
            parent_window.ui.scrollAreaWidgetContents.layout().addWidget(opt_button)
        parent_window.ui.scrollAreaWidgetContents.layout().addStretch()

    def show_graph(self, graph):
        parent_window = self._parent
        self.graph_name = graph

        if graph != "Summary":
            parent_window.ui.value_box.setEnabled(False)
            parent_window.ui.value_box.setCurrentIndex(0)
            parent_window.ui.value_box.setStyleSheet("background-color: rgba(86, 101, 115, 0.1);")
        else:
            parent_window.ui.value_box.setEnabled(True)
            parent_window.ui.value_box.setStyleSheet("background-color: transparent")
        self.update_graph()

    #Source - https://stackoverflow.com/a/70248114
    def wipe_out_layout(self, layout):
        for i in reversed(range(layout.count())):
            if layout.itemAt(i).widget():
                layout.itemAt(i).widget().setParent(None)
            else:
                layout.removeItem(layout.itemAt(i))

    def update_graph(self):
        parent_window = self._parent
        self.wipe_out_layout(parent_window.ui.charts_widget.layout())
        #self.set_graph_view = None

        if self.graph_name in self.func_mapping:
            graph_func = self.func_mapping[self.graph_name]()
        else:
            return

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

    def create_subscription_graph(self):
        parent_window = self._parent
        result = self.query.find_subscriptions(parent_window.userID)

        graph = QChart()
        graph_series = QHorizontalBarSeries()
        graph_series.setBarWidth(1)
        for sub in result:
            sub_bar = QBarSet(sub[0])
            sub_bar.append(int(sub[1]))
            graph_series.append(sub_bar)
        graph.addSeries(graph_series)

        y_axis = QBarCategoryAxis()
        y_axis.append([sub[0] for sub in result])
        graph.addAxis(y_axis, Qt.AlignLeft)
        graph_series.attachAxis(y_axis)

        x_axis = QValueAxis()
        x_axis.setRange(0, max([int(sub[1]) for sub in result]))
        x_axis.setLabelFormat("%f")
        x_axis.setTickCount(6)
        graph.addAxis(x_axis, Qt.AlignBottom)
        graph_series.attachAxis(x_axis)
        graph.setTitle("Possible subscriptions")

        return graph

    def create_summary_graph(self):
        parent_window = self._parent

        transaction_type_txt, value_txt = self.get_combo_text()
        result= self.get_date()

        graph = QChart()
        if transaction_type_txt == "All":
            bar_names = ["Income", "Expense"]
            try:
                in_max_toggle = self.max_toggle_dic[True][value_txt]
                out_max_toggle = self.max_toggle_dic[False][value_txt]
            except:
                in_max_toggle = None
                out_max_toggle = None
            income = self.query.total_transfer_or_extreme_value(parent_window.userID, accountID=parent_window.accountID , transfer_toggle=True, max_toggle=in_max_toggle, date_lower=result[0], date_upper=result[1])
            expense = self.query.total_transfer_or_extreme_value( parent_window.userID, accountID=parent_window.accountID , transfer_toggle=False, max_toggle=out_max_toggle, date_lower=result[0], date_upper=result[1])
            graph_series = QBarSeries()

            int_bar = QBarSet(bar_names[0])
            out_bar = QBarSet(bar_names[1])

            int_bar.append(int(income))
            out_bar.append(int(expense))

            graph_series.append(int_bar)
            graph_series.append(out_bar)

            graph.addSeries(graph_series)

            x_axis = self.add_to_x_axis(bar_names, graph)
            graph_series.attachAxis(x_axis)

            y_axis = self.add_to_y_axis(max(int(income), int(expense)), graph)
            graph_series.attachAxis(y_axis)

            graph.setTitle("Income vs Expense")

        else:
            max_toggle = None
            transfer_toggle = self.transfer_toggle_dic[transaction_type_txt]
            if transfer_toggle is not None and value_txt != "Total":
                max_toggle = self.max_toggle_dic[transfer_toggle][value_txt]

            going = self.query.total_transfer_or_extreme_value(parent_window.userID, accountID=parent_window.accountID, transfer_toggle=transfer_toggle, max_toggle=max_toggle, date_lower=result[0], date_upper=result[1])
            name = "Income" if transfer_toggle is True else "Expense"

            graph_series = QBarSeries()
            going_bar = QBarSet(name)
            going_bar.append(int(going))
            graph_series.append(going_bar)

            graph.addSeries(graph_series)

            x_axis = self.add_to_x_axis(name, graph)
            y_axis = self.add_to_y_axis(going, graph)

            graph_series.attachAxis(x_axis)
            graph_series.attachAxis(y_axis)

            graph.setTitle(name)
        return graph

    def add_to_y_axis(self, value, graph, tick=5, horizontal=None):
        y_axis = QValueAxis() 
        y_axis.setRange(0, value)
        y_axis.setLabelFormat("%d")
        y_axis.setTickCount(tick)
        graph.addAxis(y_axis, Qt.AlignLeft)
        return y_axis

    def add_to_x_axis(self, value, graph):
        x_axis = QBarCategoryAxis()
        x_axis.append(value)
        graph.addAxis(x_axis, Qt.AlignBottom)
        return x_axis
        
    def create_weekly_graph(self):
        pass

    def create_monthly_graph(self):
        pass

    def create_yearly_graph(self):
        pass

    def create_distribution_graph(self):
        pass