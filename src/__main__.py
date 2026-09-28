from .Threader.ThreadService import ThreadManager
from .Chunker.ChunkingService import ChunkingService
from .Utils.ArgumentProcessor import Process_Arguments, ArgumentError
from .Model.AI import Assistant
from threading import current_thread
from time import sleep
import json
from time import time
from math import floor

def main_func() -> None:
    TM = ThreadManager()
    args = {}
    command = ""

    args = Process_Arguments()

    if not args or not len(args.keys()) > 0:
        return None

    command = list(args.keys())[0]

    if command == "index":
        print("Indexing raw files.")
        t = time()
        ChunkingService()
        total = floor((time() - t)*100)/100
        print(f"Indexing finished in {total}s")
    elif command == "search":
        question, number = args[command].get("-unamed"), args[command].get("-k")
        result = ChunkingService().fetch_bm25_results(question)
        for i in result:
            print(f"{i.file_path} [{i.first_character_index}:{i.last_character_index}]")
    elif command == "answer":
        question, number = args[command].get("-unamed"), args[command].get("-k")
        result = ChunkingService().fetch_bm25_results(question)
    

        print(Assistant().generate_response(question).answer)
        print("\n<<USING SOURCES>>\n")
        for i in result:
            print(f"{i.file_path} [{i.first_character_index}:{i.last_character_index}]")

if __name__ == "__main__":
    main_func()