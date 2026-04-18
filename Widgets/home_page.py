from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import QPushButton, QHeaderView
from PyQt5.QtCore import Qt, QDate, QSortFilterProxyModel

from db_queries import QueryProcessor
from Widgets.app_table_helper import TransactionTable
from system_functions import SystemHelpers
from Widgets.thread_worker import ThreadWorker

class HomePage():
    def __init__(self, parent):
        self._parent = parent
        self.transactions = None
        self.filter_transaction = None
        self.current_day = datetime.today().date()
        self.current_time = datetime.now().strftime("%Y-%m-%d")
        self.download_folder_path = Path.home() / "Downloads"
        self.system = SystemHelpers()
        self.proxy_model = QSortFilterProxyModel()
        self.home_signals_connect()

    def home_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.start_date_edit.editingFinished.connect(lambda: self.get_filter_date(start=True))
        parent_window.ui.end_date_edit.editingFinished.connect(lambda: self.get_filter_date(start=False))
        parent_window.ui.download_df_combo.activated.connect(self.download_table)
        parent_window.ui.upload_file_button.clicked.connect(lambda clicked, transaction=self.transactions: self.system.set_select_dates(transaction))
        parent_window.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        parent_window.ui.tableView.verticalHeader().setVisible(False)
        parent_window.ui.start_date_edit.setCalendarPopup(True)
        parent_window.ui.end_date_edit.setCalendarPopup(True)

    def show_table(self):
            query = QueryProcessor()
            parent_window = self._parent
            if not parent_window.accountID:
                return

            self.transactions = query.get_transactions(parent_window.accountID)
            if len(self.transactions) == 0:
                self.set_table(False)
                parent_window.ui.no_account_label.setText(f"No transaction found for '{parent_window.account_name}'")
            else:
                self.set_table(True)

                min_date, _, transactions = self.system.set_select_dates(self.transactions)
                self.transactions = transactions

                parent_window.start_date = min_date
                parent_window.end_date = self.current_day

                parent_window.ui.start_date_edit.setDate(QDate(min_date.year, min_date.month, min_date.day))
                parent_window.ui.end_date_edit.setDate(QDate(self.current_day.year, self.current_day.month, self.current_day.day))

                self.initalise(min_date, self.current_day)

    def initalise(self, start_date, end_date):
        parent_window = self._parent
        if self.transactions is None:
            return
        self.filter_transaction = self.transactions[self.transactions.iloc[:, 3].dt.date.between(start_date, end_date)]

        # -- TABLE LOADING -- 
        self.model = TransactionTable(self.filter_transaction, parent_window, self)
        self.data = self.filter_transaction

        # Set the search filter for the table
        # inspired from:  https://www.youtube.com/watch?v=53bZSTSLUqI

        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(5)
        parent_window.ui.search_transaction_line.textChanged.connect(lambda text: self.filtered_search(text, self.proxy_model))
        parent_window.ui.tableView.setModel(self.proxy_model)

        self.load_buttons(self.proxy_model)

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

    def handle_remove_button(self, id):
        query = QueryProcessor()
        query.delete_transaction(int(id))
        self.show_table()

    def download_table(self):
        if self.filter_transaction is None:
            return
        parent_window = self._parent
        download_type = parent_window.ui.download_df_combo.currentText()
        if ("CSV" in download_type):
            self.worker = ThreadWorker(lambda: self.system.create_csv(parent_window.account_name, self.filter_transaction))
            self.worker.start()

        elif ("PDF" in download_type):
            self.worker = ThreadWorker(lambda: self.system.create_pdf(parent_window.account_name, self.filter_transaction))
            self.worker.start()

    def get_filter_date(self, start=None):
        parent_window =self._parent
        if start is True:
            value = parent_window.ui.start_date_edit.date().toPyDate()
            parent_window.start_date  = value
        elif start is False:
            value = parent_window.ui.end_date_edit.date().toPyDate()
            parent_window.end_date  = value
        self.initalise(parent_window.start_date, parent_window.end_date)

    def set_table(self, flag):
        parent_window = self._parent
        if flag:
            parent_window.ui.home_stacked.setCurrentWidget(parent_window.ui.table_page)
        else:
            parent_window.ui.home_stacked.setCurrentWidget(parent_window.ui.no_account_page)