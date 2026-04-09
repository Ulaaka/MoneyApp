import sys,  shutil, pycountry
from decouple import config
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QHeaderView, QPushButton, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from financial_app import Ui_MainWindow
from disclaimer_window import Disclaimer_window
from live_output_window import Live_output_window
from queries import query_processor
from Table_View import ListModel
from FILE_handling import file_handling
from stream import Stream
from account_selection_and_add_window import Account_selection_page
from account_control_page import Account_control_page
from profile_page import Profile_page

class MainWindow(QMainWindow):
    def __init__(self, controller , key, userID):
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key
        self.userID = userID
        self.account_name = None
        self.accountID = None
        self.status_panel = False
        self.currency_list = [f"{currency.alpha_3} - {currency.name} " for currency in pycountry.currencies]

        self.ui = Ui_MainWindow()
        self.file_handle = file_handling(self.accountID, self.key)

        self.ui.setupUi(self)
        self.MainWindow_signals_connection()
        self.manage_home_page()
        self.accounts_selection_show()

    def label_click(self,event):
        current_account = self.ui.account_name_label.text()
        if current_account == "Not selected":
            return
        Account_control_page(current_account, self)

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

    def show_files(self):
        query = query_processor()
        if not self.accountID:
            return
        files = query.get_files(self.accountID)
        if files is None:
            self.set_files(False)
            self.ui.no_file_label.setText(f"No files found for '{self.account_name}'")
        else:
             self.set_files(True)
             tree_model = QStandardItemModel()
             tree_model.setHorizontalHeaderLabels(["Name", "Size", "Kind", "Date Added", "", ""])

             for  tuple in files:
                items = []
                for col_index, col_val in enumerate(tuple[1:]):
                    if (col_index == 1):
                        converted_size_str = self.file_handle.convert_file_size(col_val)
                        item = QStandardItem(converted_size_str)
                        item.setData(int(col_val), Qt.UserRole)
                    elif (col_index == 3):
                        item = QStandardItem(str(col_val))
                        item.setData(str(col_val),  Qt.UserRole)
                    else:
                        item = QStandardItem(col_val)
                        if (col_index == 0):
                             # associated fileID for filename item
                            item.setData(tuple[0], Qt.UserRole)
                        else:
                            item.setData(col_val, Qt.UserRole)
                    items.append(item)
                for item in items:
                    item.setEditable(False)
                tree_model.appendRow(items)
                tree_model.setSortRole(Qt.UserRole)

             self.ui.treeView.setModel(tree_model)

             for row_index, _ in enumerate(files):
                item_button = QPushButton("Remove")
                view_button = QPushButton("View")
                item_button.setObjectName("item_button")
                view_button.setObjectName("view_button")
                self.ui.treeView.setIndexWidget(tree_model.index(row_index, 4), item_button)
                self.ui.treeView.setIndexWidget(tree_model.index(row_index, 5), view_button)
                fileID = tree_model.data(tree_model.index(row_index, 0), Qt.UserRole)
                item_button.clicked.connect(lambda click, id=fileID: self.delete_fileID(id))
                view_button.clicked.connect(lambda clicked, id=fileID: self.view_file_with_ID(id))

    def view_file_with_ID(self, id):
        file_handle = file_handling(self.accountID, self.key)
        file_handle.view_file(fileID=id)

    def delete_fileID(self, fileID):
        print(fileID)
        disclaimer = Disclaimer_window(fileID, self)
        disclaimer.show()

    def show_table(self):
        query = query_processor()
        if not self.accountID:
            return

        transactions = query.get_transactions(self.accountID)
        if len(transactions) == 0:
            self.set_table(False)
            self.ui.no_account_label.setText(f"No transaction found for '{self.account_name}'")
        else:
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

    def set_files(self, flag):
        if flag:
            self.ui.files_stack.setCurrentWidget(self.ui.files_tree_page)
        else:
            self.ui.files_stack.setCurrentWidget(self.ui.no_file_page)

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
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.account_name_label.mousePressEvent = self.label_click

        self.ui.full_menu_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)

        self.ui.treeView.header().setSectionResizeMode(QHeaderView.Stretch)


    def home_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)
        self.show_table()

    def upload_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.upload_page)
        self.ui.upload_stack.setCurrentWidget(self.ui.page)

    def file_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.files_page)
        #self.ui.files_stack.setCurrentWidget(self.ui.files_tree_page)
        self.show_files()

    def stats_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.stats_page)

    def profile_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)
        profile_page = Profile_page(self.account_name, self)
        profile_page.show()

    def settings_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)

    def update_parent(self, option, accountID):
        self.account_name = option
        self.accountID = accountID
        self.ui.account_name_label.setText(option)
        self.show_table()

        # when the file window close
    def closeEvent(self, event):
        for file in self.file_handle.temp_files:
            self.file_handle.delete_temp_file(file)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('style.qss', 'r') as styling:
        style = styling.read()

    app.setStyleSheet(style)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
