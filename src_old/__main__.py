from src.Chunker.ChunkerClass import Chunker

chunk = Chunker()
if chunk.ChunkInit():
    chunk.ChunkFileInit("vllm-0.10.1")
