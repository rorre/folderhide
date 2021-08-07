import shutil

from pathlib import Path
from typing import Union

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
