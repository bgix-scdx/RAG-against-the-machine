from ..DataModels.DataModel import MinimalSource
from ..Printer.PrinterClass import Printer
from enum import Enum
from typing import Dict, Any, List
from sys import argv
from os import listdir, access, W_OK
from os.path import isdir
from math import floor
from time import sleep, time
from .JsonTraductor import JsonTraductor
import json


def ChunkPython(file) -> Any:
    pass


def ChunkMarkdown(file) -> Any:
    pass


def ChunkAny(text: str, path: str) -> MinimalSource:
    maxlength = 2000
    file_sources = []
    slice_size = 50
    anchor = len(text)
    index = anchor

    while index >= 0:
        if anchor - index >= 2000:
            newsource = MinimalSource(file_path=path,
                                      first_character_index=index,
                                      last_character_index=anchor)
            file_sources.append(newsource)
            anchor = index
        index -= slice_size
        if index <= 0:
            newsource = MinimalSource(file_path=path,
                                      first_character_index=index,
                                      last_character_index=anchor)
            file_sources.append(newsource)
            break
    return file_sources


class FileToFunc(Enum):
    py = ChunkPython
    md = ChunkMarkdown


def GetSettings(file: str) -> Any:  # TODO: Move it to dedicated file
    try:
        with open(file, "r") as p:
            return json.load(p)
    except FileNotFoundError:
        Printer.Error(f"Setting file {file}, could not be found.")
    except json.decoder.JSONDecodeError:
        Printer.Error(f"Setting file {file}, Invalid Json Format.")


class Chunker:
    settings_path: str = "src/Settings/Chunker.json"
    settings: Dict[str, str | int] | None = GetSettings(settings_path)

    def ChunkInit(self) -> bool:
        if not self.settings or not self.settings.get("chunksize"):
            return False
        if len(argv) >= 2 and argv[1] == "--max_chunk_size" and int(argv[2]):
            maxval = int(argv[2])
            if maxval != self.settings["chunksize"]:
                Printer.Warn(f" - Changing max chunk size to {maxval}")
                self.settings["chunksize"] = maxval
        csize = self.settings.get("chunksize")
        if not csize or not isinstance(csize, int) or csize > 2000:
            Printer.Error("Chunk size can not be above 2000.")
            return False
        return True

    def ChunkFileInit(self, path: str) -> List[MinimalSource]:
        '''Will chunk the files according to what file they are'''
        AllFiles: List[str] = self.ChunkFileRecCount(path)
        Chunks = self.ChunkFileRecChunk(AllFiles)
        with open("logs.json", "x+") as f:
            JsonTraductor.write(f, Chunks)
        return Chunks

    def ChunkFileRecCount(self, path) -> List[str]:
        localcount = []
        if isdir(path):
            for _, file in enumerate(listdir(path)):
                localcount += self.ChunkFileRecCount(path+"/"+file)
        elif self.ChunkValidateFile(path):
            localcount += [path]
        return localcount

    def ChunkFileRecChunk(self, filesPathList: List[str]) -> List[MinimalSource]:
        starting_time: float = time()
        current_count: int = 0
        total_count: int = len(filesPathList)
        chunks = []
        for path in filesPathList:
            print("\033[A\33[2K\r", end="")
            self.DisplayLoadingBar()
            print(f" [{current_count} | {total_count}]")
            chunks = self.ChunkFileCheck(path)
            current_count += 1
        print("\033[A\33[2K\r", end="")
        print(f"Completed chunking in {floor(time() - starting_time)} seconds.")
        return chunks

    def ChunkFileCheck(self, path: str, chunks: List[MinimalSource] = []) -> Any:
        file_name = path.split("/")[len(path.split("/"))-1]
        file_type = file_name.split(".")[len(file_name.split(".")) - 1]
        try:
            with open(path, "r") as f:
                if hasattr(FileToFunc, file_type):
                    pass
                else:
                    chunks += ChunkAny(f.read()[::-1], path)
        except UnicodeDecodeError:
            return chunks
        return chunks

    @staticmethod
    def ChunkValidateFile(path) -> bool:
        "Used to Validate if the file is a valid file to be chunked, returns True if it is valid, False otherwise."
        try:
            with open(path, "r"):
                pass
        except FileNotFoundError:
            return False
        except PermissionError:
            return False
        except IsADirectoryError:
            return False
        return True

    @staticmethod
    def DisplayLoadingBar() -> None:  # TODO: Move it to a utils folder
        from ..Enums.LoadingAnimeEnum import LoadingAnimation
        speed: float = 8
        loadingbar = LoadingAnimation.Default.value
        print(loadingbar[floor(time() * speed) % len(loadingbar)], end="")
