import sys
from PySide6.QtWidgets import QApplication

from widget_main import Widget


from window_main import MainWindow


if __name__ == "__main__":
    app = QApplication()

    widget = Widget()

    mainWindow = MainWindow(widget)
    mainWindow.resize(1600, 800)
    mainWindow.show()

    sys.exit(app.exec())
