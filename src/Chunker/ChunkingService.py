from ..Utils.Decorators import service
from ..Utils.AutoJson import AutoJson
from typing import List, Any
from .DataModels import MinimalSource, UnansweredQuestion, MinimalSearchResults
from os.path import isdir, isfile
from os import listdir, access, W_OK, remove
from ..Utils.PermChecker import PermChecker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from enum import Enum
from tqdm import tqdm  # type: ignore[import-untyped]


class FormatPriority(Enum):
    """Used to class files chunking priority.\n
    The key being the format of the file,
    The value used as a list of separators."""
    any = ["\n\n", "\n", " ", ""]
    py = ["\nclass", "def", "\n", "\n", " ", ""]
    md = ["\n#", "\n##", "\n###", "\n####", "\n\n", "\n", " ", ""]
    toml = ["\n\n[", "\n[", "\n\n", "\n", " ", ""]


@service
class ChunkingService:
    """
    Used to Chunk and save the chunk or load an existing chunk data.
    """
    Chunks: List[MinimalSource] = []
    Paths: List[str] = []
    Position: str = "data/processed/index.json"
    Token: Any = None

    def _LoadRecusive(self, path: str) -> None:
        """
        Enter a file and call ChunkFile() for each valid files.\n
        If an other directory is found, it enters inside and call it self.
        """
        for obj in listdir(path):
            fullpath = path + "/" + obj
            if isdir(fullpath):
                self._LoadRecusive(fullpath)
            elif PermChecker.CanOpenFile(fullpath):
                self.Paths += [fullpath]

    def Index(self, path: str) -> bool:
        self._LoadRecusive(path)
        for p in tqdm(self.Paths):
            fileformat = p.split('.')[1] if len(p.split('.')) == 2 else " "
            self.Chunks += self.ChunkFile(p, fileformat)
        return True

    def ChunkFile(self, path: str, format: str) -> List[MinimalSource]:
        """
        Chunk a a valid file and return minimal sources.
        """
        content = ""
        offset = 0
        generated: List[MinimalSource] = []
        priority = (getattr(FormatPriority, format).value if
                    hasattr(FormatPriority, format) else
                    getattr(FormatPriority, "any").value)
        try:
            with open(path) as f:
                content = f.read()
        except UnicodeDecodeError:
            return generated

        textSplitter = RecursiveCharacterTextSplitter(
            separators=priority,
            chunk_size=2000,  # TODO: ADD SETTING
            chunk_overlap=0,
            is_separator_regex=False,
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
            )
            generated.append(source)
            offset = end
        return generated

    def _WriteStatus(self, path: str) -> None:
        """
        Will write the saved chunk in the target file when called.
        Does nothing is self.Chunks is empty.
        """
        total = []

        for i in self.Chunks:
            total.append({"file_path": i.file_path,
                          "text_value": i.text_value,
                          "first_character_index": i.first_character_index,
                          "last_character_index": i.last_character_index})

        if access(path, W_OK):
            remove(path)
        if isfile(path):
            remove(path)
        with open(path, "x") as f:
            f.write(AutoJson.to_json(total))

    def fetch_bm25_results(self, UQ: UnansweredQuestion,
                           source_count: int = 5) -> MinimalSearchResults:
        """
        Fetch the sources of an Unansered question, with by default 5 sources.
        put the result in a MinimalSearchResults and returns it.
        """
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
        if not self.Token:
            self.Token = BM25.index(corpus)  # TODO: Add setting
        docs = self.Token.search([UQ.question], k=source_count)
        index = 1
        for i in docs[0]:
            context += f"{i}\n"
            index += 1
        found_sources: List[MinimalSource] = []
        i = 0

        for i in docs[0]:
            indoc = sources[i['id']]
            source = MinimalSource(
                file_path=indoc['file_path'],
                text_value=indoc['text_value'],
                first_character_index=indoc['first_character_index'],
                last_character_index=indoc['last_character_index'],
                score=i['score'],
            )
            found_sources.append(source)

        return MinimalSearchResults(
            question=UQ.question,
            question_id=UQ.question_id,
            retrieved_sources=found_sources
        )





class Collision:

    def Event() -> None:
        pass


@service
class CollisionService:
    collision_list = []

    def New(Name, Func) -> Collision:
        col = Collision(Name, Func)
        self.collission_list.append(col)

    def TouchBound(isnt1, inst2) -> None:
        if inst2 in isnt1:
            




class Instance:
    Collision