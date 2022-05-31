from PyQt5.QtCore import QThread, pyqtSignal
from folderhide.core import hide as hide_core, unhide as unhide_core
from folderhide.gui.utils import info, error, debug


class HideThread(QThread):
    _progress = 0
    progress = pyqtSignal(int)
    total = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(
        self, targetFolder: str, password: str, configPath: str, *args, **kwargs
    ):
        self._targetFolder = targetFolder
        self._password = password
        self._configPath = configPath
        super().__init__(*args, **kwargs)

    def on_info(self, msg: str):
        self.log.emit(info(msg))

    def on_error(self, msg: str):
        self.log.emit(error(msg))

    def on_debug(self, msg: str):
        self.log.emit(debug(msg))

    def run(self):
        hide_core(
            self._targetFolder,
            self._password,
            self._configPath,
            self.on_info,
            self.on_debug,
            self.on_error,
        )


class UnhideThread(QThread):
    _progress = 0
    progress = pyqtSignal(int)
    total = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, configFile: str, password: str, *args, **kwargs):
        self._configFile = configFile
        self._password = password
        super().__init__(*args, **kwargs)

    def on_info(self, msg: str):
        self.log.emit(info(msg))

    def on_error(self, msg: str):
        self.log.emit(error(msg))

    def on_debug(self, msg: str):
        self.log.emit(debug(msg))

    def run(self):
        unhide_core(
            self._password, self._configFile, self.on_info, self.on_error, self.on_debug
        )
