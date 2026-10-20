from .Chunker.ChunkingService import ChunkingService
from typing import Dict, Any, List
from .Chunker.DataModels import UnansweredQuestion
from .Chunker.DataModels import MinimalSearchResults, MinimalSource
from .Chunker.DataModels import RagDataset, MinimalAnswer
from .Chunker.DataModels import StudentSearchResultsAndAnswer
from .Utils.Decorators import secure
from json.decoder import JSONDecodeError
from os.path import isfile, isdir
from os import remove
from tqdm import tqdm  # type: ignore[import-untyped, unused-ignore]
from fire import Fire  # type: ignore[import-untyped, unused-ignore]


def GenerateUQ(question: str, id: str | None = None) -> UnansweredQuestion:
    """Generate Unanswered Questions to avoid repetitions in code"""
    UQ = UnansweredQuestion(question=question)
    if id:
        UQ.question_id = id
    return UQ


def get_text_in_file(datasetsource: Dict[str, Any]) -> str:
    "Get the text of a file based on the index of the first and last character"
    with open(datasetsource["file_path"], "r") as f:
        return f.read()[datasetsource["first_character_index"]:
                        datasetsource["last_character_index"]]


class Commands:
    def index(self, max_chunk_size: int = 2000) -> None:
        """Index the raw file as a json file of chunks"""
        CS = ChunkingService()
        if CS.Index("data/raw", max_chunk_size):
            CS._WriteStatus(CS.Position)
            print(f"\033[38;2;0;255;0mChunks of {max_chunk_size} "
                  "has fully been"
                  "saved under \"data/processed/index.json\".\033[0m")

    @secure((ValueError))
    def search(self, query: str = "", k: int = 5) -> MinimalSearchResults:
        """Search the sources for a question"""
        if k <= 0:
            raise ValueError("Number of sources must be at least 1")
        sources = ChunkingService().fetch_bm25_results(GenerateUQ(query), k)
        return sources

    @secure((IsADirectoryError, JSONDecodeError, ValueError,
            PermissionError, FileNotFoundError))
    def search_dataset(self, dataset_path: str = "", k: int = 5,
                       save_directory: str = "") -> str:
        """Search datasets based on a question asked and return the sources."""
        import json
        from time import time
        if not isdir(save_directory):
            raise IsADirectoryError("Expected a directory for -save_directory")

        dirpath = dataset_path.split("/")
        filename = dirpath[len(dirpath) - 1]

        if "code" in filename and isdir(save_directory + "/code"):
            save_directory += "/code"
        elif "docs" in filename and isdir(save_directory + "/docs"):
            save_directory += "/docs"
        save_directory += "/StudentSearchResults.json"

        if k <= 0:
            raise ValueError("Number of sources must be at least 1")
        loaded_data = {}
        try:
            with open(dataset_path, "r") as f:
                loaded_data = json.load(f)
        except PermissionError as err:
            raise PermissionError(f"Read permissions missing: {err}")
        except FileNotFoundError as err:
            raise FileNotFoundError(f"File could not be found: {err}")
        anwsers: List[MinimalSearchResults] = []
        i = 1
        t = time()

        if (not isinstance(loaded_data, dict)
                or not loaded_data.get("rag_questions")):
            raise ValueError("Json malformed, needs to"
                             " be '{rag_questions:[...]}'")

        for rq in loaded_data['rag_questions']:
            try:
                if rq["question_id"]:
                    pass  # checking if question_id is inside the json.
                if not rq.get("question") or rq["question"] == "":
                    print("Question cant not be None or empty.")
                    raise ValueError(rq)
            except KeyError:
                raise ValueError("Malformed json,"
                                 "question and question_id are mendatory.\n\t"
                                 f"current value: {rq}")

        rd = RagDataset(rag_questions=([GenerateUQ(data["question"],
                                                   data["question_id"])
                        for data in loaded_data['rag_questions']]))

        for question in tqdm(rd.rag_questions, desc="Searching"):
            source = ChunkingService().fetch_bm25_results(question, k)
            anwsers.append(source)
            i += 1

        to_dict = {"search_results": [], "k": k}
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
        if isfile(save_directory):
            remove(save_directory)
        with open(save_directory, 'x') as f:
            f.write(json.dumps(to_dict, indent=1))

        print(f"Finished after {(time() - t)/60:.0f}.{(time() - t) % 60:.0f} "
              "minute")
        return f"Data saved as {save_directory}"

    @secure(ValueError)
    def answer(self, query: str = "", k: int = 5) -> str:
        """Call the AI to answer a question"""
        from .Model.AI import Assistant
        search_data = self.search(query, k)
        if not search_data:
            return "No search data found"
        responce = Assistant().generate_response(search_data)
        if not responce:
            return "No responce was given."
        return responce.answer

    @secure((FileNotFoundError, IsADirectoryError))
    def answer_dataset(self, student_search_results_path: str = "",
                       save_directory: str = ""
                       ) -> StudentSearchResultsAndAnswer:
        """Anwser a dataset and return the answer the list"""
        import json
        from .Model.AI import Assistant

        dirpath = student_search_results_path.split("/")
        filename = dirpath[len(dirpath) - 1]

        datapath = student_search_results_path
        savepath = save_directory
        if not isdir(savepath):
            raise IsADirectoryError("Expected a directory for -save_directory")
        if "code" in filename and isdir(savepath + "/code"):
            savepath += "/code"
        elif "docs" in filename and isdir(savepath + "/docs"):
            savepath += "/docs"
        savepath += "/StudentSearchResultsAndAnswer.json"
        datasets = []
        k: int = 0
        answers: List[MinimalAnswer] = []
        if not isinstance(datapath, str):
            raise ValueError

        with open(datapath, "r") as f:
            file = json.load(f)
            if not file.get("search_results"):
                raise FileNotFoundError("File given dont"
                                        " match result of dataset.")
            datasets = file["search_results"]
            k = file["k"]

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
            ma: MinimalAnswer = Assistant().generate_response(search)
            answers.append(ma)

        studresult = StudentSearchResultsAndAnswer(
            search_results=answers,
            k=k
        )

        answerJSON = studresult.todict()
        if isfile(savepath):
            remove(savepath)
        with open(savepath, "x") as f:
            f.write(json.dumps(answerJSON, indent=4))

        return studresult

    @secure((ValueError, FileNotFoundError,
             PermissionError, IsADirectoryError))
    def evaluate(self, student_search_results_path: str = "",
                 dataset_path: str = "") -> None:
        """Avaluate the database and print the percent of good sources"""
        """Good sources are the one that overlap by 10% with the subject's"""
        import json
        stud = student_search_results_path
        eval = dataset_path

        if isinstance(eval, bool):
            raise ValueError("Invalid Arguments for -dataset_path")

        print(eval, stud)
        evaldata = {}
        studdata = {}

        try:
            with open(eval, "r") as fe:
                evaldata = json.loads(fe.read())["rag_questions"]
            with open(stud, "r") as fs:
                studdata = json.loads(fs.read())["search_results"]
        except FileNotFoundError as err:
            raise FileNotFoundError(f"Could not find files:\n\t\t{err}")
        except PermissionError as err:
            raise PermissionError("Permissions missing to open"
                                  f" file: \n\t\t{err}")

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
                                 " your file's path. "
                                 "(you probably inversed docs "
                                 "and code for your set)")
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


def CreateEmptyFiles() -> None:
    from pathlib import Path
    paths = ["data/output",
             "data/processed",
             "data/output/search_results/code",
             "data/output/search_results/docs",
             "data/output/search_results_and_answer/code",
             "data/output/search_results_and_answer/docs"]

    for str in paths:
        Path(str).mkdir(parents=True, exist_ok=True)


@secure((KeyboardInterrupt, TypeError))
def main() -> None:
    CreateEmptyFiles()
    Fire(Commands)


if __name__ == "__main__":
    main()
