import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream

from financial_app import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self, controller , key):
        super(MainWindow, self).__init__()

        self.controller = controller
        self.key = key

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.full_menu_widget.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.buttons_connected()

    def buttons_connected(self):
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


    def home_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home_page)

    def upload_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.upload_page)

    def file_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.files_page)

    def stats_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.stats_page)

    def profile_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.profile_page)

    def settings_page_show(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.settings_page)
