import sys
from pathlib import Path
from cx_Freeze import setup, Executable

icon_path = Path('favicon.ico')

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [Executable("CountBoard.py", base=base, icon=str(icon_path))]

include_files = [
    'favicon.ico',
    'del.ico',
    'edit.ico',
    'exit.ico',
    'github.ico',
    'help.ico',
    'home.ico',
    'recovery.ico',
    'update.ico',
    'introduction.md'
]

options = {
    'build_exe': {
        'include_files': [f for f in include_files if Path(f).exists()],
        'packages': [
            'os',
            'sys',
            'win32api',
            'win32gui',
            'win32con',
            'apscheduler',
            'sqlitedict',
            'pywin10',
            'ttkbootstrap',
            'markdown2',
            'tkhtmlview',
            'requests',
            'PIL'
        ],
        'excludes': [
            'unittest',
            'pydoc',
            'pdb',
            'test'
        ]
    }
}

setup(
    name="CountBoard",
    version="1.3.0.5",
    description="CountBoard 是一个基于 Tkinter 开源的桌面日程倒计时应用。",
    executables=executables,
    options=options
)