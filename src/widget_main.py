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
    QSpacerItem,
)
from PySide6.QtCore import Slot, Qt, Signal
import threading
from enum import Enum

from widget_combo_box import ComboBox
from widget_plot import CustomPlotWidget


class Widget(QWidget):
    showSerialComboboxSignal = Signal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("UART PLOT")
        self._plotWidget = CustomPlotWidget()
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
        # spacer的横向不影响其他排序就行，纵向最高60，可被压缩
        spcaceItem = QSpacerItem(10, 60, QSizePolicy.Preferred, QSizePolicy.Maximum)
        self._setting_layout.addWidget(self._uart_groupbox)
        self._setting_layout.addSpacerItem(spcaceItem)
        self._setting_layout.addWidget(self._plot_setting_groupbox)
        self._setting_layout.addSpacerItem(spcaceItem)
        self._setting_layout.addWidget(self._selector_groupbox)
        self._setting_layout.addStretch()
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
        self.refresh_serial_port()
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

        self._refresh_data_interval_box = QLineEdit(str(self._plotWidget._refresh_interval_millisec))
        self._refresh_data_interval_box.textChanged.connect(self.refresh_data_interval_changed)
        self._refresh_data_interval_box.setFixedWidth(50)
        self._refresh_data_interval_label = QLabel("Plot Interval")
        self._refresh_data_interval_label.setToolTip("data refresh interval (ms)")
        self._plot_setting_layout.addRow(self._refresh_data_interval_label, self._refresh_data_interval_box)

        self._plot_setting_groupbox = QGroupBox("Plot Setting")
        self._plot_setting_groupbox.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))
        self._plot_setting_groupbox.setLayout(self._plot_setting_layout)

    class FlagGroup(Enum):
        G1 = "1"
        G2 = "2"

        # flag should be: x1, x2, y1, y2...
        def is_belong_me(self, flag):
            if len(flag) != 2:
                return False
            return self.value == flag[1]

    def create_selector_group(self):

        ## selectors-定义
        self._selector_group1_layout = QVBoxLayout()
        self._selector_group2_layout = QVBoxLayout()
        self.data_boxes = {flag: QCheckBox(flag) for flag in self._plotWidget._data_flags}
        for flag, data_box in self.data_boxes.items():
            data_box.checkStateChanged.connect(
                # checkStateChanged的信号 会自动将changed state传给lambda的第一个变量
                lambda state, flag1=flag: self.box_changed(state, flag1)
            )  # lambda 表达式在循环中延迟赋值，导致此处不能简化为lambda: self.box_changed(state, flag)
            # data_box.setChecked(True)
            if self.FlagGroup.G1.is_belong_me(flag):
                self._selector_group1_layout.addWidget(data_box)

            if self.FlagGroup.G2.is_belong_me(flag):
                self._selector_group2_layout.addWidget(data_box)

        ## selectors-组装
        self._selector_groupbox = QGroupBox("Data selector")
        self._selector_layout = QHBoxLayout()
        self._selector_layout.addLayout(self._selector_group1_layout)
        self._selector_layout.addLayout(self._selector_group2_layout)
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
        if self.FlagGroup.G1.is_belong_me(flag):
            self._plotWidget.renew_plot_group1(state == Qt.CheckState.Checked, flag)
        if self.FlagGroup.G2.is_belong_me(flag):
            self._plotWidget.renew_plot_group2(state == Qt.CheckState.Checked, flag)
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
        self.parentWidget().statusBar().showMessage("detect serial port")
        items = self._plotWidget._serial_data.detect_serial_port()
        self.showSerialComboboxSignal.emit(items)

    def showSerialPortCombobox(self, items):
        self._portx_box.clear()
        self._portx_box.addItems(items)
        self._portx_box.setCurrentIndex(len(items) - 1)

    def serial_port_changed(self, idx):
        port = self._portx_box.currentText().split(" ")[0]
        self._plotWidget._serial_data.com.port = port
        self.parentWidget().statusBar().showMessage("port changed")

    def baudrate_changed(self, idx):
        self._plotWidget._serial_data.com.baudrate = self._baudrate_box.currentText()
        self.parentWidget().statusBar().showMessage("baudrate changed")

    def refresh_data_interval_changed(self, text):
        self._plotWidget.set_data_refresh_interval(int(text))
        self.parentWidget().statusBar().showMessage("data refresh interval changed")
