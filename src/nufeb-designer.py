from MainWindowRunner import MainWindowRunner
from PyQt6 import  QtWidgets


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    MainWindowRunner = MainWindowRunner(MainWindow)


    MainWindow.show()
    sys.exit(app.exec())