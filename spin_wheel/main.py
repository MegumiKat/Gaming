# main.py
import sys
from PyQt6 import QtWidgets
from main_window import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.resize(800, 550)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()