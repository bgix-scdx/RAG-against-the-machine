from tqdm import tqdm  # type: ignore[import-untyped, unused-ignore]
from .Chunker.ChunkingService import ChunkingService
from .Utils.ArgumentProcessor import Process_Arguments
from .Utils.PermChecker import PermChecker
from typing import Dict, Any, List
from .Chunker.DataModels import UnansweredQuestion, StudentSearchResults
from .Chunker.DataModels import MinimalSearchResults, MinimalSource
from .Chunker.DataModels import AnsweredQuestion
from .Utils.Decorators import secure
from os.path import isfile, isdir
from os import remove


@secure(KeyboardInterrupt)
def main_func() -> None:
    """Process the arguments and call the apropriate function."""
    args = Process_Arguments()
    if not args:
        return
    command = list(args.keys())[0]
    match command:
        case "index":
            index(args[command])
        case "search":
            sources = search(args[command])
            print(f"\nSources for \"{sources.question}\""
                  f"[ID: {sources.question_id}]\n")
            for i in sources.retrieved_sources:
                print(f"[{i.score:.1f}] {i.file_path}"
                      f"[{i.first_character_index}:{i.last_character_index}]")
        case "search_dataset":
            search_dataset(args[command])
        case "answer":
            answer(args[command])
        case "answer_dataset":
            answer_dataset(args[command])
        case "evaluate":
            evaluate(args[command])
        case _:
            print("This argument is not attached to any functions.")


def GenerateUQ(question: str, id: str | None = None) -> UnansweredQuestion:
    """Generate Unanswered Questions to avoid repetitions in code"""
    UQ = UnansweredQuestion(question=question)
    if id:
        UQ.question_id = id
    return UQ


def answer(args: Dict[str, Any]) -> None:
    """Call the AI to answer a question"""
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


@secure((FileNotFoundError, IsADirectoryError))
def answer_dataset(args: Dict[str, Any]) -> List[AnsweredQuestion]:
    """Anwser a dataset and return the answer the list"""
    import json
    from .Model.AI import Assistant
    datapath, savepath = args['-dataset_path'], args['-save_directory']
    if not isdir(savepath):
        raise IsADirectoryError("Expected a directory for -save_directory")
    savepath += "/StudentSearchResultsAndAnswer.json"
    datasets = []
    answers = []
    if not isinstance(datapath, str):
        raise ValueError

    with open(datapath, "r") as f:
        file = json.load(f)
        if not file.get("search_results"):
            raise FileNotFoundError("File given dont match result of dataset.")
        datasets = file["search_results"]
    for i in tqdm(datasets, desc="Answering"):
        search = MinimalSearchResults(
            question=i["question"],
            question_id=i["question_id"],
            retrieved_sources=[MinimalSource(
                text_value=get_text_in_file(a),
                first_character_index=a["first_character_index"],
                last_character_index=a["last_character_index"],
                file_path=a["file_path"]
            ) for a in i["retrieved_sources"]]
        )
        aq: AnsweredQuestion = Assistant().generate_response(search)
        aq.sources
        answers.append(aq)

    answerJSON = [{
            "question": a.question,
            "question_id": a.question_id,
            "answer": a.answer,
            "retrieved_sources": [
                {
                    "text_value": ms.text_value,
                    "first_character_index": ms.first_character_index,
                    "last_character_index": ms.last_character_index,
                    "file_path": ms.file_path
                } for ms in a.sources]
    } for a in answers]

    if isfile(savepath):
        remove(savepath)
    with open(savepath, "x") as f:
        f.write(json.dumps(answerJSON, indent=1))
    return answers


@secure(IsADirectoryError)
def search_dataset(args: Dict[str, Any]) -> StudentSearchResults:
    """Search datasets based on a question asked and return the sources."""
    import json
    from time import time
    datapath = args['-dataset_path']
    savepath = args['-save_directory']
    if not isdir(savepath):
        raise IsADirectoryError("Expected a directory for -save_directory")
    savepath += "/StudentSearchResults.json"
    sources_count = int(args['-k'])

    if not isinstance(datapath, str) or not isinstance(savepath, str):
        raise ValueError

    with open(datapath, "r") as f:
        loaded_data = json.load(f)
    anwsers: List[MinimalSearchResults] = []
    i = 1
    t = time()
    for data in tqdm(loaded_data['rag_questions'], desc="Searching"):
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
    if isfile(savepath):
        remove(savepath)
    with open(savepath, 'x') as f:
        f.write(json.dumps(to_dict, indent=1))

    print(f"Finished after {(time() - t)/60:.0f}.{(time() - t) % 60:.0f} "
          "minute")
    return StudentSearchResults(
        search_results=anwsers,
        k=sources_count
    )


def index(args: Dict[str, Any]) -> None:
    """Index the raw file as a json file of chunks"""
    cs = args["-max_chunk_size"] if args.get("-max_chunk_size") else 2000
    CS = ChunkingService()
    if CS._LoadRecusive("data/raw"):
        CS._WriteStatus(CS.Position)
        print(f"\033[38;2;0;255;0mChunks of {cs} has fully been"
              "saved under \"data/processed/index.json\".\033[0m")


@secure(ValueError)
def evaluate(args: Dict[str, Any]) -> None:
    """Avaluate the database and print the percent of good sources"""
    """Good sources are the one that overlap by 10% with the subject's"""
    import json
    eval, stud = args["-student_search_results_path"], args["-dataset_path"]
    if not PermChecker.CanOpenFile(eval) or not PermChecker.CanOpenFile(stud):
        print("Invalid File.")

    evaldata = {}
    studdata = {}

    with open(eval, "r") as fe:
        evaldata = json.loads(fe.read())["rag_questions"]
    with open(stud, "r") as fs:
        studdata = json.loads(fs.read())["search_results"]

    avarage: Dict[str, List[int]] = {
        "1": [],
        "3": [],
        "5": [],
        "10": []
    }
    answers = {}

    for a in studdata:
        answers[a["question_id"]] = a["retrieved_sources"]

    for question in evaldata:
        ID = question["question_id"]
        target_answer = answers.get(ID)
        if not target_answer:
            raise ValueError("The data paths do not match. please verify"
                             " your file's path.")
        for source_count in list(avarage.keys()):
            icount = int(source_count)
            if not isinstance(icount, int):
                continue
            correct = False
            for current in range(icount):
                a_source = target_answer[current]
                s_source = question["sources"][0]
                if a_source["file_path"] == s_source["file_path"]:
                    a_start = a_source["first_character_index"]
                    a_end = a_source["last_character_index"]

                    s_start = s_source["first_character_index"]
                    s_end = s_source["last_character_index"]

                    la = a_end - a_start
                    c1, c2 = s_start, s_end

                    c1 = max(a_start, s_start)
                    c2 = min(a_end, s_end)

                    prct = (c2 - c1) / la
                    if prct >= 0.05 and correct is False:
                        avarage[source_count] += [1]
                        correct = True
            if correct is False:
                avarage[source_count] += [0]

    print(f"\nEvaluating {len(studdata)} sources\n")

    for index in list(avarage.keys()):
        total = 0
        found = 0
        for i in avarage[index]:
            total += 1
            found += i
        match found:
            case 0:
                print(f"Recall @{index} = ~0")
            case _:
                print(f"Recall @{index} = {((found / total)*100):0.2f}%")
    print()


if __name__ == "__main__":
    main_func()
