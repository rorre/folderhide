import shutil

from pathlib import Path
from typing import Union
from PyQt5.QtWidgets import QLineEdit
from PyQt5 import QtCore

PathType = Union[str, Path]


def info(msg: str):
    return "[INFO] " + msg


def error(msg: str):
    return "[ERR] " + msg


def debug(msg: str):
    return "[DBG] " + msg


def move_file(src: PathType, dest: PathType):
    target_path = Path(dest)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dest)


class PasswordBar(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setEchoMode(QLineEdit.Password)

    def event(self, e: QtCore.QEvent) -> bool:
        if e.type() == e.HoverEnter:
            self.onHoverEnter(e)
            return True
        elif e.type() == e.HoverLeave:
            self.onHoverLeave(e)
            return True

        return super().event(e)

    def onHoverEnter(self, e: QtCore.QEvent):
        self.setEchoMode(QLineEdit.Normal)

    def onHoverLeave(self, e: QtCore.QEvent):
        self.setEchoMode(QLineEdit.Password)
