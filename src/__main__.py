from .Threader.ThreadService import ThreadManager
from .Chunker.ChunkingService import ChunkingService
from .Utils.ArgumentProcessor import Process_Arguments
from .Model.AI import Assistant
from threading import current_thread
from time import sleep
import json

if __name__ == "__main__":
    TM = ThreadManager()
# TM.Start(WhileLoop)
    #ai = Assistant()
    args = json.dumps(Process_Arguments(), indent=4)
    #ChunkingService()
    #question = "What activation formats does the fused batched MoE layer return in vLLhttps://profile-v3.intra.42.fr/M?"
    #print(ai.generate_response(question))
    #print(ChunkingService().fetch_bm25_results(question))
    #sleep(1)
    #TM.Shutdown()
