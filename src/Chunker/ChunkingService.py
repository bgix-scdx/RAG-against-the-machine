from ..Utils.Decorators import service
from ..Utils.AutoJson import AutoJson
from typing import List, Any, Dict
from .DataModels import MinimalSource
from os.path import isdir
from os import listdir, access, W_OK, remove
from ..Utils.PermChecker import PermChecker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from enum import Enum
from json import dumps

class FormatPriority(Enum):
    any = ["\n\t", "\n"]
    py = ["\nclass", "\ndef", "\n"]
    md = ["\n###", "\n##", "\n#", "\n***", "\n\t", "\n"]
    toml = ["\n\n[", "\n[","\n", "\n\t"]


@service
class ChunkingService:
    Chunks: List[MinimalSource] = []
    Position: str = "data/processed/index.json"

    def _LoadRecusive(self, path) -> Any:
        for obj in listdir(path):
            fullpath = path + "/" + obj
            if isdir(fullpath):
                self._LoadRecusive(fullpath)
            elif PermChecker.CanOpenFile(fullpath):
                format = obj.split('.')[1] if len(obj.split('.')) == 2 else " "
                self.Chunks += self.ChunkFile(fullpath, format)

    def ChunkFile(self, path, format) -> List[MinimalSource]:
        content = ""
        offset = 0
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
            start = content.index(txt, offset)
            end = start + len(txt)
            source = MinimalSource(
                file_path=path,
                text_value=txt,
                first_character_index=start,
                last_character_index=end,
                index = len(generated) + 1
            )
            generated.append(source)
            offset = end
        return generated

    def _WriteStatus(self, path: str):
        total = []
        index = 1
        for source in self.Chunks:
            total.append({
                "file_path": source.file_path,
                "text_value": source.text_value,
                "first_character_index": source.first_character_index,
                "last_character_index": source.last_character_index
            })
            index += 1
        if access(path, W_OK):
            remove(path)
        with open(path, "x") as f:
            f.write(AutoJson.to_json(total))

    def __init__(self):
        self._LoadRecusive("vllm-0.10.1")
        self._WriteStatus(self.Position)

    def fetch_bm25_results(self, question: str) -> SyntaxError:
        from bm25s import BM25, tokenize
        import json
        context = ""
        sources = {}
        texted = []

    
        with open(self.Position, "r") as f:
            sources = json.load(f)
            
        for i in sources:
            texted.append(i.get("text_value"))

        retriever = BM25(corpus=texted)
        retriever.index(tokenize(texted)) #  TODO: Add setting

        query = tokenize(question)
        docs, scores = retriever.retrieve(query, k=3)

        index = 1
        for i in docs[0]:
            context += f"\n<context {index}>\n{i}\n</context {index}>"
            index += 1
        
        return context
    