import json
import os
import sys
from pathlib import Path
import traceback
from typing import List, Tuple

import click

from folderhide.typing import CLIContext
from folderhide.utils import get_all_files, get_crypto, random_str
from folderhide.cli.utils import (
    info,
    debug,
    error,
    revert_hide,
    revert_unhide,
    move_file,
)


@click.group()
@click.option("--debug", "dbg", default=False, is_flag=True)
@click.pass_context
def cli(ctx: CLIContext, dbg: bool):
    ctx.ensure_object(dict)
    ctx.obj["debug"] = dbg
    if dbg:
        debug("Debug is turned on.")


@cli.command(name="hide", help="Hide the folder.")
@click.argument(
    "folder",
    type=click.Path(
        exists=True,
        file_okay=False,
        dir_okay=True,
    ),
)
@click.argument("password")
@click.option(
    "--output-file",
    "-o",
    "output",
    default="cfg.enc",
    help="The output data path. This file tells the program how to unhide your folder.",
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
    ),
)
@click.pass_context
def hide(ctx: CLIContext, folder: str, password: str, output: str):
    files = get_all_files(folder)
    if ctx.obj["debug"]:
        debug("Total files: " + str(len(files)))

    target_dir = Path("." + random_str(8))
    target_dir.mkdir(exist_ok=True)
    info("Target directory: " + str(target_dir))

    if sys.platform == "win32":
        import ctypes

        info("WIN: Marking folder as hidden")
        ctypes.windll.kernel32.SetFileAttributesW(str(target_dir.resolve()), 0x2)

    output_datas: List[Tuple[str, str]] = []
    used_strs: List[str] = []

    info("Hiding files")
    try:
        with click.progressbar(files) as bar:
            src: str
            for src in bar:
                fname = random_str(16)
                while fname in used_strs:
                    fname = random_str(16)

                dest = target_dir / fname
                move_file(src, dest, ctx.obj["debug"])

                output_datas.append((src, str(dest)))
                used_strs.append(fname)
    except Exception:
        error("An exception has occured.")
        traceback.print_exc()
        revert_hide(output_datas, ctx.obj["debug"])
        return

    cipher = get_crypto(password)
    if not ctx.obj["debug"]:
        info("Encrypting config")
        text, tag = cipher.encrypt_and_digest(json.dumps(output_datas).encode())
    else:
        text, tag = (json.dumps(output_datas).encode(), "empty16bytesdata".encode())

    info("Writing config")
    with open(output, "wb") as f:
        [f.write(x) for x in (cipher.nonce, tag, text)]

    info("Done!")
    info("Config available at: " + output)
    info("Hidden folder: " + str(target_dir))
    info("Please keep this file safe. This file is important for the unhide process.")
    info("The file also needs to be in the same directory as the folder.")


@cli.command(name="unhide", help="Unhide the folder from config.")
@click.argument("password")
@click.option(
    "--config",
    "-c",
    help="Config to load from.",
    default="cfg.enc",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
)
@click.pass_context
def unhide(ctx: CLIContext, password: str, config: str):
    info("Loading config")
    with open(config, "rb") as f:
        nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]
    cipher = get_crypto(password, nonce=nonce)

    if not ctx.obj["debug"]:
        try:
            info("Decrypting config")
            text_data = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            error("Wrong config password!")
    else:
        text_data = ciphertext

    info("Loading config")
    data: List[Tuple[str, str]] = json.loads(text_data.decode())

    info("Unhiding files")
    try:
        with click.progressbar(data) as bar:
            src: str
            dest: str
            for dest, src in bar:
                move_file(src, dest, ctx.obj["debug"])
    except Exception:
        error("An error has occured.")
        traceback.print_exc()
        revert_unhide(data, ctx.obj["debug"])
        return

    os.rmdir(src[:9])
    os.remove(config)
    info("Done!")
