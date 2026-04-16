from PyQt5.QtCore import QThread, pyqtSignal
# https://realpython.com/python-pyqt-qthread/
class ThreadWorker(QThread):
    done = pyqtSignal()

    def __init__(self, todo):
        super().__init__()
        self.function = todo

    def run(self):
        self.function()
        self.done.emit()