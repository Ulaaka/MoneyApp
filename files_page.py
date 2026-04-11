from PyQt5.QtWidgets import  QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from disclaimer_window import Disclaimer_window
from queries import query_processor
from FILE_handling import file_handling

class Files_page():
    def __init__(self, parent):
        self._parent = parent

    def show_files(self):
        parent_window = self._parent
        query = query_processor()
        if not parent_window.accountID:
            return
        self.files = query.get_files(parent_window.accountID)
        if self.files is None:
            self.set_files(False)
            parent_window.ui.no_file_label.setText(f"No files found for '{parent_window.account_name}'")
        else:
             self.set_files(True)
             self.files_exist()

             for row_index in range(len(self.files)):
                item_button = QPushButton("Remove")
                view_button = QPushButton("View")
                item_button.setObjectName("item_button")
                view_button.setObjectName("view_button")
                parent_window.ui.treeView.setIndexWidget(self.tree_model.index(row_index, 4), item_button)
                parent_window.ui.treeView.setIndexWidget(self.tree_model.index(row_index, 5), view_button)
                fileID = self.tree_model.data(self.tree_model.index(row_index, 0), Qt.UserRole)
                item_button.clicked.connect(lambda click, id=fileID: self.delete_file_wht_ID(id))
                view_button.clicked.connect(lambda clicked, id=fileID: self.view_file_with_ID(id))
    
    def view_file_with_ID(self, id):
        parent_window = self._parent
        file_handle = file_handling(parent_window.accountID, parent_window.key)
        file_handle.view_file(fileID=id)

    def delete_file_wht_ID(self, fileID):
        disclaimer = Disclaimer_window(fileID, self._parent)
        disclaimer.show()

    def files_exist(self):
        parent_window = self._parent
        file_handle = file_handling(parent_window.accountID, parent_window.key)
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(["Name", "Size", "Kind", "Date Added", "", ""])

        for  tuple in self.files:
            items = []
            for col_index, col_val in enumerate(tuple[1:]):
                if (col_index == 1):
                    converted_size_str = file_handle.convert_file_size(col_val)
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
            self.tree_model.appendRow(items)
            self.tree_model.setSortRole(Qt.UserRole)

            parent_window.ui.treeView.setModel(self.tree_model)
    def set_files(self, flag):
        parent_window = self._parent
        if flag:
            parent_window.ui.files_stack.setCurrentWidget(parent_window.ui.files_tree_page)
        else:
            parent_window.ui.files_stack.setCurrentWidget(parent_window.ui.no_file_page)
