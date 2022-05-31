import json
import os
import sys
import traceback
from pathlib import Path
from typing import Callable

from folderhide.typing import MoveData
from folderhide.utils import (
    FileMetadata,
    generate_config,
    get_all_files,
    get_crypto,
    move_file,
    random_str,
)

LogFunction = Callable[[str], None]


def hide(
    folder: str,
    password: str,
    output: str,
    info_func: LogFunction,
    debug_func: LogFunction,
    error_func: LogFunction,
    progress_func: Callable[[int, int], None],
):
    base_folder = Path(folder).parent
    files = get_all_files(folder, base_folder)
    debug_func("Total files: " + str(len(files)))

    target_dir = Path("." + random_str(8))
    info_func("Target directory: " + str(target_dir))

    if sys.platform == "win32":
        import ctypes

        info_func("WIN: Marking folder as hidden")
        ctypes.windll.kernel32.SetFileAttributesW(str(target_dir.resolve()), 0x2)

    info_func("Generating paths")
    output_datas = generate_config(files, target_dir)

    cipher = get_crypto(password)
    info_func("Encrypting config")
    text, tag = cipher.encrypt_and_digest(json.dumps(output_datas).encode())

    info_func("Writing config")
    with open(output, "wb") as f:
        [f.write(x) for x in (cipher.nonce, tag, text)]

    info_func("Hiding files")
    output_folder = Path(output).parent
    (output_folder / target_dir).mkdir(parents=True, exist_ok=True)

    try:
        total_length = len(output_datas)
        for i, cfg in enumerate(output_datas):
            move_file(base_folder / cfg.original, output_folder / cfg.modified)
            progress_func(i, total_length)

    except Exception:
        error_func("An exception has occured.")
        traceback.print_exc()
        return

    info_func("Done!")
    info_func("Config available at: " + output)
    info_func("Hidden folder: " + str(target_dir))
    info_func(
        "Please keep this file safe. This file is important for the unhide process."
    )
    info_func("The file also needs to be in the same directory as the folder.")


def unhide(
    password: str,
    config: str,
    info_func: LogFunction,
    debug_func: LogFunction,
    error_func: LogFunction,
    progress_func: Callable[[int, int], None],
):
    info_func("Reading config")
    with open(config, "rb") as f:
        nonce, tag, ciphertext = [f.read(x) for x in (16, 16, -1)]
    cipher = get_crypto(password, nonce=nonce)

    try:
        info_func("Decrypting config")
        text_data = cipher.decrypt_and_verify(ciphertext, tag)
    except ValueError:
        error_func("Wrong config password!")
        return

    info_func("Loading config")
    data: MoveData = json.loads(text_data.decode())

    info_func("Unhiding files")
    config_folder = Path(config).parent

    try:
        total_length = len(data)
        for i, cfg in enumerate(data):
            cfg = FileMetadata(*cfg)
            move_file(config_folder / cfg.modified, config_folder / cfg.original)
            progress_func(i, total_length)

    except Exception:
        error_func("An error has occured.")
        traceback.print_exc()
        return

    os.remove(config)
    info_func("Done!")
