from PyQt5.QtWidgets import QDialog
from Widgets.disclaimer_widget import Ui_Disclaimer
from queries import query_processor

class Deletion_disclaimer_window(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_Disclaimer()
        self.current_account = parent.current_account
        self.accountID = parent.accountID
        self.userID = parent.userID
        self._parent = parent
        self.query = query_processor()
        self.ui.setupUi(self)
        self.signal_connect()

    def signal_connect(self):
        self.setObjectName("disclaimer_widget")
        self.ui.disclaimer_label.setText("Deleting the account will result in the permanent removal of related transactions and files")
        self.ui.proceed_button.clicked.connect(self.proceed_button_clicked)
        self.ui.cancel_button.clicked.connect(self.cancel_button_clicked)

    def proceed_button_clicked(self):
        main_window = self._parent.parent()
        main_window.ui.stackedWidget.setCurrentWidget(main_window.ui.home_page)
        options = self.query.compute_account_options(self.userID)

        if options and self.current_account in options:
            options.remove(self.current_account)

        if options:
            accountID = self.query.get_accountID(options[0], self.userID)
            main_window.update_account(options[0], accountID)
        else:
            main_window.update_account("Not selected", None)
        main_window.home_page_handler()
        self.query.delete_account(self.accountID)
        main_window.home_page_handler()
        self.close()

    def cancel_button_clicked(self):
        self.close()
