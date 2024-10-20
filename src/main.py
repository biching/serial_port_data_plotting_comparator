import sys
from PySide6.QtWidgets import QApplication
from window_main import MainWindow


if __name__ == "__main__":
    app = QApplication()
    mainWindow = MainWindow()
    mainWindow.resize(1800, 1000)
    mainWindow.show()

    sys.exit(app.exec())
