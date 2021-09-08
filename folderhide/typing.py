from typing import List, Tuple, TypedDict

from click import Context


class ObjContext(TypedDict):
    debug: bool


class CLIContext(Context):
    obj: ObjContext


MoveData = List[Tuple[str, str]]
