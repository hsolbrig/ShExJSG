from typing import Optional, List
from pyjsg.jsglib.logger import FileWithAWriteString


class MemLogger(FileWithAWriteString):
    def __init__(self, prefix: Optional[str] = None):
        self.prefix = prefix if prefix is not None else ""
        self.log = []       # type: List[str]

    def write(self, txt: str) -> None:
        if txt != "\n":
            self.log.append(self.prefix + txt)

    def read(self) -> List[str]:
        return self.log

    def clear(self) -> None:
        self.log = []
