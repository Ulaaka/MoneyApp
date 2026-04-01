import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QCompleter
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtCore, QtWidgets
from financial_app import Ui_MainWindow
from account_selection_panel import account_selection_form
from account_add_page import account_add_page_form
from queries import query_processor
import pycountry

class Account_selection_page(QtWidgets.QDialog):
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
        self.account_options = self.compute_account_options()

        self.ui.accounts_list.clear()
        if self.account_options:
            self.ui.accounts_list.addItems(self.account_options)
        self.update_list()

    def compute_account_options(self):
        accounts = self.query.return_accounts_given_userID(self.userID)
        options_list = [account[1] for account in accounts] if accounts else []
        return options_list if options_list else None

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

    def remove_accounts(self):
        pass

class Account_add_page(QtWidgets.QDialog):
    def __init__(self, currencies, parent):
        super().__init__(parent)
        self.ui = account_add_page_form()
        self.ui.setupUi(self)
        self.currencies = currencies
        self.userID = parent.userID
        self.query = query_processor()

        self.signals_connect()

        currency_search = self.ui.account_currency_combo.lineEdit()
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
        self.query.insert_account(self.userID, account_name, account_type, account_currency)
        self.parent().show_accounts()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, controller , key, userID):
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key
        self.userID = userID

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.status_panel = False

        self.ui.full_menu_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.buttons_connected()

        self.query = query_processor()

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

    def accounts_selection_show(self):
        if not self.status_panel:

            # https://forum.qt.io/topic/116360/qwidget-maptoglobal-not-giving-right-result/2

            global_pos = self.ui.account_button.mapToGlobal(QPoint(0,0))
            self.panel = Account_selection_page(self)
            self.panel.move(global_pos.x(), global_pos.y() +self.ui.account_button.height() + 20)
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
