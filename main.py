import os, sys
from PyQt5.QtWidgets import  QApplication
from Widgets.user_authentication_page import UserAuthentication
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # reading style file
    style_path = os.path.join(os.path.dirname(__file__), "style_resource", "style.qss")
    with open(style_path, 'r') as styling:
        style = styling.read()

    # Apply the style sheet to the whole app
    app.setStyleSheet(style)
    window = UserAuthentication()
    window.show()

    sys.exit(app.exec())