from PyQt5.QtWidgets import QMessageBox, QLineEdit, QPushButton, QHeaderView
from PyQt5.QtCore import QPoint, QSortFilterProxyModel, Qt

from queries import query_processor
from BASE_Classes import password_class, cryptography
from Widgets.change_confirmation_window import Change_confirmation_page
from Widgets.Table_View import ListModelCategory
from Widgets.home_page import Home_page
from system_functions import system_functions
import os, base64, secrets
class Change_password_page():
    def __init__(self, parent):
        self._parent = parent
        self.password_manager = password_class()
        self.query = query_processor()
        self.objective = 0
        self.change_password_signals_connect()

    def change_password_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.change_password_button_settings.clicked.connect(self.change_password)
        parent_window.ui.forgot_password_button_settings.clicked.connect(self.forgot_password_handle)
        parent_window.ui.current_password_line.setEchoMode(QLineEdit.Password)
        parent_window.ui.new_password_line.setEchoMode(QLineEdit.Password)
        parent_window.ui.new_password_line.setToolTip(
            "Your password must be at least 8 characters \n"
            "should include: \n"
            "- a combination of numbers\n"
            "- letters\n"
            "- special characters (!$@%)"
        )

    def change_password(self):
        crypto = cryptography()
        system = system_functions()
        query = query_processor()
        parent_window = self._parent
        current_password = parent_window.ui.current_password_line.text()
        new_password = parent_window.ui.new_password_line.text()
        if (self.objective == 0):
            safety = self.password_manager.check_password_safety(new_password)

            if current_password and new_password:
                if not safety:
                    QMessageBox.warning(
                        parent_window,
                        'Error',
                        "Your password must be at least 8 characters\n"
                        "should include:\n"
                        "- a combination of numbers\n"
                        "- letters\n"
                        "- special characters (!$@%)"
                    )
                    return

                hash_password = self.query.get_hashed_password(userID=parent_window.userID)[0]
                compare_current = self.password_manager.check_password(current_password, hash_password)

                if not compare_current:
                    QMessageBox.warning(
                        parent_window, 'Error', "Current Password Does Not Match")
                    return

                compare_new = self.password_manager.check_password(new_password, hash_password)

                if compare_new:
                    QMessageBox.warning(
                        parent_window, 'Error', "New password must different from current password")
                    return

                result = self.password_manager.change_password(parent_window.userID, new_password)
                # password changed
                if result:
                    parent_window.ui.current_password_line.clear()
                    parent_window.ui.new_password_line.clear()
                    enc_data_key, salt = system.update_data_key(current_password, new_password, self._parent.userID)
                    query.change_data_key_salt(enc_data_key, salt, self._parent.userID)
                    QMessageBox.information(
                        parent_window, "Confirmation", "Password Changed")
                    return
            else:
                QMessageBox.warning(
                    parent_window, "Error", "Please enter both fields")
                return
        else:
            # when forgot password
            result = self.password_manager.change_password(parent_window.userID, new_password)
            if result:
                parent_window.ui.current_password_line.show()
                parent_window.ui.current_password_line.clear()
                parent_window.ui.new_password_line.clear()
                self.objective = 0

                new_salt = os.urandom(32)
                new_wrapping_key = crypto.generate_key(new_password, new_salt)
                new_data_key = base64.urlsafe_b64encode(secrets.token_bytes(32))
                new_encrypted_data_key = crypto.encrypt_data_key(new_wrapping_key, new_data_key)
                query.change_data_key_salt(new_encrypted_data_key, new_salt, self._parent.userID)
                query.delete_user_files(self._parent.userID)
                QMessageBox.information(
                    parent_window, "Confirmation", "Password Changed")
                return

    def forgot_password_handle(self):
        parent_window = self._parent
        confirmation_window = Change_confirmation_page(parent_window)
        confirmation_window.finished.connect(self.capture_result)
        global_pos = parent_window.ui.forgot_password_button_settings.mapToGlobal(QPoint(0,0))
        confirmation_window.move(global_pos.x(), global_pos.y() + parent_window.ui.forgot_password_button_settings.height())
        confirmation_window.start_time()
        confirmation_window.show()

    def capture_result(self):
        parent_window = self._parent
        parent_window.ui.current_password_line.hide()
        parent_window.ui.new_password_line.clear()
        self.objective = 1

