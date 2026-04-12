from PyQt5.QtWidgets import  QWidget, QPushButton
from PyQt5.QtCore import Qt, QPoint
from queries import query_processor
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from Widgets.account_control_page import Account_control_page
from Widgets.change_confirmation_window import Change_confirmation_page

class Profile_page(QWidget):
    def __init__(self, current_account, parent):
        super().__init__(parent)
        self.current_account = current_account
        self.userID = parent.userID
        self._parent = parent
        self.username_button_state = False
        self.mail_button_state = False
        self.query = query_processor()
        self.profile_signals_connect()
        self.show_profile_page()

    def profile_signals_connect(self):
        parent_window = self._parent
        # previous example

        parent_window.ui.username_change_button.clicked.connect(self.change_username)
        parent_window.ui.email_change_button.clicked.connect(self.change_user_mail)

    def show_profile_page(self):
        tree_model = QStandardItemModel()
        tree_model.setHorizontalHeaderLabels(["Account Name", ""])
        parent_window = self._parent
        result = self.query.get_user_info(self.userID)

        result_accounts = self.query.get_number_of_accounts(self.userID)

        parent_window.ui.username_change_value.setText(result[0])
        parent_window.ui.email_change_value.setText(result[1])
        parent_window.ui.user_created_value.setText(str(result[2]))
        parent_window.ui.user_accounts_value.setText(str(len(result_accounts)))

        for account in result_accounts:
            item = QStandardItem(account)
            item.setEditable(False)
            tree_model.appendRow(item)
            tree_model.setSortRole(Qt.UserRole)

        parent_window.ui.accounts_treeView.setModel(tree_model)
        parent_window.ui.accounts_treeView.setColumnWidth(0, 300)
        parent_window.ui.accounts_treeView.setColumnWidth(1, 80)

        for row_index in range(len(result_accounts)):
            see_account = QPushButton("Edit/View")
            see_account.setObjectName('see_account')
            parent_window.ui.accounts_treeView.setIndexWidget(tree_model.index(row_index, 1), see_account)
            account_name = tree_model.data(tree_model.index(row_index, 0))
            see_account.clicked.connect(lambda click, name=account_name: self.navigate_to_account_control(name))
        self.activate(False, "both")

    def activate(self, flag, type):
        parent_window = self._parent
        dictionary = {
            "mail": [parent_window.ui.email_change_value, parent_window.ui.email_change_button],
            "name": [parent_window.ui.username_change_value, parent_window.ui.username_change_button]
        }
        if type != "both":
            widgets = [dictionary.get(type)]
        else:
            widgets = dictionary.values()

        for value, button in widgets:
            value.setEnabled(flag)
            if flag:
                button.setText("save")
                value.setStyleSheet("border: 2px solid blue;")
            else:
                button.setText("edit")
                value.setStyleSheet("border: 2px solid black;")

    def change_username(self):
        parent_window = self._parent
        state = self.username_button_state
        self.username_button_state = not state
        self.activate(self.username_button_state, "name")

        if (self.username_button_state is False):
            account_name = parent_window.ui.username_change_value.text()
            self.query.update_user(self.userID, new_username=account_name)
            self.show_profile_page()


    def change_user_mail(self):
        parent_window = self._parent
        state = self.mail_button_state
        self.mail_button_state = not state

        if (self.mail_button_state is True):
            confirmation_window = Change_confirmation_page(self)
            confirmation_window.finished.connect(self.capture_result)
            global_pos = parent_window.ui.email_change_button.mapToGlobal(QPoint(0,0))
            confirmation_window.move(global_pos.x(), global_pos.y() + parent_window.ui.email_change_button.height())
            confirmation_window.start_time()
            confirmation_window.show()

        if (self.mail_button_state is False):
            email = parent_window.ui.email_change_value.text()
            self.query.update_user(self.userID, new_email=email)
            self.show_profile_page()

    def navigate_to_account_control(self, name):
        parent_window = self._parent
        accountID = self.query.get_accountID(name, self.userID)
        parent_window.update_parent(name, accountID)
        account_control = Account_control_page(name, parent_window)
        account_control.show()

    def capture_result(self):
        self.activate(self.mail_button_state, "mail")


