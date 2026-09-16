from ..Utils.Decorators import service
from typing import List, Any
from .DataModels import MinimalSource
from os.path import isdir
from os import listdir, access, W_OK
from ..Utils.PermChecker import PermChecker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from enum import Enum


class FormatPriority(Enum):
    any = ["\n\t", "\n", " "]
    py = ["\nclass", "\ndef", "\n"]
    md = ["\n###", "\n##", "\n#", "\n***", "\n\t", "\n"]


@service
class ChunkingService:
    Chunks: List[MinimalSource]

    def _LoadRecusive(self, path) -> Any:
        for obj in listdir(path):
            fullpath = path + "/" + obj
            if isdir(fullpath):
                self._LoadRecusive(fullpath)
            elif PermChecker.CanOpenFile(fullpath):
                format = obj.split('.')[1] if len(obj.split('.')) == 2 else " "
                self.ChunkFile(fullpath, format)

    def ChunkFile(self, path, format) -> List[MinimalSource]:
        content = ""
        generated = []
        priority = (getattr(FormatPriority, format).value if
                    hasattr(FormatPriority, format) else
                    getattr(FormatPriority, "any").value)
        indexerSize = 10  # TODO: add setting
        try:
            with open(path) as f:
                content = f.read()
        except UnicodeDecodeError:
            return generated
        textSplitter = RecursiveCharacterTextSplitter(
            separators = priority,
            chunk_size = 2000,  # TODO: ADD SETTING
            chunk_overlap = 0,
        )

        chunks = textSplitter.split_text(content)

        for txt in chunks:
            source = MinimalSource()
            source.text_value = txt

            print(txt)
        

    @staticmethod
    def _CheckStatus():
        pass

    def __init__(self):
        self._LoadRecusive("vllm-0.10.1")
