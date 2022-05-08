from typing import List, Tuple, TypedDict

from click import Context

from folderhide.utils import FileMetadata


class ObjContext(TypedDict):
    debug: bool


class CLIContext(Context):
    obj: ObjContext


MoveData = List[FileMetadata]
