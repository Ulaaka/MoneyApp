from PyQt5.QtWidgets import QPushButton, QComboBox
from PyQt5.QtCore import Qt, QDate, QSortFilterProxyModel
from queries import query_processor
from Widgets.Table_View import ListModel
from system_functions import system_functions
from Widgets.thread_worker import Thread_worker
class Home_page():
    def __init__(self, parent):
        self._parent = parent
        self.transactions = None

    def show_table(self):
            parent_window = self._parent
            query = query_processor()
            if not parent_window.accountID:
                return

            self.transactions = query.get_transactions(parent_window.accountID)
            if len(self.transactions) == 0:
                self.set_table(False)
                parent_window.ui.no_account_label.setText(f"No transaction found for '{parent_window.account_name}'")
            else:
                self.set_table(True)

                min_date, max_date = self.set_select_dates()

                if min_date is not None and max_date is not None:
                    parent_window.start_date = min_date
                    parent_window.end_date = max_date


                if (parent_window.start_date < min_date and parent_window.end_date > max_date):
                    return
                else:
                    self.filter_transaction = self.transactions[self.transactions.iloc[:, 3].dt.date.between(parent_window.start_date, parent_window.end_date)]

                # -- TABLE LOADING -- 
                self.model = ListModel(self.filter_transaction, parent_window, self)
                self.data = self.filter_transaction

                # Set the search filter for the table
                # inspired from:  https://www.youtube.com/watch?v=53bZSTSLUqI

                proxy_model = QSortFilterProxyModel()
                proxy_model.setSourceModel(self.model)
                proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
                proxy_model.setFilterKeyColumn(5)
                parent_window.ui.search_transaction_line.textChanged.connect(lambda text: self.filtered_search(text, proxy_model))
                parent_window.ui.tableView.setModel(proxy_model)

                self.load_buttons(proxy_model)

                # Hides the ID columns of dataframe
                hidden_columns = [0, 1, 2]
                for i in hidden_columns:
                    parent_window.ui.tableView.setColumnHidden(i, True)

    def filtered_search(self, text, proxy):
        proxy.setFilterRegExp(text)
        self.load_buttons(proxy)

    def load_buttons(self, proxy):
        parent_window = self._parent
        for row_index in range(proxy.rowCount()):
            index_button = proxy.index(row_index, proxy.columnCount() - 1)
            source_index = proxy.mapToSource(index_button)
            source_model = proxy.sourceModel()
            transaction_id = source_model._data.iloc[source_index.row(), 0]
            remove_button = QPushButton("Remove")
            remove_button.setObjectName("item_button")
            parent_window.ui.tableView.setIndexWidget(index_button, remove_button)
            remove_button.clicked.connect(
                lambda checked, id=transaction_id: self.handle_remove_button(id))

    def set_select_dates(self):
        parent_window = self._parent
        if self.transactions is None:
            return
        self.transactions = self.transactions.sort_values(by=self.transactions.columns[3], ascending=False)
        date_list = self.transactions.iloc[:, 3].tolist()

        if len(date_list) == 0:
            min_date = None
            max_date = None
            return

        min_date = min(date_list).date()
        max_date = max(date_list).date()

        parent_window.ui.start_date_edit.setDate(QDate(min_date.year, min_date.month, min_date.day))
        parent_window.ui.end_date_edit.setDate(QDate(max_date.year, max_date.month, max_date.day))
        return min_date, max_date

    def handle_remove_button(self, id):
        query = query_processor()
        query.delete_transaction(int(id))
        self.show_table()

    def download_table(self):
        parent_window = self._parent
        download_type = parent_window.ui.download_df_combo.currentText()
        system = system_functions()
        if ("CSV" in download_type):
            self.worker = Thread_worker(lambda: system.create_csv(parent_window.account_name, self.filter_transaction))
            self.worker.start()

        elif ("PDF" in download_type):
            self.worker = Thread_worker(lambda: system.create_pdf(parent_window.account_name, self.filter_transaction))
            self.worker.start()


    def get_filter_date(self, start=None):
        parent_window =self._parent
        if start is True:
            value = parent_window.ui.start_date_edit.date()
            parent_window.start_date  = value.toPyDate()
        elif start is False:
            value = parent_window.ui.end_date_edit.date()
            parent_window.end_date  = value.toPyDate()
        self.show_table()

    def set_table(self, flag):
        parent_window = self._parent
        if flag:
            parent_window.ui.home_stacked.setCurrentWidget(parent_window.ui.table_page)
        else:
            parent_window.ui.home_stacked.setCurrentWidget(parent_window.ui.no_account_page)