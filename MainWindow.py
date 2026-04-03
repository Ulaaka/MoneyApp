import sys,  shutil, pycountry
from decouple import config
from PyQt5.QtWidgets import QMainWindow, QApplication, QCompleter, QFileDialog
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5 import QtCore, QtWidgets
from financial_app import Ui_MainWindow
from account_selection_panel import account_selection_form
from account_add_page import account_add_page_form
from queries import query_processor
from Table_View import ListModel
from FILE_handling import file_handling
class Account_selection_page(QtWidgets.QDialog):
    chose_account = pyqtSignal(str) 
    def __init__(self, parent):
        super().__init__(parent)

        self.userID = parent.userID
        self.query = query_processor()

        self.ui = account_selection_form()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Popup)

        self.completer = QCompleter(self.ui.accounts_list.model(), self)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.ui.lineEdit.setCompleter(self.completer)

        self.signals_connect()
        self.show_accounts()

    def signals_connect(self):
        self.ui.accounts_list.model().rowsInserted.connect(self.update_list)
        self.ui.accounts_list.model().rowsRemoved.connect(self.update_list)
        self.ui.add_accounts_empty.clicked.connect(self.add_accounts)
        self.ui.add_accounts_list.clicked.connect(self.add_accounts)

    def show_accounts(self):
        self.account_options = self.query.compute_account_options(self.userID)
        self.ui.accounts_list.clear()
        if self.account_options:
            self.ui.accounts_list.addItems(self.account_options)
            self.ui.accounts_list.currentTextChanged.connect(self.set_account)
        self.update_list()

    def set_account(self, option):
        self.chose_account.emit(option)

    def update_list(self):

        if (self.ui.accounts_list.count() > 0):
            self.ui.accounts_list.setVisible(True)
            self.ui.add_accounts_list.setVisible(True)
            self.ui.empty_container.setVisible(False)
        else:
            self.ui.accounts_list.setVisible(False)
            self.ui.add_accounts_list.setVisible(False)
            self.ui.empty_container.setVisible(True)
        self.adjustSize()

    def add_accounts(self):
        currency_list = [f"{currency.alpha_3} - {currency.name} " for currency in pycountry.currencies]
        self.account_add_page = Account_add_page(currency_list, self)
        self.account_add_page.show()


class Account_add_page(QtWidgets.QDialog):
    def __init__(self, currencies, parent):
        super().__init__(parent)
        self.ui = account_add_page_form()
        self.ui.setupUi(self)
        self.currencies = currencies
        self.userID = parent.userID
        self.query = query_processor()

        self.signals_connect()
        self.ui.account_name_type.setObjectName("input_field")
        currency_search = self.ui.account_currency_combo.lineEdit()
        currency_search.setObjectName("input_field")
        currency_search.setPlaceholderText("Search currency...")
        completer = QCompleter(self.ui.account_currency_combo.model(), self)

        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

    def signals_connect(self):
        self.ui.account_currency_combo.addItems(self.currencies)
        self.ui.submit_button.clicked.connect(self.add_account_database)

    def add_account_database(self):
        account_name = self.ui.account_name_type.text()
        account_type = self.ui.account_type_combo.currentText()
        account_currency = self.ui.account_currency_combo.currentText()[:3]
        accountID = self.query.insert_account(self.userID, account_name, account_type, account_currency)
        self.parent().show_accounts()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, controller , key, userID):
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key
        self.userID = userID
        self.account_name = None
        self.accountID = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.no_account_label.setObjectName("no_account_label")
        self.status_panel = False

        self.ui.account_name_label.setObjectName('no_account_label')

        self.ui.full_menu_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.buttons_connected()

        self.query = query_processor()
        self.accounts_selection_show()
        self.show_table()

    def show_table(self):
        options = self.query.compute_account_options(self.userID)
        if not options:
            self.set_table(False)
            self.ui.no_account_label.setText(f"No Account found")

        if self.account_name is None:
            self.account_name = options[0]

        accountID = self.query.get_accountID(self.account_name, self.userID)
        transactions = self.query.get_transactions(accountID)
        if transactions.empty:
            self.set_table(False)
            self.ui.no_account_label.setText(f"No transaction found for '{self.account_name}'")
        else:
            self.set_table(True)
            self.model = ListModel(transactions, self)
            self.ui.tableView.setModel(self.model)

            hidden_columns = [0, 1, 2]
            for i in hidden_columns:
                self.ui.tableView.setColumnHidden(i, True)

    def update_table(self):
        self.set_table(True)
        transactions = self.query.get_transactions(self.accountID)
        self.model = ListModel(transactions, self)
        self.ui.tableView.setModel(self.model)

    def set_table(self, flag):
        if flag:
            self.ui.home_stacked.setCurrentWidget(self.ui.table_page)
        else:
            self.ui.home_stacked.setCurrentWidget(self.ui.no_account_page)

    def upload_file(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, 'Open File', "", "CSV Files (*.csv);;PDF Files (*.pdf)")
        if file_paths:
            for file_path in file_paths:
                # config('FOLDER_PATH')
                shutil.copy(file_path, "/Users/nyamdorjbat-erdene/Final_year/exp_folder")
        print(self.accountID)
        files_process = file_handling(self.accountID, self.key)
        # process the files
        files_process.process_files_in_folder()
        self.update_table()


    def buttons_connected(self):
        self.ui.home_button_1.clicked.connect(self.home_page_show)
        self.ui.home_button_2.clicked.connect(self.home_page_show)

        self.ui.upload_button_1.clicked.connect(self.upload_page_show)
        self.ui.upload_button_2.clicked.connect(self.upload_page_show)

        self.ui.file_button_1.clicked.connect(self.file_page_show)
        self.ui.file_button_2.clicked.connect(self.file_page_show)

        self.ui.stats_button_1.clicked.connect(self.stats_page_show)
        self.ui.stats_button_2.clicked.connect(self.stats_page_show)

        self.ui.profile_button_1.clicked.connect(self.profile_page_show)
        self.ui.profile_button_2.clicked.connect(self.profile_page_show)

        self.ui.settings_button_1.clicked.connect(self.settings_page_show)
        self.ui.settings_button_2.clicked.connect(self.settings_page_show)

        self.ui.account_button.clicked.connect(self.accounts_selection_show)

        self.ui.upload_file_button.clicked.connect(self.upload_file)
        self.ui.upload_file_button.setObjectName('upload_file_button')

    def home_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)

    def upload_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.upload_page)

    def file_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.files_page)

    def stats_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.stats_page)

    def profile_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)

    def settings_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)
    
    def update_parent(self, option):
        self.account_name = option
        self.accountID = self.query.get_accountID(option, self.userID)
        self.ui.account_name_label.setText(option)
        self.show_table()

    def accounts_selection_show(self):
        if not self.status_panel:
            # https://forum.qt.io/topic/116360/qwidget-maptoglobal-not-giving-right-result/2
            self.panel = Account_selection_page(self)
            self.panel.chose_account.connect(self.update_parent)

            global_pos = self.ui.account_button.mapToGlobal(QPoint(0,0))
            self.panel.move(global_pos.x(), global_pos.y() +self.ui.account_button.height() + 20)
            self.panel.finished.connect(lambda: setattr(self, 'status_panel', False))

            self.panel.show()
            self.status_panel = True
        else:
            self.panel.close()
            self.status_panel = False

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('style.qss', 'r') as styling:
        style = styling.read()

    app.setStyleSheet(style)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
