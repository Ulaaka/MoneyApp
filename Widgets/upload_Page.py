import sys, shutil
from datetime import date
from decouple import config

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate, pyqtSignal, QObject

from Widgets.live_output_window import LiveOutputWindow
from Widgets.thread_worker import ThreadWorker
from Widgets.home_page import HomePage

from db_queries import QueryProcessor
from file_handle import FileHandling

class UploadPage():
    def __init__(self, parent):
        self._parent = parent
        self.home_page = HomePage(parent)
        self.current_date = date.today()
        self.upload_signals_connect()

    def upload_signals_connect(self):
        parent_window = self._parent
        parent_window.ui.upload_file_button.clicked.connect(self.upload_file)
        parent_window.ui.add_transaction_button.clicked.connect(self.add_transaction)


    def add_transaction(self):
        parent_window = self._parent
        query = QueryProcessor()
        if parent_window.accountID is None:
            QMessageBox.warning(
            parent_window, "Error", "Please create an account first")
            return

        try:
            date_input = parent_window.ui.transaction_date_edit.date().toPyDate()
            type = parent_window.ui.transaction_type_combo.currentText()
            description = parent_window.ui.description_text.toPlainText()
            amount = int(parent_window.ui.amount_transaction_line.text())
            balance = int(parent_window.ui.balance_transaction_line.text())
        except:
            QMessageBox.warning(
            parent_window, "Error", "Password fill the required fields")
            return

        if date_input and type and description and amount:
            if not balance:
                balance = 0
            if date_input > self.current_date:
                self.clear_fields()
                QMessageBox.warning(
                parent_window, "Error", "Entered date is not valid")
                return

            #transaction_list.append((accountID, self.file_ID, self.change_to_date(row[0]), row[1], row[2], category, Decimal(row[3]),  Decimal(row[4])))
            category = query.return_updated_category(parent_window.userID, parent_window.accountID, description)
            transaction_list = [(parent_window.accountID, 1, date_input, type, description, category, amount, balance)]
            query.insert_into_transactions(transaction_list)
            self.clear_fields()
            self.home_page.show_table()

    def clear_fields(self):
        parent_window = self._parent
        parent_window.ui.transaction_date_edit.setDate(QDate(self.current_date .year, self.current_date .month, self.current_date .day))
        parent_window.ui.description_text.clear()
        parent_window.ui.amount_transaction_line.clear()
        parent_window.ui.balance_transaction_line.clear()

    def upload_file(self):
        parent_window = self._parent
        if (not parent_window.accountID):
            QMessageBox.warning(parent_window, 'Error', 'Please create an account first')
            return

        file_paths, _ = QFileDialog.getOpenFileNames(parent_window, 'Open File', "", "CSV Files (*.csv);;PDF Files (*.pdf)")
        if file_paths:
            for file_path in file_paths:
                shutil.copy(file_path, config('FOLDER_PATH'))

        saved_stdout = sys.stdout
        self.print_output = Stream()
        self.live_output = LiveOutputWindow(parent_window, saved_stdout)
        sys.stdout = self.print_output

        # process the files
        files_process = FileHandling(parent_window.userID, parent_window.accountID, parent_window.key)
        self.worker = ThreadWorker(files_process.process_files_in_folder)
        self.worker.start()
        self.print_output.input_text.connect(self.get_output)
        self.live_output.ui.textBrowser.adjustSize()
        self.live_output.adjustSize()
        self.live_output.show()

    def get_output(self, text):
        stripped_list = [line for line in text.splitlines() if line.strip() != ""]
        lines = "\n".join(stripped_list)
        self.live_output.ui.textBrowser.append(lines)

# custom class for capturing print outputs
class Stream(QObject):
    input_text = pyqtSignal(str)

    def write(self, text):
        self.input_text.emit(text)

    def flush(self):
        sys.stdout.flush()