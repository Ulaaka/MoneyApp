import pandas as pd
from PyQt5.QtCore import QAbstractTableModel, Qt
from queries import query_processor
# https://www.pythonguis.com/faq/editing-pyqt6-tableview/
class ListModel(QAbstractTableModel):
    def __init__(self, data, parent):
        super().__init__(parent)
        self._data = data
        self.query = query_processor()
        self.userID = parent.userID

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        # add columns + extra column at the back
        return self._data.shape[1] + 1

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                column =int(index.column())
                if column < 9:
                    value = self._data.iloc[index.row(), index.column()]
                else:
                    value = ""
                return str(value)

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            column =int(index.column())
            row = int(index.row())
            transactionID = int(self._data.iloc[row, 0])
            self._data.iloc[index.row(), index.column()] = value
            # change category
            if column == 6:
                # applies changes to the closest transactions
                self.query.change_category(self.userID, value, transactionID)
                self.parent().show_table()
                # if does not want to
                # update_category()
            if column == 5:
                # 
                if self.query.change_description_and_update(value, transactionID):
                    self.parent().show_table()
            return True
        return False

    def headerData(self, col, orientation, role):
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            if (col < 9):
                return self._data.columns[col]
            else:
                return ""

    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsEditable
        )