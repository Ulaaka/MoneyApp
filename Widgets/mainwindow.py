import sys, pycountry
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QPoint, QDate

from db_queries import QueryProcessor
from datetime import datetime
from file_handle import FileHandling

from generated_files.main_app_generated import Ui_MainWindow
from Widgets.account_control_page import AccountControlPage
from Widgets.account_selection_window import AccountSelectionPage
from Widgets.profile_page import ProfilePage
from Widgets.upload_page import UploadPage
from Widgets.files_page import FilePage
from Widgets.home_page import HomePage
from Widgets.settings_page import Change_password_page, Delete_user_account, Change_category
from Widgets.graphs_page import GraphPage

class MainWindow(QMainWindow):
    """
    Main Window controller for the application
    Coordinates pages' navigation, account selection and interaction between different UI widgets.
    """
    def __init__(self, controller , key, userID):
        """
        Constructor for the main window class
        Initialises the home page
        """
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key
        self.userID = userID
        self.account_name = None
        self.accountID = None
        self.status_panel = False
        self.start_date = None
        self.end_date = None

        # list of currencies
        self.currency_list = [f"{currency.alpha_3} - {currency.name} " for currency in pycountry.currencies]

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.file_handle = FileHandling(self.userID, self.accountID, self.key)
        self.home_manager = HomePage(self)
        self.upload_manager = UploadPage(self)
        self.file_manager = FilePage(self)
        self.account_manager = AccountSelectionPage(self)
        self.profile_manager= ProfilePage(self.account_name, self)
        self.category_change_manager = Change_category(self)
        self.account_control_manager = AccountControlPage(self.account_name, self)
        self.stats_manager = GraphPage(self)
        self.query = QueryProcessor()

        self.MainWindow_signals_connection()

        # Show home page when first opened
        self.home_page_handler()

    def home_page_handler(self):
        """
        Handles the state of home page and corresponding visuals
        """
        query = QueryProcessor()
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
        """
        Opens or closes the account selection panel, showing it under the button
        and connecting corresponding signals.
        """
        if not self.status_panel:
            self.panel = AccountSelectionPage(self)
            self.panel.chose_account.connect(self.update_parent)

            # Show the window directly down the button
            global_pos = self.ui.account_button.mapToGlobal(QPoint(0,0))
            self.panel.move(global_pos.x(), global_pos.y() +self.ui.account_button.height() + 20)
            self.panel.finished.connect(lambda: setattr(self, 'status_panel', False))
            self.panel.show()
            self.status_panel = True
        else:
            self.panel.close()
            self.status_panel = False

    def update_parent(self, option, accountID):
        """
        Updates the main variables of the app where the window/pages depend on
        After account is changed, widget are refreshed to get accurate information/state
        """
        self.account_name = option
        self.accountID = accountID
        self.ui.account_name_label.setText(option)
        self.update_current_widget()

    def update_current_widget(self):
        """
        Update the current widgets, to show updated information/state
        """
        currentWidget = self.ui.stackedWidget.currentWidget()

        if currentWidget == self.ui.home_page:
            self.home_manager.show_table()
        elif currentWidget == self.ui.files_page:
            self.file_manager.show_files()
        elif currentWidget == self.ui.account_page:
            self.account_control_manager = AccountControlPage(self.account_name, self)
            self.account_control_manager.show_account_control_page()
        elif currentWidget == self.ui.settings_page:
            self.change_category_handle()
        elif currentWidget == self.ui.stats_page:
            self.stats_manager = GraphPage(self)

    def update_account(self, new_account_name, new_accountID):
        """
        Order of update actions when account is updated
        """
        self.account_name = new_account_name
        self.accountID = new_accountID
        self.ui.account_name_label.setText(new_account_name)
        self.start_date = None
        self.end_date = None
        self.home_manager.show_table()

    def MainWindow_signals_connection(self):
        """
        MainWindow signal connection
        """
        # Set the Home Page as the default page
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
        """
        Opens/Updates category change table page
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)
        self.ui.settings_stack.setCurrentWidget(self.ui.category_change_page)
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.category_table_page)
        self.category_change_manager.show_category_table()

    def change_password_handle(self):
        """
        Opens/Updates password change page
        """
        self.ui.settings_stack.setCurrentWidget(self.ui.change_password_page)
        self.change_password_handler = Change_password_page(self)

    def delete_user_handle(self):
        """
        Opens/Updates user delete page
        """
        self.ui.settings_stack.setCurrentWidget(self.ui.delete_user_account_page)
        self.delete_user_handler = Delete_user_account(self)

    def logout_handle(self):
        """
        Triggered when logging out
        """
        self.log_out()

    def privacy_note_handle(self):
        """
        Opens Privacy None page
        """
        self.ui.settings_stack.setCurrentWidget(self.ui.privacy_note_page)

    def account_label_clicked(self, event):
        """
        Opens account selection window, manages its state
        """
        current_account = self.ui.account_name_label.text()
        if current_account == "Not selected":
            return
        self.account_control_manager = AccountControlPage(current_account, self)
        self.account_control_manager.show_account_control_page()

    def home_page_show(self):
        """
        Opens home page, its corresponding widgets
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)
        self.home_manager.show_table()

    def upload_page_show(self):
        """
        Opens upload page, its corresponding widgets
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.upload_page)
        self.ui.upload_stack.setCurrentWidget(self.ui.upload_page_2)

    def file_page_show(self):
        """
        Opens file page, its corresponding widgets
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.files_page)
        self.file_manager.show_files()

    def stats_page_show(self):
        """
        Opens graphs page, its corresponding widgets
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.stats_page)
        self.stats_manager = GraphPage(self)

    def profile_page_show(self):
        """
        Opens profile page, its corresponding widgets
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)
        self.profile_manager.show_profile_page()

    def settings_page_show(self):
        """
        Opens settings page, its corresponding widgets
        """
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)
        self.ui.settings_stack.setCurrentWidget(self.ui.category_table_page)

    def closeEvent(self, event):
        """
        Deleted temporary files created when the app closes
        """
        for file in self.file_handle.temp_files:
            self.file_handle.delete_temp_file(file)
        event.accept()

    def log_out(self):
        """
        Log out the app
        """
        self.controller.start_login()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # loads style file where widget styles are defined
    with open('style.qss', 'r') as styling:
        style = styling.read()

    app.setStyleSheet(style)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
