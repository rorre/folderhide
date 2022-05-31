import random
import string
import shutil
from pathlib import Path
from typing import List, Optional, Union, cast, NamedTuple

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt

random.seed("folderhide")
salt = random.randbytes(16)


PathType = Union[str, Path]


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


def get_all_files(dir: PathType, base_path: PathType):
    if isinstance(dir, str):
        working_dir = Path(dir)
    else:
        working_dir = dir

    files: List[str] = []
    for d in working_dir.iterdir():
        if d.is_dir():
            files.extend(get_all_files(d, base_path))
        else:
            files.append(str(d.relative_to(base_path)))

    return files


def random_str(N: int = 8):
    return "".join(
        random.SystemRandom().choice(
            string.ascii_uppercase + string.ascii_lowercase + string.digits
        )
        for _ in range(N)
    )


def generate_config(files: List[str], target_dir: Path):
    output_datas: List[FileMetadata] = []
    used_strs: List[str] = []

    for src in files:
        new_fname = random_str(16)
        while new_fname in used_strs:
            new_fname = random_str(16)

        new_path = target_dir / new_fname
        output_datas.append(FileMetadata(src, str(new_path)))
        used_strs.append(new_fname)

    return output_datas


def move_file(src: PathType, dest: PathType):
    target_path = Path(dest)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src, dest)
