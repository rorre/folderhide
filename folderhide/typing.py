from typing import TypedDict
from click import Context
from typing import List, Tuple


class ObjContext(TypedDict):
    debug: bool


class CLIContext(Context):
    obj: ObjContext


MoveData = List[Tuple[str, str]]
