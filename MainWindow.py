import sys, pycountry
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QPoint, QDate

from queries import query_processor
from datetime import datetime
from FILE_handling import file_handling

from Widgets.financial_app import Ui_MainWindow
from Widgets.account_selection_and_add_window import Account_selection_page
from Widgets.account_control_page import Account_control_page
from Widgets.profile_page import Profile_page
from Widgets.upload_Page import Upload_page
from Widgets.files_page import Files_page
from Widgets.home_page import Home_page
from Widgets.settings_page import Change_password_page, Delete_user_account, Change_category
from Widgets.stats_page import Stats_page
class MainWindow(QMainWindow):
    def __init__(self, controller , key, userID):
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key
        self.userID = userID
        self.account_name = None
        self.accountID = None
        self.status_panel = False
        self.start_date = None
        self.end_date = None
        self.currency_list = [f"{currency.alpha_3} - {currency.name} " for currency in pycountry.currencies]

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.file_handle = file_handling(self.userID, self.accountID, self.key)
        self.home_manager = Home_page(self)
        self.upload_manager = Upload_page(self)
        self.file_manager = Files_page(self)
        self.account_manager = Account_selection_page(self)
        self.profile_manager= Profile_page(self.account_name, self)
        self.category_change_manager = Change_category(self)
        self.account_control_manager = Account_control_page(self.account_name, self)
        self.stats_manager = Stats_page(self)

        self.query = query_processor()

        self.MainWindow_signals_connection()
        self.home_page_handler()

    def home_page_handler(self):
        query = query_processor()
        options = query.compute_account_options(self.userID)

        if options is None:
            self.home_manager.set_table(False)
            self.ui.no_account_label.setText(f"No Account found")
            self.ui.account_name_label.setText("Not selected")
        else:
            if self.account_name is None:
                accountID = query.get_accountID(options[0], self.userID)
                self.update_account(options[0], accountID)
            else:
                self.home_manager.show_table()

    def account_page_handler(self):
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

    def update_parent(self, option, accountID):
        self.account_name = option
        self.accountID = accountID
        self.ui.account_name_label.setText(option)
        self.update_current_widget()

    def update_current_widget(self):
        currentWidget = self.ui.stackedWidget.currentWidget()

        if currentWidget == self.ui.home_page:
            self.home_manager.show_table()
        elif currentWidget == self.ui.files_page:
            self.file_manager.show_files()
        elif currentWidget == self.ui.account_page:
            self.account_control_manager = Account_control_page(self.account_name, self)
            self.account_control_manager.show_account_control_page()
        elif currentWidget == self.ui.settings_page:
            self.change_category_handle()
        elif currentWidget == self.ui.stats_page:
            self.stats_manager = Stats_page(self)

    def update_account(self, new_account_name, new_accountID):
        self.account_name = new_account_name
        self.accountID = new_accountID
        self.ui.account_name_label.setText(new_account_name)
        self.start_date = None
        self.end_date = None
        self.home_manager.show_table()

    def MainWindow_signals_connection(self):
        # Default connections
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)
        self.ui.full_menu_widget.hide()

        # -- BUTTONS CONNECTIONS -- 
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

        self.ui.account_button.clicked.connect(self.account_page_handler)

        self.ui.change_category_button.clicked.connect(self.change_category_handle)
        self.ui.change_password_button.clicked.connect(self.change_password_handle)
        self.ui.delete_user_button.clicked.connect(self.delete_user_handle)
        self.ui.logout_button.clicked.connect(self.logout_handle)
        self.ui.privacy_note_button.clicked.connect(self.privacy_note_handle)

        self.ui.account_name_label.mousePressEvent = self.account_label_clicked

        current_date = datetime.now()
        self.ui.transaction_date_edit.setDate(QDate(current_date.year, current_date.month, current_date.day))

    def change_category_handle(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)
        self.ui.settings_stack.setCurrentWidget(self.ui.category_change_page)
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.category_table_page)
        self.category_change_manager.show_category_table()

    def change_password_handle(self):
        self.ui.settings_stack.setCurrentWidget(self.ui.change_password_page)
        self.change_password_handler = Change_password_page(self)

    def delete_user_handle(self):
        self.ui.settings_stack.setCurrentWidget(self.ui.delete_user_account_page)
        self.delete_user_handler = Delete_user_account(self)

    def logout_handle(self):
        self.log_out()

    def privacy_note_handle(self):
        self.ui.settings_stack.setCurrentWidget(self.ui.privacy_note_page)

    def account_label_clicked(self, event):
        current_account = self.ui.account_name_label.text()
        if current_account == "Not selected":
            return
        self.account_control_manager = Account_control_page(current_account, self)
        self.account_control_manager.show_account_control_page()

    def home_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)
        self.home_manager.show_table()

    def upload_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.upload_page)
        self.ui.upload_stack.setCurrentWidget(self.ui.upload_page_2)

    def file_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.files_page)
        self.file_manager.show_files()

    def stats_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.stats_page)
        self.stats_manager = Stats_page(self)

    def profile_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)
        self.profile_manager.show_profile_page()

    def settings_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)
        self.ui.settings_stack.setCurrentWidget(self.ui.category_table_page)

        # when the file window close
    def closeEvent(self, event):
        for file in self.file_handle.temp_files:
            self.file_handle.delete_temp_file(file)
        event.accept()

    def log_out(self):
        self.controller.start_login()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    with open('style.qss', 'r') as styling:
        style = styling.read()

    app.setStyleSheet(style)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
