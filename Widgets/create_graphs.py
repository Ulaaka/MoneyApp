import calendar
from PyQt5.QtCore import  Qt, QPointF
from PyQt5.QtChart import QChart, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis, QHorizontalBarSeries, QPieSeries, QLineSeries, QCategoryAxis

from graph_db_queries import GraphQueries
from datetime import datetime, timedelta, date
class CreateGraph:
    def __init__(self, parent, active_filters, account_currency):
        self._parent = parent
        self.query = GraphQueries()
        self.account_currency = account_currency
        self.active_filters = active_filters
        self.current_date = datetime.today().date()

        self.transfer_toggle_dic = {
            "Income": True,
            "Expense": False,
            "All": None,
        }

        self.max_toggle_dic = {
            False: {
                "Highest": False,
                "Lowest": True,
            },
            True: {
                "Highest": True,
                "Lowest": False,
            },
        }


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
        x_axis.setLabelFormat("%d")
        x_axis.setTickCount(6)
        graph.addAxis(x_axis, Qt.AlignBottom)
        graph_series.attachAxis(x_axis)
        graph.setTitle("Possible subscriptions")
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