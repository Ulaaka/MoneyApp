from PyQt5.QtWidgets import QPushButton, QSizePolicy, QWidget, QVBoxLayout, QLabel, QComboBox, QDateEdit, QApplication, QFileDialog
from PyQt5.QtCore import QDate, Qt, QPointF
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QHorizontalBarSeries, QPieSeries, QLineSeries, QCategoryAxis
from queries import query_processor
from datetime import datetime, timedelta, date
from pathlib import Path
import calendar, os
class Stats_page():
    def __init__(self, parent):
        self._parent = parent
        self.active_buttons = []
        self.query = query_processor()
        self.set_graph_view = None
        self.graph_name = "Summary"
        self.account_currency = None
        self.active_filters = {}
        self.current_date = datetime.today().date()
        self.download_folder_path = Path.home() / "Downloads"

        self.widget_layout = parent.ui.filters_widget.layout()
        self.scroll_layout = parent.ui.scrollAreaWidgetContents.layout()

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
        parent_window.ui.scrollAreaWidgetContents.setStyleSheet("background-color: #fff;")
        parent_window.ui.download_chart_button.clicked.connect(self.download_graph)
        if parent_window.accountID:
            self.account_currency = self.query.get_type_account_currency(parent_window.account_name, parent_window.userID)[1].upper()

        self.wipe_out_layout(self.scroll_layout)

        # populate buttons 
        for graph in list(self.func_mapping.keys()):
            opt_button = QPushButton(graph)
            opt_button.setStyleSheet("background-color: #313a46;")
            opt_button.setObjectName("email_change_button")
            opt_button.setFixedHeight(50)
            opt_button.clicked.connect(lambda clicked, graph_name=graph: self.show_graph(graph_name))
            self.scroll_layout.addWidget(opt_button)
        self.scroll_layout.addStretch()

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
            add.currentTextChanged.connect(self.update_graph)
        elif widget_desc["type"] == "dateEdit":
            add = QDateEdit()
            date = widget_desc["value"]
            if date:
                add.setDate(QDate(date.year, date.month, date.day))
            add.setCalendarPopup(True)
            add.setObjectName("stats_date")

            add.dateChanged.connect(self.update_graph)
        vertical.addWidget(add)
        self.active_filters[widget_desc["name"]] = add
        return widget

    def download_graph(self):
        filename = f"{self.graph_name}_{self.current_date}.png"

        self.set_graph_view.repaint()
        QApplication.processEvents() 
        file_path = os.path.join(self.download_folder_path, filename)
        grabbed = self.set_graph_view.grab()
        grabbed.save(file_path)


    def create_subscription_graph(self):
        parent_window = self._parent
        account_text = self.active_filters["Accounts"].currentText()
        if account_text == "All":
            result = self.query.find_subscriptions(parent_window.userID)
        else:
            result = self.query.find_subscriptions(parent_window.userID, account_text)
        graph = QChart()
        graph_series = QHorizontalBarSeries()
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
        if result:
            x_axis.setRange(0, max([int(sub[1]) for sub in result]))
        x_axis.setLabelFormat("%f")
        x_axis.setTickCount(6)
        graph.addAxis(x_axis, Qt.AlignBottom)
        graph_series.attachAxis(x_axis)
        graph.setTitle("Possible subscriptions")
        return graph

    def create_summary_graph(self):
        parent_window = self._parent
        transaction_type_txt = self.active_filters["Transaction Type"].currentText()
        value_txt = self.active_filters["Mode"].currentText()

        date_low_str = self.active_filters["From"].date().toString("yyyy-MM-dd")
        date_up_str = self.active_filters["To"].date().toString("yyyy-MM-dd")

        y_column_name = f"Amount in {self.account_currency}"
        graph = QChart()
        if transaction_type_txt == "All":
            bar_names = ["Income", "Expense"]
            try:
                in_max_toggle = self.max_toggle_dic[True][value_txt]
                out_max_toggle = self.max_toggle_dic[False][value_txt]
            except:
                in_max_toggle = None
                out_max_toggle = None
            income = self.query.total_transfer_or_extreme_value(parent_window.userID, accountID=parent_window.accountID , transfer_toggle=True, max_toggle=in_max_toggle, date_lower=date_low_str, date_upper=date_up_str)
            expense = self.query.total_transfer_or_extreme_value( parent_window.userID, accountID=parent_window.accountID , transfer_toggle=False, max_toggle=out_max_toggle, date_lower=date_low_str, date_upper=date_up_str)
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


            y_axis = self.add_to_y_axis(max(int(income), int(expense)), graph, y_column_name)
            graph_series.attachAxis(y_axis)

            graph.setTitle("Income vs Expense")

        else:
            max_toggle = None
            transfer_toggle = self.transfer_toggle_dic[transaction_type_txt]
            if transfer_toggle is not None and value_txt != "Total":
                max_toggle = self.max_toggle_dic[transfer_toggle][value_txt]

            going = self.query.total_transfer_or_extreme_value(parent_window.userID, accountID=parent_window.accountID, transfer_toggle=transfer_toggle, max_toggle=max_toggle, date_lower=date_low_str, date_upper=date_up_str)
            name = "Income" if transfer_toggle is True else "Expense"

            graph_series = QBarSeries()
            going_bar = QBarSet(name)
            going_bar.append(int(going))
            graph_series.append(going_bar)

            graph.addSeries(graph_series)

            x_axis = self.add_to_x_axis(name, graph)
            y_axis = self.add_to_y_axis(going, graph, y_column_name)


            graph_series.attachAxis(x_axis)
            graph_series.attachAxis(y_axis)

            graph.setTitle(name)
        return graph

    def add_to_y_axis(self, value, graph , title_text=None, horizontal=None):
        y_axis = QValueAxis()
        if title_text:
            y_axis.setTitleText(title_text)
        y_axis.setRange(0, value)
        y_axis.setLabelFormat("%d")
        y_axis.setTickCount(5)
        graph.addAxis(y_axis, Qt.AlignLeft)
        return y_axis

    def add_to_x_axis(self, value, graph):
        x_axis = QBarCategoryAxis()
        x_axis.append(value)
        graph.addAxis(x_axis, Qt.AlignBottom)
        return x_axis

    def create_weekly_graph(self):
        parent_window = self._parent

        transaction_type_txt = self.active_filters["Transaction Type"].currentText()
        value_txt = self.active_filters["Mode"].currentText()
        graph = QChart()
        week_day = self.current_date.weekday()
        if transaction_type_txt == "All":
            try:
                in_max_toggle = self.max_toggle_dic[True][value_txt]
                out_max_toggle = self.max_toggle_dic[False][value_txt]
            except:
                in_max_toggle = None
                out_max_toggle = None
    
            in_result_list = []
            out_result_list = []
            for idx,  i in enumerate(range(week_day + 1)):
                day = self.current_date - timedelta(days=week_day - i)
                date_str = day.strftime("%Y-%m-%d")
                result_in = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=True,
                                                        max_toggle=in_max_toggle, date_lower=date_str, date_upper=date_str)
                result_out = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=False,
                                                        max_toggle=out_max_toggle, date_lower=date_str, date_upper=date_str)
                if result_in is None:
                    result_in = 0

                if result_out is None:
                    result_out = 0

                in_result_list.append((calendar.day_name[day.weekday()], int(result_in), idx))
                out_result_list.append((calendar.day_name[day.weekday()], int(result_out), idx))

                for axis in graph.axes():
                    graph.removeAxis(axis)
                graph.removeAllSeries()

                in_series = QLineSeries()
                in_series.setName("Income")

                out_series = QLineSeries()
                out_series.setName("Expense")

                for i in in_result_list:
                    in_series.append(i[2], i[1])

                for i in out_result_list:
                    out_series.append(i[2], i[1])

                graph.addSeries(in_series)
                graph.addSeries(out_series)

                category_axis = QCategoryAxis()
                for idx, day in enumerate(range(len(in_result_list))):
                    category_axis.append(in_result_list[idx][0], idx)

                axis_y = QValueAxis()
                combined = in_result_list + out_result_list
                axis_y.setRange(0, max([result[1] for result in combined]) * 1.2)

                graph.addAxis(category_axis, Qt.AlignBottom)
                graph.addAxis(axis_y, Qt.AlignLeft)

                in_series.attachAxis(category_axis)
                in_series.attachAxis(axis_y)

                out_series.attachAxis(category_axis)
                out_series.attachAxis(axis_y)
                graph.setTitle("Weekly Trend: Income vs Expense")

        else:

            max_toggle = None
            transfer_toggle = self.transfer_toggle_dic[transaction_type_txt]
            if transfer_toggle is not None and value_txt != "Total":
                max_toggle = self.max_toggle_dic[transfer_toggle][value_txt]

            graph_series = QLineSeries()
            name = "Income" if transfer_toggle is True else "Expense"
            graph_series.setName(name)

            result_list = []
            for idx,  i in enumerate(range(week_day + 1)):
                day = self.current_date - timedelta(days=week_day - i)
                date_str = day.strftime("%Y-%m-%d")
                result = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=transfer_toggle,
                                                        max_toggle=max_toggle, date_lower=date_str, date_upper=date_str)
                if result is None:
                    result = 0
                result_list.append((calendar.day_name[day.weekday()], int(result), idx))

            for i in result_list:
                graph_series.append(i[2], i[1])

            category_axis = QCategoryAxis()
            for idx, day in enumerate(range(len(result_list))):
                category_axis.append(result_list[idx][0], idx)

            axis_y = QValueAxis()
            axis_y.setRange(0, max([result[1] for result in result_list]) * 1.2)
            graph.addSeries(graph_series)
            graph.addAxis(category_axis, Qt.AlignBottom)
            graph.addAxis(axis_y, Qt.AlignLeft)
            graph_series.attachAxis(category_axis)
            graph_series.attachAxis(axis_y)
            graph.setTitle("Weekly Trend")

        return graph

    def create_monthly_graph(self):

        parent_window = self._parent

        transaction_type_txt = self.active_filters["Transaction Type"].currentText()
        value_txt = self.active_filters["Mode"].currentText()

        result = calendar.monthrange(self.current_date.year, self.current_date.month)[1]
        first_day = date(self.current_date.year, self.current_date.month, 1)

        graph = QChart()
        if transaction_type_txt == "All":
            try:
                in_max_toggle = self.max_toggle_dic[True][value_txt]
                out_max_toggle = self.max_toggle_dic[False][value_txt]
            except:
                in_max_toggle = None
                out_max_toggle = None

            in_result_list = []
            out_result_list = []
            for idx,  i in enumerate(range(int(self.current_date.day))):
                day = first_day + timedelta(days=i)
                date_str = day.strftime("%Y-%m-%d")
                result_in = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=True,
                                                        max_toggle=in_max_toggle, date_lower=date_str, date_upper=date_str)
                result_out = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=False,
                                                        max_toggle=out_max_toggle, date_lower=date_str, date_upper=date_str)
                if result_in is None:
                    result_in = 0

                if result_out is None:
                    result_out = 0

                in_result_list.append((idx+1, int(result_in)))
                out_result_list.append((idx+1, int(result_out)))
                for axis in graph.axes():
                    graph.removeAxis(axis)
                graph.removeAllSeries()

                in_series = QLineSeries()
                in_series.setName("Income")

                out_series = QLineSeries()
                out_series.setName("Expense")

                for i in in_result_list:
                    in_series.append(QPointF(float(i[0]), float(i[1])))

                for i in out_result_list:
                    out_series.append(QPointF(float(i[0]), float(i[1])))

                graph.addSeries(in_series)
                graph.addSeries(out_series)

                category_axis = QCategoryAxis()
                axis_y = QValueAxis()
                combined = in_result_list + out_result_list
                axis_y.setRange(0, max([result[1] for result in combined]))

                graph.addAxis(category_axis, Qt.AlignBottom)
                graph.addAxis(axis_y, Qt.AlignLeft)

                in_series.attachAxis(category_axis)
                in_series.attachAxis(axis_y)

                out_series.attachAxis(category_axis)
                out_series.attachAxis(axis_y)
                graph.setTitle("Monthly Trend: Income vs Expense")
        else:
            graph_series = QLineSeries()

            max_toggle = None
            transfer_toggle = self.transfer_toggle_dic[transaction_type_txt]
            if transfer_toggle is not None and value_txt != "Total":
                max_toggle = self.max_toggle_dic[transfer_toggle][value_txt]

            name = "Income" if transfer_toggle is True else "Expense"
            graph_series.setName(name)

            result_list = []
            for idx, i in enumerate(range(int(self.current_date.day))):
                day = first_day + timedelta(days=i)
                date_str = day.strftime("%Y-%m-%d")
                if (day == self.current_date):
                    break
                result = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=transfer_toggle,
                                                max_toggle=max_toggle, date_lower=date_str, date_upper=date_str)
                if result is None:
                    result = 0
                result_list.append((idx+1, int(result)))
            for i in result_list:
                graph_series.append(QPointF(float(i[0]), float(i[1])))

            category_axis = QCategoryAxis()
            axis_y = QValueAxis()

            axis_y.setRange(0, max([result[1] for result in result_list]))
            graph.addSeries(graph_series)
            graph.addAxis(category_axis, Qt.AlignBottom)
            graph.addAxis(axis_y, Qt.AlignLeft)
            graph_series.attachAxis(category_axis)
            graph_series.attachAxis(axis_y)
            graph.setTitle("Monthly Trend")

        return graph

    def create_yearly_graph(self):
        parent_window = self._parent
        months_list = self.get_month_ranges()
        transaction_type_txt = self.active_filters["Transaction Type"].currentText()
        value_txt = self.active_filters["Mode"].currentText()
        graph = QChart()
        if transaction_type_txt == "All":
            try:
                in_max_toggle = self.max_toggle_dic[True][value_txt]
                out_max_toggle = self.max_toggle_dic[False][value_txt]
            except:
                in_max_toggle = None
                out_max_toggle = None

            in_result_list = []
            out_result_list = []

            for idx, month_range in enumerate(months_list):
                result_in = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=True,
                                            max_toggle=in_max_toggle, date_lower=month_range[0], date_upper=month_range[1])
                result_out = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=False,
                                                max_toggle=out_max_toggle, date_lower=month_range[0], date_upper=month_range[1])
                if result_in is None:
                    result_in = 0
                if result_out is None:
                    result_out = 0

                in_result_list.append((calendar.month_name[idx+1], result_in, idx))
                out_result_list.append((calendar.month_name[idx+1], result_out, idx))

                for axis in graph.axes():
                    graph.removeAxis(axis)
                graph.removeAllSeries()

                in_series = QLineSeries()
                in_series.setName("Income")

                out_series = QLineSeries()
                out_series.setName("Expense")

                for i in in_result_list:
                    in_series.append(i[2], i[1])

                for i in out_result_list:
                    out_series.append(i[2], i[1])

                graph.addSeries(in_series)
                graph.addSeries(out_series)

                category_axis = QCategoryAxis()
                for idx, day in enumerate(range(len(in_result_list))):
                    category_axis.append(in_result_list[idx][0], idx)

                axis_y = QValueAxis()
                combined = in_result_list + out_result_list
                axis_y.setRange(0, max([result[1] for result in combined]))

                graph.addAxis(category_axis, Qt.AlignBottom)
                graph.addAxis(axis_y, Qt.AlignLeft)

                in_series.attachAxis(category_axis)
                in_series.attachAxis(axis_y)

                out_series.attachAxis(category_axis)
                out_series.attachAxis(axis_y)
                graph.setTitle("Yearly Trend: Income vs Expense")
        else:
            graph_series = QLineSeries()

            max_toggle = None
            transfer_toggle = self.transfer_toggle_dic[transaction_type_txt]
            if transfer_toggle is not None and value_txt != "Total":
                max_toggle = self.max_toggle_dic[transfer_toggle][value_txt]

            name = "Income" if transfer_toggle is True else "Expense"
            graph_series.setName(name)

            result_list = []
            for idx, month_range in enumerate(months_list):
                result = self.query.total_transfer_or_extreme_value(parent_window.userID, parent_window.accountID, transfer_toggle=transfer_toggle,
                                            max_toggle=max_toggle, date_lower=month_range[0], date_upper=month_range[1])
                if result is None:
                    result = 0
                result_list.append((calendar.month_name[idx+1], result, idx))

            for i in result_list:
                graph_series.append(i[2], i[1])

            graph.addSeries(graph_series)
            category_axis = QCategoryAxis()

            category_axis = QCategoryAxis()
            for idx, month in enumerate(range(len(result_list))):
                category_axis.append(result_list[idx][0], idx)

            axis_y = QValueAxis()
            axis_y.setRange(0, max([result[1] for result in result_list]))
            graph.addSeries(graph_series)
            graph.addAxis(category_axis, Qt.AlignBottom)
            graph.addAxis(axis_y, Qt.AlignLeft)
            graph_series.attachAxis(category_axis)
            graph_series.attachAxis(axis_y)
            graph.setTitle("Yearly Trend")
        return graph

    def create_type_distribution_graph(self):
        account_name = self.active_filters["Accounts"].currentText()
        date_low_str = self.active_filters["From"].date().toString("yyyy-MM-dd")
        date_up_str = self.active_filters["To"].date().toString("yyyy-MM-dd")

        if (account_name != "All"):
            types = self.query.show_by_type(self._parent.userID, date_low_str, date_up_str, account_name)
        else:
             types = self.query.show_by_type(self._parent.userID, date_low_str, date_up_str)
        graph = QChart()
        graph_series = QPieSeries()
        for type in types:
            name = str(type[0])
            value = float(type[1])
            graph_series.append(name, value)
        graph.addSeries(graph_series)
        graph.setTitle("Transaction by Types")
        return graph

    def create_category_distribution_graph(self):
        account_name = self.active_filters["Accounts"].currentText()
        date_low_str = self.active_filters["From"].date().toString("yyyy-MM-dd")
        date_up_str = self.active_filters["To"].date().toString("yyyy-MM-dd")

        if (account_name != "All"):
            types = self.query.show_by_category(self._parent.userID, date_low_str, date_up_str, account_name)
        else:
             types = self.query.show_by_category(self._parent.userID, date_low_str, date_up_str)
        graph = QChart()
        graph_series = QPieSeries()
        for type in types:
            name = str(type[0])
            value = float(type[1])
            graph_series.append(name, value)
        graph.addSeries(graph_series)
        graph.setTitle("Transaction by Categories")
        return graph

    def create_top_income_sources(self):
        parent_window = self._parent
        date_low_str = self.active_filters["From"].date().toString("yyyy-MM-dd")
        date_up_str = self.active_filters["To"].date().toString("yyyy-MM-dd")
        graph = QChart()
        graph_series = QHorizontalBarSeries()
        graph.setTitle("Top Income Sources")
        top_sources = self.query.common_transactions(parent_window.userID, 5, parent_window.accountID,
        transfer_toggle=True, date_lower=date_low_str, date_upper=date_up_str)

        for sub in top_sources:
            sub_bar = QBarSet(sub[0])
            sub_bar.append(int(sub[1]))
            graph_series.append(sub_bar)
        graph.addSeries(graph_series)

        y_axis = QBarCategoryAxis()
        y_axis.append([sub[0] for sub in top_sources])
        graph.addAxis(y_axis, Qt.AlignLeft)
        graph_series.attachAxis(y_axis)

        x_axis = QValueAxis()
        if top_sources:
            x_axis.setRange(0, max([int(sub[1]) for sub in top_sources]))
        x_axis.setLabelFormat("%d")
        x_axis.setTickCount(6)
        graph.addAxis(x_axis, Qt.AlignBottom)
        graph_series.attachAxis(x_axis)
        return graph


    def create_top_expense_sources(self):
        parent_window = self._parent
        date_low_str = self.active_filters["From"].date().toString("yyyy-MM-dd")
        date_up_str = self.active_filters["To"].date().toString("yyyy-MM-dd")
        graph = QChart()
        graph_series = QHorizontalBarSeries()
        graph.setTitle("Top Expense Sources")
        top_sources = self.query.common_transactions(parent_window.userID, 5, parent_window.accountID,
        transfer_toggle=False, date_lower=date_low_str, date_upper=date_up_str)
        for sub in top_sources:
            sub_bar = QBarSet(sub[0])
            sub_bar.append(int(sub[1]))
            graph_series.append(sub_bar)
        graph.addSeries(graph_series)

        y_axis = QBarCategoryAxis()
        y_axis.append([sub[0] for sub in top_sources])
        graph.addAxis(y_axis, Qt.AlignLeft)
        graph_series.attachAxis(y_axis)

        x_axis = QValueAxis()
        if top_sources:
            x_axis.setRange(0, max([int(sub[1]) for sub in top_sources]))
        x_axis.setLabelFormat("%d")
        x_axis.setTickCount(6)
        graph.addAxis(x_axis, Qt.AlignBottom)
        graph_series.attachAxis(x_axis)
        return graph

    def get_month_ranges(self):
        months_list = []
        for month in range(self.current_date.month):
            first_day = date(self.current_date.year, month+1, 1)
            last_day = date(self.current_date.year, month+2, 1) - timedelta(days=1)
            if month == self.current_date.month:
                last_day = self.current_date

            months_list.append((first_day.strftime("%Y-%m-%d"), last_day.strftime("%Y-%m-%d")))
        return months_list