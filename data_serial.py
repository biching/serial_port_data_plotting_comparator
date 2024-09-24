from queue import Queue
import os
import sys
import time
import signal
import string
import pyqtgraph as pg
import array
import serial
import numpy as np
import threading
from PySide6.QtCore import QTimer
import serial.tools.list_ports

from enum import Enum


class ConnStatus(Enum):
    CLOSED = 0
    CONNECTED = 1
    LOSE = 2
    CONNECTING = 3


class SerialData:

    def __init__(self, data_flags):
        self._data_flags = data_flags
        self._serial_status = ConnStatus.LOSE
        self._queues = {flag: Queue(maxsize=0) for flag in self._data_flags}

        # 初始化展示数据
        self._data_size = 120
        self._data = {flag: np.zeros(self._data_size) for flag in self._data_flags}

        self.idx = 0

        self.serial_init()

    def serial_init(self):
        self.com = serial.Serial()
        self.portx = "/dev/cu.usbserial-14130"
        self.baudrate = 115200

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)

    def open_serial(self):
        self.com.port = self.portx
        self.com.baudrate = self.baudrate

        print("open serial \nport:", self.portx)
        print("baudrate:", self.baudrate)

        try:
            self.com.open()
        except Exception as e:
            print("open serial error:", e)
            return False
        self._serial_status = ConnStatus.CONNECTED

        try:
            self.serial_thread = threading.Thread(target=self.Serial)
            self.serial_thread.setDaemon(True)
            self.serial_thread.start()
        except Exception as e:
            print("serial thread error:", e)

        # 定时任务，将新数据刷新到图表中
        print("parse time is set:")
        self.timer.start(50)

        return True

    def close_serial(self):
        print("try to close_serial:")
        try:
            self._serial_status = ConnStatus.CLOSED
            self.serial_thread.join()
            print("closed successfully:")
        except Exception as e:
            print("serial thread join error:", e)

        self.timer.stop()
        print("parse time is set:")

        self.com.close()
        print("serial com is closed:")

    def Serial(self):
        ret = b""
        while self._serial_status == ConnStatus.CONNECTED:
            n = self.com.inWaiting()
            if n:
                try:
                    ret = self.com.readline()
                except Exception as e:
                    print("readline error:", e)
                # print(ret)
                if len(ret):
                    try:
                        data_get = ret.decode("UTF-8")
                    except Exception as e:
                        print("decode error:", e)
                        continue
                    data = self.parse_input(data_get)
                    if data is None:
                        print("parse error, data is %s" % data_get)

    def parse_input(self, data):
        if not data.startswith("$"):
            return None
        items = data[1:-2].split(":")
        if len(items) != 2:
            print("fields num is not right")
            return None
        try:
            tag = items[0]
            item = float(items[1])
        except Exception as e:
            print("format error", e)
            return None

        if tag in self._data_flags:
            self._queues[tag].put(item)
        else:
            print("tag error")
            return None

        # print(tag, item)

        return True

    def refresh_data(self):
        for flag in self._data_flags:
            if self.idx < self._data_size:
                self._data[flag][self.idx] = self._queues[flag].get()
                # 将第一个数据赋值给所有位置，以便图表尽早做自适应调整y轴显示范围
                if self.idx == 0:
                    self._data[flag].fill(self._data[flag][self.idx])
                self.idx += 1
            else:
                self._data[flag][:-1] = self._data[flag][1:]
                self._data[flag][self.idx - 1] = self._queues[flag].get()

    def detect_serial_port(self):  # 检测串口
        items = []
        while 1:  # 循环检测串口
            port_list = list(serial.tools.list_ports.comports())
            if len(port_list) > 0:
                for p in port_list:
                    show_str = "{} {} - {}".format(p.device, p.name, p.description)
                    if p.manufacturer:
                        show_str += " - {}".format(p.manufacturer)
                    if p.pid:
                        show_str += " - pid(0x{:04X})".format(p.pid)
                    if p.vid:
                        show_str += " - vid(0x{:04X})".format(p.vid)
                    if p.serial_number:
                        show_str += " - v{}".format(p.serial_number)
                    if p.device.startswith("/dev/cu.Bluetooth-Incoming-Port"):
                        continue
                    items.append(show_str)
                break
            time.sleep(0.5)
        return items
