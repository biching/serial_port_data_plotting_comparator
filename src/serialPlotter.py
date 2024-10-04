import sys
from PySide6.QtWidgets import QApplication
from window_main import MainWindow


if __name__ == "__main__":
    app = QApplication()
    mainWindow = MainWindow()
    mainWindow.resize(1600, 800)
    mainWindow.show()

    sys.exit(app.exec())
