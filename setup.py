import sys
from cx_Freeze import setup, Executable

import os
os.environ['TCL_LIBRARY'] = "C:\\Users\\jackc\\AppData\\Local\\Programs\\Python\\Python36-32\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Users\\jackc\\AppData\\Local\\Programs\\Python\\Python36-32\\tcl\\tk8.6"


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["datetime", "tkinter", "csv", "ast"],
                     "include_files": [r"C:\Users\jackc\AppData\Local\Programs\Python\Python36-32\DLLs\tcl86t.dll",
                    r"C:\Users\jackc\AppData\Local\Programs\Python\Python36-32\DLLs\tk86t.dll"],
                     "optimize": 2,}

bdist_msi_options = {
    'add_to_path': False,
}


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Timesheet Reformatter",
        version = "1.0",
        description = "Reformats timesheets for state reporting",
        author = "Jack Langston",
        options = {"build_exe": build_exe_options,
                    "install_exe": {
                        "force": True,
                    },
                    "bdist_msi": bdist_msi_options
                   },
        executables = [Executable("TimesheetFormatter.py",
                                  base=base,
                                  shortcutName="TimeSheet Formatter",
                                  shortcutDir="DesktopFolder",
                                  icon="ico.ico")])