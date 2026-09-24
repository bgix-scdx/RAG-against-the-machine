from .Threader.ThreadService import ThreadManager
from .Chunker.ChunkingService import ChunkingService
from .Utils.ArgumentProcessor import Process_Arguments, ArgumentError
from .Model.AI import Assistant
from threading import current_thread
from time import sleep
import json
from time import time
from math import floor

if __name__ == "__main__":
    TM = ThreadManager()
    args = {}
    command = ""
    try:
        args = Process_Arguments()
    except ArgumentError as e:
        print(f"\033[38;2;255mError while parsing arguments: {e}\033[0m")

    if not len(args.keys()) > 0:
        print(f"\033[38;2;255mNo arguments provided.\033[0m")

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
    

        print(Assistant().generate_response(question))
        print("\n<<USING SOURCES>>\n")
        for i in result:
            print(f"{i.file_path} [{i.first_character_index}:{i.last_character_index}]")