from PyQt5.QtWidgets import QCompleter, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from queries import query_processor
import pandas as pd
from deletion_disclaimer_window import Deletion_disclaimer_window

class Account_control_page(QWidget):
    def __init__(self, current_account, parent):
        super().__init__(parent)
        self.current_account = current_account
        self.userID = parent.userID
        self.accountID = parent.accountID
        self._parent = parent
        self.currencies = parent.currency_list
        self.objective = 0
        self.query = query_processor()
        self.account_control_signals_connect()

    def account_control_signals_connect(self):
        parent_window = self._parent

        parent_window.ui.stackedWidget.setCurrentWidget(parent_window.ui.account_page)
        parent_window.ui.comboBox_2.addItems(self.currencies)
        currency_search = parent_window.ui.comboBox_2.lineEdit()
        completer = QCompleter(parent_window.ui.comboBox_2.model(), self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        currency_search.setCompleter(completer)

        parent_window.ui.change_button.clicked.connect(self.objective_toggler)
        parent_window.ui.delete_account.clicked.connect(self.delete_acc)
        self.show_account_control_page()

    def show_account_control_page(self):
        parent_window = self._parent
        parent_window.ui.lineEdit_2.setText(self.current_account)

        result = self.query.get_type_account_currency(self.current_account, self.userID)
        parent_window.ui.comboBox.setEditable(True)
        parent_window.ui.comboBox.setCurrentText(result[0])
        parent_window.ui.comboBox_2.setCurrentText(result[1])

        result_1 = self.query.get_create_update_account(self.current_account, self.userID)
        if (result_1[1] is None):
            str_result = "Not Updated"
            parent_window.ui.account_update_value.setText(str_result)
        else:
            parent_window.ui.account_update_value.setText(str(result_1[1]))
        parent_window.ui.account_created_value.setText(str(result_1[0]))
        self.activate(False)

    def activate(self, flag):
        parent_window = self._parent
        if flag:
            parent_window.ui.change_button.setText("Save")
        else:
            parent_window.ui.change_button.setText("Edit")
        parent_window.ui.lineEdit_2.setEnabled(flag)
        parent_window.ui.comboBox.setEnabled(flag)
        parent_window.ui.comboBox_2.setEnabled(flag)

    def delete_acc(self):
        disclaimer_window = Deletion_disclaimer_window(self)
        disclaimer_window.show()

    def objective_toggler(self):
        if (self.objective == 1):
            self.get_answer()
        self.objective = 1 - self.objective
        self.manage_change_account()

    def manage_change_account(self):
        if (self.objective == 1):
            flag = True
        else:
            flag = False
        self.activate(flag)

    def get_answer(self):
        parent_window = self._parent
        account_name = parent_window.ui.lineEdit_2.text()
        account_type = parent_window.ui.comboBox.currentText()
        account_currency = parent_window.ui.comboBox_2.currentText()[:3]

        if not account_name:
            QMessageBox.warning(self, 'Error', 'Account Name section cant be empty')
            return

        self.query.update_account(account_name, account_type, account_currency, self.accountID)
        parent_window.update_account(account_name, self.accountID)
        self.current_account = account_name
        self.show_account_control_page()