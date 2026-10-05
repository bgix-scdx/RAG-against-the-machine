from .Chunker.ChunkingService import ChunkingService
from .Utils.ArgumentProcessor import Process_Arguments
from typing import Dict, Any, List
from .Chunker.DataModels import UnansweredQuestion, StudentSearchResults
from .Chunker.DataModels import MinimalSearchResults, MinimalSource


def main_func() -> None:
    args = Process_Arguments()
    print(args)
    command = list(args.keys())[0]
    if command == "index":
        index(args[command])
    elif command == "search":
        sources = search(args[command])
        print(f"\nSources for \"{sources.question}\""
              f"[ID: {sources.question_id}]\n")

        for i in sources.retrieved_sources:
            print(f"[{i.score:.1f}] {i.file_path}"
                  f"[{i.first_character_index}:{i.last_character_index}]")
    elif command == "search_dataset":
        search_dataset(args[command])
    elif command == "answer":
        answer(args[command])
    elif command == "answer_dataset":
        answer_dataset(args[command])


def GenerateUQ(question: str, id: str | None = None) -> UnansweredQuestion:
    UQ = UnansweredQuestion(question=question)
    if id:
        UQ.question_id = id
    return UQ


def answer(args: Dict[str, Any]) -> None:
    from .Model.AI import Assistant
    search_data = search(args)
    responce = Assistant().generate_response(search_data)
    print(responce.answer)


def search(args: Dict[str, Any]) -> MinimalSearchResults:
    question, sources_count = GenerateUQ(args["-unamed"]), int(args["-k"])
    sources = ChunkingService().fetch_bm25_results(question, sources_count)
    return sources


def get_text_in_file(datasetsource: Dict[str, Any]) -> str:
    with open(datasetsource["file_path"], "r") as f:
        return f.read()[datasetsource["first_character_index"]:
                        datasetsource["last_character_index"]]


def answer_dataset(args: Dict[str, Any]) -> None:
    import json
    from .Model.AI import Assistant
    datapath, savepath = args.get('-dataset_path'), args.get('-save_directory')
    print(datapath, savepath)
    datasets = []

    if not isinstance(datapath, str):
        raise ValueError

    with open(datapath, "r") as f:
        datasets = json.load(f)["search_results"]
    for i in datasets:
        search = MinimalSearchResults(
            question=i["question"],
            question_id=i["question_id"],
            retrieved_sources=[MinimalSource(
                text_value=get_text_in_file(a),
                first_character_index=a["first_character_index"],
                last_character_index=a["last_character_index"],
                index=0,
                file_path=a["file_path"]
            ) for a in i["retrieved_sources"]]
        )
        print(Assistant().generate_response(search).answer)


def search_dataset(args: Dict[str, Any]) -> StudentSearchResults:
    # –dataset_path <path> –k <int> –save_directory <dir>
    import json
    from time import time
    datapath = args.get('-dataset_path')
    savepath = args.get('-save_directory')
    sources_count = int(args['-k'])

    if not isinstance(datapath, str) or not isinstance(savepath, str):
        raise ValueError

    with open(datapath, "r") as f:
        loaded_data = json.load(f)
    anwsers: List[MinimalSearchResults] = []
    i = 1
    t = time()
    for data in loaded_data['rag_questions']:
        question = GenerateUQ(data["question"], data["question_id"])
        source = ChunkingService().fetch_bm25_results(question, sources_count)
        anwsers.append(source)
        i += 1

    to_dict = {"search_results": [], "k": sources_count}
    questionlist = []
    for msr in anwsers:
        questionlist.append(
            {
                "question": msr.question,
                "question_id": msr.question_id,
                "retrieved_sources": [
                    {"file_path": a.file_path,
                     "first_character_index": a.first_character_index,
                     "last_character_index": a.last_character_index}
                    for a in msr.retrieved_sources]
            }
        )
    to_dict["search_results"] = questionlist
    with open(savepath, 'x') as f:
        f.write(json.dumps(to_dict, indent=1))

    print(f"Finished after {(time() - t)/60:.0f}.{(time() - t) % 60:.0f}"
          "minute")
    return StudentSearchResults(
        search_results=anwsers,
        k=sources_count
    )


def index(args: Dict[str, Any]) -> None:
    cs = args["-max_chunk_size"] if args.get("-max_chunk_size") else 2000
    CS = ChunkingService()
    if CS._LoadRecusive("data/raw"):
        CS._WriteStatus(CS.Position)
        print(f"\033[38;2;0;255;0mChunks of {cs} has fully been"
              "saved under \"data/processed/index.json\".\033[0m")


if __name__ == "__main__":
    main_func()
