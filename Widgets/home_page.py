from PyQt5.QtWidgets import QPushButton, QHeaderView, QFileDialog
from PyQt5.QtCore import Qt, QDate, QSortFilterProxyModel
from queries import query_processor
from Widgets.Table_View import ListModel
from system_functions import system_functions
from Widgets.thread_worker import Thread_worker
from pathlib import Path
from datetime import datetime
import os

class Home_page():
    def __init__(self, parent):
        self._parent = parent
        self.transactions = None
        self.filter_transaction = None
        self.current_time = datetime.now().strftime("%Y-%m-%d")
        self.download_folder_path = Path.home() / "Downloads"
        self.home_signals_connect()

    def home_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.start_date_edit.editingFinished.connect(lambda: self.get_filter_date(start=True))
        parent_window.ui.end_date_edit.editingFinished.connect(lambda: self.get_filter_date(start=False))
        parent_window.ui.download_df_combo.activated.connect(self.download_table)
        parent_window.ui.upload_file_button.clicked.connect(self.set_select_dates)
        parent_window.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        parent_window.ui.tableView.verticalHeader().setVisible(False)
        parent_window.ui.start_date_edit.setCalendarPopup(True)
        parent_window.ui.end_date_edit.setCalendarPopup(True)


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

                if parent_window.start_date is None and parent_window.end_date is  None:
                    parent_window.start_date = min_date
                    parent_window.end_date = max_date

                parent_window.ui.start_date_edit.setDate(QDate(parent_window.start_date.year, parent_window.start_date.month, parent_window.start_date.day))
                parent_window.ui.end_date_edit.setDate(QDate(parent_window.end_date.year, parent_window.end_date.month, parent_window.end_date.day))

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
        return min_date, max_date

    def handle_remove_button(self, id):
        query = query_processor()
        query.delete_transaction(int(id))
        self.show_table()

    def download_table(self):
        if self.filter_transaction is None:
            return
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