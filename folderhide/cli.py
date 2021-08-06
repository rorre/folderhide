import json
import os
import shutil
from pathlib import Path
from typing import List, Tuple

import click

from folderhide.typing import CLIContext
from folderhide.utils import get_all_files, get_crypto, random_str


def error(msg: str):
    click.echo(click.style("[ERR]", fg="red") + " " + msg)


def debug(msg: str):
    click.echo(click.style("[DBG]", fg="blue") + " " + msg)


def info(msg: str):
    click.echo("[INFO] " + msg)


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
@click.pass_context
def hide(ctx: CLIContext, folder: str, password: str):
    files = get_all_files(folder)
    if ctx.obj["debug"]:
        debug("Total files: " + str(len(files)))

    target_dir = Path(random_str(8))
    target_dir.mkdir(exist_ok=True)
    info("Target directory: " + str(target_dir))

    output_datas: List[Tuple[str, str]] = []
    used_strs: List[str] = []

    info("Hiding files")
    with click.progressbar(files) as bar:
        file: str
        for file in bar:
            fname = random_str(16)
            while fname in used_strs:
                fname = random_str(16)

            target_path = target_dir / fname
            shutil.move(file, target_path)
            if ctx.obj["debug"]:
                debug("Move:")
                debug("  - Source: " + file)
                debug("  - Target: " + str(target_path))

            output_datas.append((file, str(target_path)))
            used_strs.append(fname)

    cipher = get_crypto(password)
    if not ctx.obj["debug"]:
        info("Encrypting config")
        text, tag = cipher.encrypt_and_digest(json.dumps(output_datas).encode())
    else:
        text, tag = (json.dumps(output_datas).encode(), "empty16bytesdata".encode())

    info("Writing config")
    with open("cfg.enc", "wb") as f:
        [f.write(x) for x in (cipher.nonce, tag, text)]

    info("Done!")
    info("Config available at: cfg.enc")


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
    with click.progressbar(data) as bar:
        src: str
        dest: str
        for dest, src in bar:
            if ctx.obj["debug"]:
                debug("Move:")
                debug("  - Source: " + src)
                debug("  - Target: " + dest)

            target_path = Path(dest)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(src, dest)

    os.rmdir(src[:8])
    os.remove(config)
    info("Done!")
