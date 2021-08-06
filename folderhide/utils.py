import string
from typing import List, Optional, Union, cast
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
import random
from pathlib import Path

random.seed("folderhide")
salt = random.randbytes(16)


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
