from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QCheckBox,
    QSizePolicy,
    QFormLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QLabel,
)
from PySide6.QtCore import Slot, Qt, Signal
import threading

from widget_combo_box import ComboBox


class Widget(QWidget):
    showSerialComboboxSignal = Signal(list)

    def __init__(self, plotWidget):
        super().__init__()
        self.setWindowTitle("UART PLOT")
        self._plotWidget = plotWidget
        self.busy = False
        self.showSerialComboboxSignal.connect(self.showSerialPortCombobox)

        # 左上： 设置界面
        self.create_uart_group()

        self.create_plot_setting_group()

        # 左下: 数据选择器（selector）
        self.create_selector_group()

        # 左侧-总组装
        # self._setting_groupbox = QGroupBox("Setting")
        self._setting_groupbox = QWidget()
        self._setting_layout = QVBoxLayout()
        # self._left_layout.addLayout(self._setting_layout)
        self._setting_layout.addWidget(self._uart_groupbox)
        self._setting_layout.addStretch(1)
        self._setting_layout.addWidget(self._plot_setting_groupbox)
        self._setting_layout.addStretch(2)
        self._setting_layout.addWidget(self._selector_groupbox)
        self._setting_groupbox.setLayout(self._setting_layout)

        # 总组装
        self._main_layout = QHBoxLayout()
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## 左侧加入
        sizePolicy.setHorizontalStretch(1)
        self._setting_groupbox.setSizePolicy(sizePolicy)
        self._main_layout.addWidget(self._setting_groupbox)

        ## 右侧图表展示
        sizePolicy.setHorizontalStretch(8)
        self._plotWidget.setSizePolicy(sizePolicy)
        self._main_layout.addWidget(self._plotWidget)

        self.setLayout(self._main_layout)

    def create_uart_group(self):

        self._uart_groupbox = QGroupBox("UART Setting")
        self._uart_layout = QFormLayout(self._uart_groupbox)

        self._portx_box = ComboBox(self._uart_groupbox)
        # self.refresh_serial_port()
        self._portx_box.clicked.connect(self.refresh_serial_port)
        self._portx_box.currentIndexChanged.connect(self.serial_port_changed)
        self._uart_layout.addRow("Port", self._portx_box)
        self._baudrate_box = QComboBox(self._uart_groupbox)
        self._baudrate_box.currentIndexChanged.connect(self.baudrate_changed)
        self._uart_layout.addRow("Baudrate", self._baudrate_box)
        self._baudrate_box.addItems(["115200", "9600"])

        self._engine_button = QPushButton(self.tr("START"))
        self._engine_button.clicked.connect(self.start_stop_engine)
        self._uart_layout.addRow(self._engine_button)

        self._uart_layout.setLabelAlignment(Qt.AlignLeft)
        self._uart_groupbox.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

    def create_plot_setting_group(self):

        self._plot_setting_layout = QFormLayout()
        self._plot_setting_layout.setHorizontalSpacing(25)
        self._plot_setting_layout.setFormAlignment(Qt.AlignJustify)

        self._refresh_data_interval_box = QLineEdit("30")
        self._refresh_data_interval_box.textChanged.connect(self.refresh_data_interval_changed)
        self._refresh_data_interval_box.setFixedWidth(50)
        self._refresh_data_interval_label = QLabel("Plot Interval")
        self._refresh_data_interval_label.setToolTip("data refresh interval (ms)")
        self._plot_setting_layout.addRow(self._refresh_data_interval_label, self._refresh_data_interval_box)

        self._plot_setting_groupbox = QGroupBox("Plot Setting")
        self._plot_setting_groupbox.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._plot_setting_groupbox.setLayout(self._plot_setting_layout)

    def create_selector_group(self):

        ## height boxes
        self._height_layout = QVBoxLayout()
        self.data_boxes = {flag: QCheckBox(flag) for flag in self._plotWidget._data_flags}
        for flag, data_box in self.data_boxes.items():
            data_box.checkStateChanged.connect(
                lambda state, flag1=flag: self.box_changed(state, flag1)
            )  # lambda 表达式延迟赋值作妖
            # data_box.setChecked(True)
            self._height_layout.addWidget(data_box)

        # self.axis_y_selector = QGroupBox(self._selector_layout)
        # self.axis_y_selector.setLayout(self._select_vbox)

        ## vario box
        self._vario_box = QCheckBox("V")
        self._vario_box.setChecked(True)
        self._vario_box.stateChanged.connect(lambda state, flag="v": self.box_changed(state, flag))
        self._vario_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        ## 左下-组装
        self._selector_groupbox = QGroupBox("Data selector")
        self._selector_layout = QHBoxLayout()
        self._selector_layout.addLayout(self._height_layout)
        self._selector_layout.addWidget(self._vario_box)
        self._selector_groupbox.setLayout(self._selector_layout)

        self._selector_groupbox.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

    def toggle_setting(self):
        widget = self._setting_groupbox
        if widget.isVisible():
            widget.hide()
        else:
            widget.show()

    @Slot()
    def box_changed(self, state, flag):
        self._plotWidget.renew_item(state == Qt.CheckState.Checked, flag)
        print(f"state: {state == Qt.CheckState.Checked}; flag: {flag}")

    @Slot()
    def start_stop_engine(self):
        if self.busy:
            return
        self.busy = True

        if self._engine_button.text() == self.tr("START"):
            self.parentWidget().statusBar().showMessage("Serial Connectting")
            if self._plotWidget.start_plot():
                self._engine_button.setText(self.tr("STOP"))
                self.parentWidget().statusBar().showMessage("Serial Connected")
        else:
            self._plotWidget.stop_plot()
            self._engine_button.setText(self.tr("START"))
            self.parentWidget().statusBar().showMessage("Serial closed")

        self.busy = False

    def refresh_serial_port(self):
        t = threading.Thread(target=self.detect_serial_port_process)
        t.setDaemon(True)
        t.start()

    def detect_serial_port_process(self):
        items = self._plotWidget._serial_data.detect_serial_port()
        self.showSerialComboboxSignal.emit(items)

    def showSerialPortCombobox(self, items):
        self._portx_box.clear()
        self._portx_box.addItems(items)

    def serial_port_changed(self, idx):
        port = self._portx_box.currentText().split(" ")[0]
        self._plotWidget._serial_data.portx = port

    def baudrate_changed(self, idx):
        self._plotWidget._serial_data.paudrate = self._baudrate_box.currentText()

    def refresh_data_interval_changed(self, text):
        self._plotWidget.set_data_refresh_interval(int(text))
