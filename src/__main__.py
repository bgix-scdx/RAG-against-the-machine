from .Chunker.ChunkingService import ChunkingService
from .Utils.ArgumentProcessor import Process_Arguments, ArgumentError
from threading import current_thread
from time import sleep
from typing import Dict, Any, List
from .Chunker.DataModels import UnansweredQuestion, StudentSearchResults, MinimalSearchResults
from time import time
from math import floor

def main_func() -> None:
    args = Process_Arguments()
    command = list(args.keys())[0]
    if command == "index":
        index(args[command])
    elif command == "search":
        search(args[command])
    elif command == "search_dataset":
        search_dataset(args[command])

def GenerateUQ(question: str, id: str | None = None) -> UnansweredQuestion:
    UQ = UnansweredQuestion(question=question)
    if id:
        UQ.question_id = id
    return UQ

def search(args: Dict[str, Dict[str, Any]]) -> None:
    question, sources_count = GenerateUQ(args.get("-unamed")), args.get("-k")
    sources = ChunkingService().fetch_bm25_results(question, sources_count)

    print(f"\nSources for \"{sources.question}\" [ID: {sources.question_id}]\n")

    for i in sources.retrieved_sources:
        print(f"[{i.score:.1f}] {i.file_path} [{i.first_character_index}:{i.last_character_index}]")

def search_dataset(args: Dict[str, Dict[str, Any]]) -> StudentSearchResults:
    # –dataset_path <path> –k <int> –save_directory <dir>
    import json
    from time import time
    datapath, savepath, sources_count = args.get('-dataset_path'), args.get('-save_directory'), args.get('-k')

    with open(datapath, "r") as f:
        loaded_data = json.load(f)
    anwsers: List[MinimalSearchResults] = []
    i = 1
    t = time()
    for data in loaded_data['rag_questions']:
        question = GenerateUQ(data["question"], data["question_id"])
        source = ChunkingService().fetch_bm25_results(question)
        anwsers.append(source)
        print(f"{(i / len(loaded_data['rag_questions'])) * 100:.0f}%")
        i += 1    

    to_dict = {"search_results":[], "k": sources_count}
    for i in anwsers:
        to_dict["search_results"].append(
            {
                "question": i.question,
                "question_id": i.question_id,
                "retrieved_sources": [{"file_path":a.file_path, "first_character_index":a.first_character_index, "last_character_index":a.last_character_index} for a in i.retrieved_sources]
            }
        )

    with open(savepath, "x") as f:
        f.write(json.dumps(to_dict, indent=1))


    print(f"Finished after {(time() - t)/60:.0f}.{(time() - t) % 60:.0f} minute")
    return StudentSearchResults(
        search_results = anwsers,
        k = sources_count
    )


def index(args: Dict[str, Dict[str, Any]]) -> None:
    chunk_size = args["-max_chunk_size"] if args.get("-max_chunk_size") else 2000
    CS = ChunkingService()
    if CS._LoadRecusive("data/raw"):
        CS._WriteStatus(CS.Position)
        print(f"\033[38;2;0;255;0mChunks of {chunk_size} has fully been saved under \"data/processed/index.json\".\033[0m")
    

if __name__ == "__main__":
    main_func()