import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from widget_main import Widget
from widget_plot import CustomPlotWidget

from window_main import MainWindow
from data_serial import SerialData


if __name__ == "__main__":
    app = QApplication()

    data_flags = ["x", "y", "z", "v"]
    # 单独线程：读取数据并解析
    serialData = SerialData(data_flags)

    plotWidget = CustomPlotWidget(serialData)
    widget = Widget(plotWidget)

    mainWindow = MainWindow(widget)
    mainWindow.resize(1200, 500)
    mainWindow.show()

    sys.exit(app.exec())
