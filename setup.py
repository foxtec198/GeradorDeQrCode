import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages":[
        "os","time"
    ],
    "includes":[
        "sqlite3",
        "PyQt5",
        "pyodbc",
        "segno",
        "PIL",
        "PyPDF2",
        "reportlab",
        "qdarktheme",
        "webbrowser",
    ],
    "include_files":[
        "resources"
    ]
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    
setup(
    name = 'Gerador de QR Code',
    version = '1.5',
    description = 'Gera QR Codes para utilizacao',
    options = {"build_exe":build_exe_options},
    executables = [Executable(
        'main.py', 
        icon='resources/scr/icon.ico', 
        base=base
        )
                   ]
)