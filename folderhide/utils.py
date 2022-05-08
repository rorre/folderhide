import random
import string
from pathlib import Path
from typing import List, Optional, Union, cast, NamedTuple

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt

random.seed("folderhide")
salt = random.randbytes(16)


class FileMetadata(NamedTuple):
    original: str
    modified: str


def get_crypto(password: str, nonce: Optional[bytes] = None):
    key = cast(bytes, scrypt(password, salt, 16, N=2 ** 14, r=8, p=1))  # type: ignore
    if nonce:
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    else:
        cipher = AES.new(key, AES.MODE_EAX)

    return cipher


def get_all_files(dir: Union[str, Path]):
    if isinstance(dir, str):
        working_dir = Path(dir)
    else:
        working_dir = dir

    files: List[str] = []
    for d in working_dir.iterdir():
        if d.is_dir():
            files.extend(get_all_files(d))
        else:
            files.append(str(d))

    return files


def random_str(N: int = 8):
    return "".join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits
        )
        for _ in range(N)
    )


def generate_config(files: List[str]):
    output_datas: List[FileMetadata] = []
    used_strs: List[str] = []

    for src in files:
        new_fname = random_str(16)
        while new_fname in used_strs:
            new_fname = random_str(16)

        output_datas.append(FileMetadata(src, new_fname))
        used_strs.append(new_fname)

    return output_datas
