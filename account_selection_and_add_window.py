from PyQt5.QtWidgets import QDialog, QCompleter, QMessageBox
from PyQt5.QtCore import Qt,pyqtSignal, QPoint
from account_selection_panel import account_selection_form
from account_add_page import account_add_page_form
from queries import query_processor


class Account_selection_page(QDialog):
    chose_account = pyqtSignal(str, int) 
    def __init__(self, parent):
        super().__init__(parent)

        self._parent = parent
        self.userID = parent.userID
        self.currency_list = parent.currency_list

        self.ui = account_selection_form()

        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Popup)

        self.set_completer(self.ui.lineEdit, self.ui.accounts_list.model())
        self.account_selection_signals_connection()
        self.show_accounts()

    def account_selection_signals_connection(self):
        self.ui.accounts_list.model().rowsInserted.connect(self.update_list)
        self.ui.accounts_list.model().rowsRemoved.connect(self.update_list)
        self.ui.add_accounts_empty.clicked.connect(self.add_accounts)
        self.ui.add_accounts_list.clicked.connect(self.add_accounts)

    def show_accounts(self):
        query = query_processor()
        self.ui.accounts_list.clear()
        self.account_options = query.compute_account_options(self.userID)
        if self.account_options:
            self.ui.accounts_list.addItems(self.account_options)
            self.ui.accounts_list.currentTextChanged.connect(self.set_account)
        self.update_list()

    def set_account(self, option):
        query = query_processor()
        accountID = query.get_accountID(option, self.userID)
        self.chose_account.emit(option, accountID)

    def set_completer(self, search, model):

        self.completer = QCompleter(model, search)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        search.setCompleter(self.completer)

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
        self.account_add_page = Account_add_page(self.currency_list, self)
        self.account_add_page.show()

class Account_add_page(QDialog):
    def __init__(self, currencies, parent):
        super().__init__(parent)
        self.userID = parent.userID
        self.currencies = currencies

        self.ui = account_add_page_form()

        self.ui.setupUi(self)
        self.account_add_signals_connection()

    def account_add_signals_connection(self):
        self.ui.account_currency_combo.addItems(self.currencies)
        self.ui.submit_button.clicked.connect(self.add_account_database)
        currency_search = self.ui.account_currency_combo.lineEdit()
        currency_search.setObjectName("input_field")
        currency_search.setPlaceholderText("Search currency...")
        completer = QCompleter(self.ui.account_currency_combo.model(), self)

        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)

    def add_account_database(self):
        query = query_processor()
        account_name = self.ui.account_name_type.text()
        account_type = self.ui.account_type_combo.currentText()
        account_currency = self.ui.account_currency_combo.currentText()[:3]
        if account_name and account_type and account_currency:
            accountID = query.insert_account(self.userID, account_name, account_type, account_currency)
            self.parent().parent().update_account(account_name, accountID)
            self.close()
        else:
            self.close()
            QMessageBox.warning(self.parent().parent(), 'Error', 'Please enter all information')
            return