from PySide6.QtWidgets import (
    QComboBox,
)
from PySide6.QtCore import Signal


class ComboBox(QComboBox):
    clicked = Signal()

    def __init__(self, parent=None):
        QComboBox.__init__(self, parent=parent)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()

    def mouseReleaseEvent(self, QMouseEvent):
        self._showPopup()

    def _showPopup(self):
        max_w = 0
        for i in range(self.count()):
            w = self.view().sizeHintForColumn(i)
            if w > max_w:
                max_w = w
        self.view().setMinimumWidth(max_w + 50)
        super(ComboBox, self).showPopup()
