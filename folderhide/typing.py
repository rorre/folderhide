from typing import TypedDict
from click import Context


class ObjContext(TypedDict):
    debug: bool


class CLIContext(Context):
    obj: ObjContext
