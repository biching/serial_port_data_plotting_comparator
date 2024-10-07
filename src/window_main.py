from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction, QIcon, QKeySequence
from widget_main import Widget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("uartToPlot")
        self.setCentralWidget(Widget(self))

        self.createActions()
        self.createToolBars()
        self.createStatusBar()

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createToolBars(self):
        self._tool_bar = self.addToolBar("Files")
        self._tool_bar.addAction(self._new_act)
        self._tool_bar.addSeparator()
        self._tool_bar.addAction(self._start_act)
        self._tool_bar.addAction(self._stop_act)

        self._stop_act.setVisible(False)
        self._start_act.setVisible(True)

        self.addToolBar(Qt.LeftToolBarArea, self._tool_bar)

    def createActions(self):
        self._new_act = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious),
            "&Setting",
            self,
            shortcut=QKeySequence.Preferences,
            statusTip="Show/Hide Setting",
            triggered=self.toggle_setting,
        )

        self._start_act = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackStart),
            "&start",
            self,
            shortcut=QKeySequence.Open,
            statusTip="start plotting",
            triggered=self.start_plotting,
        )
        self._stop_act = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.MediaPlaybackPause),
            "&stop",
            self,
            shortcut=QKeySequence.Close,
            statusTip="stop plotting",
            triggered=self.stop_plotting,
        )

    @Slot()
    def toggle_setting(self):
        widget = self.centralWidget().toggle_setting()

    @Slot()
    def start_plotting(self):
        self.statusBar().showMessage("start plotting")
        if self.centralWidget()._plotWidget.start_plotting():
            self._stop_act.setVisible(True)
            self._start_act.setVisible(False)

    @Slot()
    def stop_plotting(self):
        self.statusBar().showMessage("stop plotting")
        if self.centralWidget()._plotWidget.stop_plotting():
            self._stop_act.setVisible(False)
            self._start_act.setVisible(True)
