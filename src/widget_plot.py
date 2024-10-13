from pyqtgraph import GraphicsLayoutWidget, mkPen, ViewBox
from PySide6.QtCore import QTimer
from data_serial import SerialData


class CustomPlotWidget(GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_data)
        self._data_flags = ["x1", "y1", "z1", "x2", "y2", "z2"]
        self._serial_data = SerialData(self._data_flags)
        self._data_item = {flag: None for flag in self._data_flags}
        self._pen_idx = 0
        self._refresh_interval_millisec = 50

        # return PlotItem
        self._plot_group1 = self.addPlot(title="Group1")
        self._plot_group1.addLegend(offset=(1, 1))
        self._plot_group1.showGrid(x=True, y=True)
        self._plot_group1.enableAutoRange()
        self._plot_group1.setMouseEnabled(False, False)
        self._plot_group1.setAutoVisible(y=True)
        self._plot_group1.setLabel(axis="left", text="y")

        # 预留位置
        self._plot_group2 = None

    def create_plot_group2(self):
        self.nextRow()

        self._plot_group2 = self.addPlot(title="Group2(disselectable)")
        self._plot_group2.addLegend(offset=(1, 1))
        self._plot_group2.showGrid(x=True, y=True)
        self._plot_group2.enableAutoRange()
        self._plot_group2.setLabel(axis="left", text="y")

    def get_pen(self):
        data_pen = [
            mkPen(cosmetic=True, width=1.0, color="k"),  # 难以识别，最后才能被选到
            mkPen(cosmetic=True, width=1.0, color="r"),
            mkPen(cosmetic=True, width=1.0, color="g"),
            mkPen(cosmetic=True, width=1.0, color="b"),
            mkPen(cosmetic=True, width=1.0, color="c"),
            mkPen(cosmetic=True, width=1.0, color="m"),
            mkPen(cosmetic=True, width=1.0, color="y"),
            mkPen(cosmetic=True, width=1.0, color="w"),
        ]
        self._pen_idx += 1
        if self._pen_idx >= len(data_pen):
            self._pen_idx %= len(data_pen)
        return data_pen[self._pen_idx]

    def _addPlotToGroup(self, group, flag):
        if self._data_item[flag] is None:
            self._data_item[flag] = group.plot(self._serial_data._data[flag], pen=self.get_pen(), name=flag)
        else:
            group.addItem(self._data_item[flag])

    def renew_plot_group1(self, state, flag):
        if state:
            self._addPlotToGroup(self._plot_group1, flag)
        else:
            self._plot_group1.removeItem(self._data_item[flag])

    def renew_plot_group2(self, state, flag):
        if state:
            if self._plot_group2 is None:
                self.create_plot_group2()
            elif self._plot_group2 not in self.items():
                self.nextRow()
                self.addItem(self._plot_group2)
            self._addPlotToGroup(self._plot_group2, flag)
        else:
            self._plot_group2.removeItem(self._data_item[flag])
            if len(self._plot_group2.items) == 0:
                self.removeItem(self._plot_group2)

    def start_plotting(self):
        if not self._serial_data.open_serial():
            return False

        # 定时任务，将新数据刷新到图表中
        print("parse time is set:")
        self._timer.start(self._refresh_interval_millisec)

        return True

    def set_data_refresh_interval(self, value):
        print(f"set_data_refresh_interval: {value}")
        self._refresh_interval_millisec = value
        self._timer.setInterval(self._refresh_interval_millisec)
        if self._timer.isActive():
            print(f"restart timer")
            self._timer.stop()
            self._timer.start()

    def stop_plotting(self):
        print("stop timer")
        self._timer.stop()
        print("close_serial")
        return self._serial_data.close_serial()

    def update_data(self):
        # 定时更新数据，并刷入到图表中
        self._serial_data.update_data()
        self.set_data()

    def set_data(self):
        for flag in self._serial_data._data_flags:
            if self._data_item[flag] is not None:
                self._data_item[flag].setData(self._serial_data._data[flag])

    def reset_data(self):
        print("reset data\n")
        self._serial_data.reset_data()
        self._plot_group1.disableAutoRange()
        self._plot_group1.enableAutoRange()
        self.set_data()
