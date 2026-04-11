import sys, shutil
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from live_output_window import Live_output_window
from FILE_handling import file_handling
from stream import Stream
from thread_worker import Thread_worker

class Upload_page():
    def __init__(self, parent):
        self._parent = parent

    def upload_file(self):
        parent_window = self._parent
        if (not parent_window.accountID):
            QMessageBox.warning(parent_window, 'Error', 'Please create an account first')
            return

        file_paths, _ = QFileDialog.getOpenFileNames(parent_window, 'Open File', "", "CSV Files (*.csv);;PDF Files (*.pdf)")
        if file_paths:
            for file_path in file_paths:
                # config('FOLDER_PATH')
                shutil.copy(file_path, "/Users/nyamdorjbat-erdene/Final_year/exp_folder")

        saved_stdout = sys.stdout
        self.print_output = Stream()
        self.live_output = Live_output_window(parent_window, saved_stdout)
        self.print_output.input_text.connect(self.get_output)
        sys.stdout = self.print_output

        # process the files
        files_process = file_handling(parent_window.accountID, parent_window.key)
        self.worker = Thread_worker(files_process.process_files_in_folder)
        self.worker.start()
        self.live_output.ui.textBrowser.adjustSize()
        self.live_output.adjustSize()
        self.live_output.show()

    def get_output(self, text):
        stripped_list = [line for line in text.splitlines() if line.strip() != ""]
        lines = "\n".join(stripped_list)
        self.live_output.ui.textBrowser.append(lines)