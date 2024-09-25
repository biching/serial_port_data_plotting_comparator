from pyqtgraph import GraphicsLayoutWidget, mkPen
from PySide6.QtCore import QTimer
from data_serial import SerialData


class CustomPlotWidget(GraphicsLayoutWidget):
    def __init__(self):
        super().__init__()
        self._timer = QTimer()
        self._timer.timeout.connect(self.reset_data)
        self._data_flags = ["x", "y", "z"]
        self._serial_data = SerialData(self._data_flags)
        self._data_item = {flag: None for flag in self._data_flags}
        self._pen_idx = 0
        self._refresh_interval_millisec = 50

        # return PlotItem
        self._item1 = self.addPlot(title="height plotting")
        self._item1.addLegend(offset=(1, 1))
        self._item1.showGrid(x=True, y=True)
        self._item1.enableAutoRange("y")
        self._item1.setLabel(axis="left", text="y-height")
        self._item1.setTitle("height Chart")

        self.nextRow()

        self._item2 = self.addPlot(title="climb rate plotting")
        self._item2.showGrid(x=True, y=True)
        self._item2.enableAutoRange("y")
        self._item2.setLabel(axis="left", text="y-vario")
        self._item2_data_v = self._item2.plot(self._serial_data._data["v"], pen=self.get_pen(), name="v")

    def get_pen(self):
        data_pen = [
            mkPen(cosmetic=True, width=1.0, color="r"),
            mkPen(cosmetic=True, width=1.0, color="g"),
            mkPen(cosmetic=True, width=1.0, color="b"),
            mkPen(cosmetic=True, width=1.0, color="y"),
        ]
        self._pen_idx += 1
        if self._pen_idx >= len(data_pen):
            self._pen_idx %= len(data_pen)
        return data_pen[self._pen_idx]

    def renew_item(self, state, flag):
        print(flag, state)
        if flag in self._data_flags:
            if state:
                if self._data_item[flag] is None:
                    self._data_item[flag] = self._item1.plot(
                        self._serial_data._data[flag], pen=self.get_pen(), name=flag
                    )
                else:
                    self._item1.addItem(self._data_item[flag])
            else:
                self._item1.removeItem(self._data_item[flag])
        else:
            if state:
                self.nextRow()
                self.addItem(self._item2)
            else:
                self.removeItem(self._item2)

    def start_plot(self):
        self._serial_data.open_serial()

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

    def stop_plot(self):
        self._serial_data.close_serial()
        self._timer.stop()

    def reset_data(self):
        # 定时更新数据，并刷入到图表中
        self._serial_data.refresh_data()
        for flag in self._serial_data._data_flags_extend:
            if flag == "v":
                self._item2_data_v.setData(self._serial_data._data[flag])
            elif self._data_item[flag] is not None:
                self._data_item[flag].setData(self._serial_data._data[flag])
