from PyQt5.QtWidgets import QCompleter, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from queries import query_processor
from Widgets.deletion_disclaimer_window import Deletion_disclaimer_window

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
        parent_window.ui.account_currency_change_combo.addItems(self.currencies)
        currency_search = parent_window.ui.account_currency_change_combo.lineEdit()
        completer = QCompleter(parent_window.ui.account_currency_change_combo.model(), self)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        currency_search.setCompleter(completer)

        parent_window.ui.change_button.clicked.connect(self.objective_toggler)
        parent_window.ui.delete_account.clicked.connect(self.delete_acc)

    def show_account_control_page(self):
        parent_window = self._parent
        parent_window.ui.account_name_change_line.setText(self.current_account)
        query = query_processor()
        result = query.get_type_account_currency(self.current_account, self.userID)
        parent_window.ui.account_type_combo.setEditable(True)
        parent_window.ui.account_type_combo.setCurrentText(result[0])
        parent_window.ui.account_currency_change_combo.setCurrentText(result[1])

        result_1 = query.get_create_update_account(self.current_account, self.userID)
        if (result_1[1] is None):
            str_result = "Not Updated"
            parent_window.ui.account_update_value.setText(str_result)
        else:
            parent_window.ui.account_update_value.setText(str(result_1[1]))
        parent_window.ui.account_created_value.setText(str(result_1[0]))
        self.activate(False)

    def activate(self, flag):
        parent_window = self._parent
        parent_window.ui.account_name_change_line.setEnabled(flag)
        parent_window.ui.account_type_combo.setEnabled(flag)
        parent_window.ui.account_currency_change_combo.setEnabled(flag)
        if flag:
            parent_window.ui.change_button.setText("Save")
            self.set_fields_border(activate=True)
        else:
            parent_window.ui.change_button.setText("Edit")
            self.set_fields_border()

    def set_fields_border(self, activate=False):
        parent_window = self._parent
        color = "black"
        if activate:
            color = "#70B9FE"
        parent_window.ui.account_name_change_line.setStyleSheet(f"border: 2px solid {color};")
        parent_window.ui.account_type_combo.setStyleSheet(f"border: 2px solid {color};")
        parent_window.ui.account_currency_change_combo.setStyleSheet(f"border: 2px solid {color}")

    def delete_acc(self):
        disclaimer_window = Deletion_disclaimer_window(self)
        disclaimer_window.show()

    def objective_toggler(self):
        self.objective = 1 - self.objective
        if (self.objective == 0):
            self.get_answer()
        self.manage_change_account()

    def manage_change_account(self):
        if (self.objective == 1):
            flag = True
        else:
            flag = False
        self.activate(flag)

    def get_answer(self):
        parent_window = self._parent
        account_name = parent_window.ui.account_name_change_line.text()
        account_type = parent_window.ui.account_type_combo.currentText()
        account_currency = parent_window.ui.account_currency_change_combo.currentText()[:3]

        if not account_name:
            QMessageBox.warning(self, 'Error', "Account Name section can't be empty")
            return

        # after updating 1st account, needs to catch the changed account
        self.accountID = parent_window.accountID 
        self.query.update_account(self.accountID, account_name, account_type, account_currency)
        parent_window.update_parent(account_name, self.accountID)
        self.current_account = account_name
        self.show_account_control_page()


