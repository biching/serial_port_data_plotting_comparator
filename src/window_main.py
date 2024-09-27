from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QAction, QIcon, QKeySequence


class MainWindow(QMainWindow):
    def __init__(self, widget):
        super().__init__()
        self.setWindowTitle("uartToPlot")
        # self.centralWidget = widget
        self.setCentralWidget(widget)

        self.createActions()
        self.createToolBars()
        self.createStatusBar()

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createToolBars(self):
        self._tool_bar = self.addToolBar("Files")
        self._tool_bar.addAction(self._new_act)

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

        self._exit_act = QAction(
            QIcon.fromTheme(QIcon.ThemeIcon.ApplicationExit),
            "&ByeBye",
            self,
            shortcut=QKeySequence.Quit,
            statusTip="quit application",
            triggered=self.close,
        )

    @Slot()
    def toggle_setting(self):
        widget = self.centralWidget().toggle_setting()
