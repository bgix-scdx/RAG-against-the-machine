from pydantic import BaseModel, Field
from typing import List
import uuid


class MinimalSource(BaseModel):
    file_path: str
    first_character_index: int
    last_character_index: int


class UnawseredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str


class AnwseredQuestion(BaseModel):
    sources: List[MinimalSource]
    anwser: str


class RagDataSet(BaseModel):
    rag_questions: List[AnwseredQuestion | UnawseredQuestion]


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]


class MinimalAnwser(MinimalSearchResults):
    answser: str


class StudentSearchResult(BaseModel):
    search_result: List[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnwser(BaseModel):
    search_results: List[MinimalAnwser]
