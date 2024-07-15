import sys

from PySide6 import QtGui as qg, QtWidgets as qw

from .app_windows import *
from .database import *


def main_cli():
    # Global variables to use throughout the application
    global app
    global db

    # Database initialization
    db = DataBase()

    # Application object initialization
    app = qw.QApplication(sys.argv)

    # Window look properties
    with open('dorm_accounting/style.css', 'r', encoding='UTF-8') as css:
        style = css.read()
    app.setStyleSheet(style)
    app.setWindowIcon(qg.QIcon(qg.QPixmap('dorm_accounting/favicon.ico')))

    # Main window
    main_window = Window_Rooms()
    app.main_window = main_window
    main_window.show()

    # If not authorized show password window
    if not db.authorized:
        main_window.hide()
        pass_window = Window_Password(main_window)
        pass_window.show()

    # Launch the application
    sys.exit(app.exec_())


if __name__ == '__main__':
    main_cli()
