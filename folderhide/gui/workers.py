import json
import os
import sys
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal

from folderhide.gui.utils import info, move_file
from folderhide.typing import MoveData
from folderhide.utils import generate_config, get_all_files, get_crypto, random_str


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

    def run(self):
        self.log.emit(info("Getting all files"))
        files = get_all_files(self._targetFolder)
        self.total.emit(len(files))

        target_dir = Path("." + random_str(8))
        target_dir.mkdir(exist_ok=True)
        self.log.emit(info("Target directory: " + str(target_dir)))

        if sys.platform == "win32":
            import ctypes

            self.log.emit(info("WIN: Marking folder as hidden"))
            ctypes.windll.kernel32.SetFileAttributesW(str(target_dir.resolve()), 0x2)

        self.log.emit(info("Generating paths"))
        output_datas = generate_config(files, target_dir)

        self.log.emit(info("Encypting config"))
        cipher = get_crypto(self._password)
        text, tag = cipher.encrypt_and_digest(json.dumps(output_datas).encode())

        self.log.emit(info("Writing config"))
        with open(self._configPath, "wb") as f:
            [f.write(x) for x in (cipher.nonce, tag, text)]

        self.log.emit(info("Hiding files"))
        for cfg in output_datas:
            move_file(cfg.original, cfg.modified)

            self._progress += 1
            self.progress.emit(self._progress)

        self.log.emit(info("Done!"))
        self.log.emit(info("Config available at: " + self._configPath))
        self.log.emit(info("Hidden folder: " + str(target_dir)))
        self.log.emit(
            info(
                "Please keep this file safe. This file is important for the unhide process."
            )
        )
        self.log.emit(
            info("The file also needs to be in the same directory as the folder.")
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

    def run(self):
        self.log.emit(info("Reading config"))
        with open(self._configFile, "rb") as f:
            nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]

        self.log.emit(info("Decrypting config"))
        cipher = get_crypto(self._password, nonce=nonce)
        text_data = cipher.decrypt_and_verify(ciphertext, tag)

        self.log.emit(info("Loading config"))
        data: MoveData = json.loads(text_data.decode())
        self.total.emit(len(data))

        self.log.emit(info("Unhiding files"))
        for dest, src in data:
            move_file(src, dest)
            self._progress += 1
            self.progress.emit(self._progress)

        if src:
            os.rmdir(src[:9])
            os.remove(self._configFile)

        self.log.emit(info("Done!"))
