import sys,  shutil, pycountry, os
from decouple import config
from PyQt5.QtWidgets import QMainWindow, QApplication, QCompleter, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5 import QtCore, QtWidgets
from financial_app import Ui_MainWindow
from account_selection_panel import account_selection_form
from account_add_page import account_add_page_form
from queries import query_processor
from Table_View import ListModel
from FILE_handling import file_handling
from live_output_widget import live_output_page
from BASE_Classes import cryptography

class Live_output_window(QtWidgets.QDialog):
    def __init__(self, parent, saved_print):
        super().__init__(parent)
        self.key = parent.key
        self.accountID = parent.accountID
        self.saved_print = saved_print

        self.ui = live_output_page()
        self.crypto = cryptography()
        self.file_handle = file_handling(self.accountID, self.key)

        self.ui.setupUi(self)
        self.live_output_signals_connection()

    def live_output_signals_connection(self):
        self.setObjectName('live_output_window')
        self.ui.textBrowser.setObjectName('live_output')
        self.ui.textBrowser.setOpenLinks(False)
        self.ui.textBrowser.textChanged.connect(self.adjust_text_edit)
        self.ui.textBrowser.anchorClicked.connect(self.link_click)

    def adjust_text_edit(self):
        text = self.ui.textBrowser.document()
        text.adjustSize()
        self.ui.textBrowser.setMinimumHeight(int(text.size().height()))

    # Action when the link in the text is clicked
    def link_click(self, event):
        flag = False
        pressed_file_name = event.toString()
        sub_save_folder = os.path.join(config('SAVE_FOLDER'),f"account_{self.accountID}")
        decrypted_text = self.crypto.decrypt(sub_save_folder, self.key, self.accountID,filename=pressed_file_name.split(":")[1])
        if (pressed_file_name.split(".")[1] == "pdf"):
            flag = True
        temp_name = self.file_handle.show_decrypted_pdf(decrypted_text, pdf_flag=flag)
        self.file_handle.temp_files.append(temp_name)
        self.file_handle.open_temp_file(temp_name)

    # when the file window close
    def closeEvent(self, event):
        for file in self.file_handle.temp_files:
            self.file_handle.delete_temp_file(file)
        event.accept()
        sys.stdout = self.saved_print

# custom class for capturing print outputs
class Stream(QtCore.QObject):
    input_text = QtCore.pyqtSignal(str)

    def write(self, text):
        self.input_text.emit(text)

    def flush(self):
        sys.stdout.flush()

class Account_selection_page(QtWidgets.QDialog):
    chose_account = pyqtSignal(str, int) 
    def __init__(self, parent):
        super().__init__(parent)

        self.userID = parent.userID

        self.ui = account_selection_form()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.Popup)

        self.completer = QCompleter(self.ui.accounts_list.model(), self)
        self.completer.setFilterMode(Qt.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)

        self.ui.lineEdit.setCompleter(self.completer)

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
        self.userID = parent.userID
        self.currencies = currencies
        self.ui = account_add_page_form()

        self.ui.setupUi(self)
        self.account_add_signals_connection()

    def account_add_signals_connection(self):
        self.ui.account_currency_combo.addItems(self.currencies)
        self.ui.submit_button.clicked.connect(self.add_account_database)
        self.ui.account_name_type.setObjectName("input_field")
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
        accountID = query.insert_account(self.userID, account_name, account_type, account_currency)
        self.parent().parent().update_account(account_name, accountID)
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, controller , key, userID):
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key
        self.userID = userID
        self.account_name = None
        self.accountID = None
        self.status_panel = False

        self.ui = Ui_MainWindow()

        self.ui.setupUi(self)
        self.MainWindow_signals_connection()
        self.manage_home_page()
        self.accounts_selection_show()

    def label_click(self,event):
        pass

    def manage_home_page(self):
        query = query_processor()
        options = query.compute_account_options(self.userID)
        if options is None:
            self.set_table(False)
            self.ui.no_account_label.setText(f"No Account found")
            self.ui.account_name_label.setText("Not selected")
        else:
            if self.account_name is None:
                accountID = query.get_accountID(options[0], self.userID)
                self.update_account(options[0], accountID)
            else:
                self.show_table()

    def show_table(self):
        query = query_processor()
        if not self.accountID:
            return

        transactions = query.get_transactions(self.accountID)
        if transactions.empty:
            self.set_table(False)
            self.ui.no_account_label.setText(f"No transaction found for '{self.account_name}'")
        else:
            print("transactions found!!!!!")
            self.set_table(True)
            self.model = ListModel(transactions, self)
            self.ui.tableView.setModel(self.model)

            hidden_columns = [0, 1, 2]
            for i in hidden_columns:
                self.ui.tableView.setColumnHidden(i, True)

    def update_account(self, new_account_name, new_accountID):
        self.account_name = new_account_name
        self.accountID = new_accountID
        self.ui.account_name_label.setText(new_account_name)
        self.show_table()

    def set_table(self, flag):
        if flag:
            self.ui.home_stacked.setCurrentWidget(self.ui.table_page)
        else:
            self.ui.home_stacked.setCurrentWidget(self.ui.no_account_page)

    def upload_file(self):
        if (not self.accountID):
            QMessageBox.warning(self, 'Error', 'Please create an account first')
            return

        file_paths, _ = QFileDialog.getOpenFileNames(self, 'Open File', "", "CSV Files (*.csv);;PDF Files (*.pdf)")
        if file_paths:
            for file_path in file_paths:
                # config('FOLDER_PATH')
                shutil.copy(file_path, "/Users/nyamdorjbat-erdene/Final_year/exp_folder")

        saved_stdout = sys.stdout 
        self.print_output = Stream()
        self.live_output = Live_output_window(self, saved_stdout)
        self.print_output.input_text.connect(self.get_output)
        sys.stdout = self.print_output

        # process the files
        files_process = file_handling(self.accountID, self.key)
        files_process.process_files_in_folder()
        self.live_output.ui.textBrowser.adjustSize()
        self.live_output.adjustSize()
        self.live_output.show()

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

    def get_output(self, text):
        stripped_list = [line for line in text.splitlines() if line.strip() != ""]
        lines = "\n".join(stripped_list)
        self.live_output.ui.textBrowser.append(lines)

    def MainWindow_signals_connection(self):
        # interface connections
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

        self.ui.no_account_label.setObjectName("no_account_label")
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.ui.account_name_label.setObjectName("account_name_label")
        self.ui.account_name_label.mousePressEvent = self.label_click

        self.ui.full_menu_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)

    def home_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)
        self.show_table()

    def upload_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.upload_page)
        self.ui.upload_stack.setCurrentWidget(self.ui.page)

    def file_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.files_page)

    def stats_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.stats_page)

    def profile_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)

    def settings_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)

    def update_parent(self, option, accountID):
        self.account_name = option
        self.accountID = accountID
        self.ui.account_name_label.setText(option)
        self.show_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('style.qss', 'r') as styling:
        style = styling.read()

    app.setStyleSheet(style)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
