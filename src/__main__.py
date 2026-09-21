from .Threader.ThreadService import ThreadManager
from .Chunker.ChunkingService import ChunkingService
from .Model.AI import Assistant
from threading import current_thread
from time import sleep


if __name__ == "__main__":
    TM = ThreadManager()
# TM.Start(WhileLoop)
    ai = Assistant()
    ChunkingService()
    question = "***What activation formats does the fused batched MoE layer return in vLLM?***"
    print(ChunkingService().fetch_bm25_results(question))
    #sleep(1)
    #TM.Shutdown()
