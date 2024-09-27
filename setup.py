import sys
from cx_Freeze import setup, Executable

setup(
    name="SerialPortPlotter",
    version="0.1",
    description="Plot data from Serial Port",
    executables=[Executable("main.py", base="gui")],
)
