import shutil
from pathlib import Path
from typing import List, Union

import click

from folderhide.utils import FileMetadata

PathType = Union[str, Path]


def error(msg: str):
    click.echo(click.style("[ERR]", fg="red") + " " + msg)


def debug(msg: str):
    click.echo(click.style("[DBG]", fg="blue") + " " + msg)


def info(msg: str):
    click.echo("[INFO] " + msg)


def move_file(src: PathType, dest: PathType, dbg: bool):
    if dbg:
        debug("Move:")
        debug("  - Source: " + str(src))
        debug("  - Target: " + str(dest))

    target_path = Path(dest)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dest)


def revert(datas: List[FileMetadata], dbg: bool = False):
    info("Reverting files")
    for dest, src in datas:
        move_file(src, dest, dbg)
