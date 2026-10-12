from pydantic import BaseModel, Field
import uuid
from typing import List, Dict, Any


class MinimalSource(BaseModel):
    """
    Store data of a chunk, including: Path, Last and First Index, Text,
    and its score if given one (set as 0 by default)
    """
    file_path: str
    first_character_index: int
    last_character_index: int
    text_value: str
    score: float = 0

    def todict(self) -> Dict[str, Any]:
        return {
                "file_path": self.file_path,
                "first_character_index": self.first_character_index,
                "last_character_index": self.last_character_index,
                "text_value": self.text_value,
                "score": self.score
        }


class UnansweredQuestion(BaseModel):
    """
    Created by a prompt, Store a question and its ID.
    if no id is given, a random one is generated.
    """
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """
    An answer given by the LLM, store its response and the sources used.
    """
    sources: List[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """
    Store a list of Answered or Unanswered Questions.
    """
    rag_questions: List[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """
    Store a question, its ID and a list of sources found for the question.
    """
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]

    def todict(self) -> Dict[str, Any]:
        return {
                "question_id": self.question_id,
                "question": self.question,
                "retrieved_sources": [_ms.todict()
                                      for _ms in self.retrieved_sources]
        }


class MinimalAnswer(MinimalSearchResults):
    """
    Only store the answer of the LLM about a question.
    """
    answer: str

    def todict(self) -> Dict[str, Any]:
        return {
                "question_id": self.question_id,
                "question": self.question,
                "answer": self.answer,
                "retrieved_sources": [_ms.todict()
                                      for _ms in self.retrieved_sources]
        }


class StudentSearchResults(BaseModel):
    """
    The result of a datasearch, containing a list of MinimalSearchResult and
    k being the ammount of sources allowed.
    """
    search_results: List[MinimalSearchResults]
    k: int

    def todict(self) -> Dict[str, Any]:
        return {
                "search_results": [_msr.todict()
                                   for _msr in self.search_results],
                "k": self.k
        }


class StudentSearchResultsAndAnswer(BaseModel):
    """
    The result of a answer_dataset, containing a list of search_results
    and k being the ammount of sources allowed.
    """
    search_results: List[MinimalAnswer]
    k: int

    def todict(self) -> Dict[str, Any]:
        return {
                "search_results": [_ma.todict()
                                   for _ma in self.search_results],
                "k": self.k
        }
