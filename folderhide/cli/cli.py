import click

from folderhide.core import hide as hide_core
from folderhide.core import unhide as unhide_core
from folderhide.cli.utils import debug, error, info
from folderhide.typing import CLIContext
from tqdm import tqdm

pbar = None


def on_progress(current: int, total: int):
    global pbar
    if pbar is None:
        pbar = tqdm(total=total)

    pbar.update(current)


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
    def on_debug(x: str):
        if ctx.obj["debug"]:
            debug(x)

    print(folder)
    hide_core(folder, password, output, info, on_debug, error, on_progress)


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
    def on_debug(x: str):
        if ctx.obj["debug"]:
            debug(x)

    unhide_core(password, config, info, on_debug, error, on_progress)