class Delete_user_account():
    def __init__(self, parent):
        self._parent = parent
        self.query = query_processor()
        self.password_manager = password_class()
        self.delete_user_signals_connect()

    def delete_user_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.delete_user_button_2.clicked.connect(self.delete_user)
        parent_window.ui.delete_user_line.setEchoMode(QLineEdit.Password)

    def delete_user(self):
        parent_window = self._parent
        current_password = self._parent.ui.delete_user_line.text()

        # this needs to be a single func
        hash_password = self.query.get_hashed_password(userID=parent_window.userID)[0]
        compare = self.password_manager.check_password(current_password, hash_password)
        if compare:
            parent_window.log_out()
            self.query.delete_user(parent_window.userID)

class Change_category():
    def __init__(self, parent):
        self._parent = parent
        self.home_page = Home_page(parent)
        self.category_signals_connect()

    def category_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        parent_window.ui.category_table.verticalHeader().setVisible(False)

    def show_category_table(self):
        query = query_processor()
        parent_window = self._parent
        if not parent_window.accountID:
            QMessageBox.warning(parent_window, "error", "Please create an account first")
            return

        categories = query.get_category_info(parent_window.userID, parent_window.accountID, asDF=True)
        # add extra row to allow for category add
        categories.loc[len(categories)] = [-1, "", "", ""]
        self.set_category_table(True)

        # -- TABLE LOADING -- 
        self.model = ListModelCategory(categories, parent_window, self)
        self.data = categories

        # Set the search filter for the table
        # inspired from:  https://www.youtube.com/watch?v=53bZSTSLUqI

        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(self.model)
        proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        proxy_model.setFilterKeyColumn(2)
        parent_window.ui.category_line.textChanged.connect(lambda text: self.filtered_search(text, proxy_model, categories))
        parent_window.ui.category_table.setModel(proxy_model)

        self.load_buttons(proxy_model, categories)
        # hide the id, list columns
        hidden_columns = [0, 1]
        for i in hidden_columns:
            parent_window.ui.category_table.setColumnHidden(i, True)


    def set_category_table(self, flag):
        parent_window = self._parent
        if flag:
            parent_window.ui.settings_stack.setCurrentWidget(parent_window.ui.category_table_page)
        else:
            parent_window.ui.settings_stack.setCurrentWidget(parent_window.ui.no_category_page)


    def handle_add_button(self):
        query = query_processor()
        parent_window = self._parent
        description = self.model.description
        name = self.model.name

        query.add_category_update(parent_window.userID, parent_window.accountID, description, name)
        self.show_category_table()
        self.home_page.show_table()

    def handle_remove_button(self, categoryID, category_name):
        parent_window = self._parent
        query = query_processor()
        query.delete_category(int(categoryID))
        query.update_transaction_after_deletion_description(parent_window.userID, parent_window.accountID, str(category_name))
        self.show_category_table()
        self.home_page.show_table()

    def filtered_search(self, text, proxy, categories):
        proxy.setFilterRegExp(text)
        self.load_buttons(proxy, categories)

    def load_buttons(self, proxy, categories):
        parent_window = self._parent
        for row_index in range(proxy.rowCount()):
            index_button = proxy.index(row_index, proxy.columnCount() - 1)
            source_model = proxy.sourceModel()
            source_index = proxy.mapToSource(index_button)
            category_id = source_model._data.iloc[source_index.row(), 0]
            category_name = source_model._data.iloc[source_index.row(), 3]
            if (proxy.rowCount() == 1 or row_index >= proxy.rowCount() - 1):
                add_button = QPushButton("Add")
                add_button.setObjectName("view_button")
                parent_window.ui.category_table.setIndexWidget(index_button, add_button)
                add_button.clicked.connect(lambda : self.handle_add_button())
            else:
                remove_button = QPushButton("Remove")
                remove_button.setObjectName("item_button")
                parent_window.ui.category_table.setIndexWidget(index_button, remove_button)
                remove_button.clicked.connect(lambda clicked, id=category_id, name = category_name: self.handle_remove_button(id, name))