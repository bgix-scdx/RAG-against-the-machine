from ..Utils.Decorators import service
from ..Utils.AutoJson import AutoJson
from typing import List, Any, Dict
from .DataModels import MinimalSource
from os.path import isdir
from os import listdir, access, W_OK, remove
from ..Utils.PermChecker import PermChecker
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from enum import Enum
from json import dumps

# class FormatPriority(Enum):
#    any = ["\n\t", "\n"]
#    py = ["class", "def", "\n"]
#    md = ["\n###", "\n##", "\n#", "\n***", "\n\t", "\n"]
#    toml = ["\n\n[", "\n[","\n", "\n\t"]

class FormatPriority(Enum):
    any = Language.MARKDOWN
    py = Language.PYTHON
    md = Language.MARKDOWN
    hpp = Language.CPP
    cpp = Language.CPP
    c = Language.C
    h = Language.C

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
    
        textSplitter = RecursiveCharacterTextSplitter.from_language(
            language = priority,
            chunk_size = 2000,  # TODO: ADD SETTING
            chunk_overlap = 0,
            length_function=len,
        )

        chunks = textSplitter.split_text(content)

        for txt in chunks:
            start = 0 #  content.index(txt, offset)
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
        self._LoadRecusive("data/raw")
        self._WriteStatus(self.Position)

    def fetch_bm25_results(self, question: str) -> SyntaxError:
        from bm25s import tokenize
        import bm25s.high_level as BM25
        import json
        context = ""
        sources = {}
        texted = []

    
        with open(self.Position, "r") as f:
            sources = json.load(f)
            
        for i in sources:
            texted.append(i.get("text_value"))

        corpus = BM25.load(self.Position, document_column="text_value")
        retriever = BM25.index(corpus) #  TODO: Add setting

        query = tokenize(question)
        docs = retriever.search([question], k=5)

        index = 1
        for i in docs[0]:
            context += f"{i}\n"
            index += 1

        found_sources = []
        if not self.Chunks:
            self.ChunkFile()


        textsource = [i['document'] for i in docs[0]]

        print(textsource)

        i = 0
        for minisource in self.Chunks:
            if minisource.text_value in textsource:
                found_sources.append(minisource)
        
        return found_sources
    