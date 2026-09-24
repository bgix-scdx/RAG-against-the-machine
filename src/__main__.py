from .Threader.ThreadService import ThreadManager
from .Chunker.ChunkingService import ChunkingService
from .Utils.ArgumentProcessor import Process_Arguments, ArgumentError
from .Model.AI import Assistant
from threading import current_thread
from time import sleep
import json

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
    print(args)

    command = list(args.keys())[0]

    if command == "index":
        ChunkingService()
