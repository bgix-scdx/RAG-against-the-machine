from .Threader.ThreadService import ThreadManager
from .Chunker.ChunkingService import ChunkingService
from threading import current_thread
from time import sleep


def WhileLoop():
    currentThread = current_thread()
    print(currentThread.stop_event)
    while not currentThread.stop_event.is_set():
        print(currentThread.stop_event)
        pass
    print("yes")


if __name__ == "__main__":
    TM = ThreadManager()
# TM.Start(WhileLoop)
    ChunkingService()
    sleep(1)
    TM.Shutdown()
