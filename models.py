from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class QuizQuestion(BaseModel):
    question: str = Field(..., example="Where did Alan Turing study?")
    options: List[str] = Field(
        ..., example=["Harvard University", "Cambridge University", "Oxford University", "Princeton University"]
    )
    answer: str = Field(..., example="Cambridge University")
    difficulty: str = Field(..., example="easy")
    explanation: str = Field(..., example="Mentioned in the 'Early life' section.")


class KeyEntities(BaseModel):
    people: List[str] = Field(default_factory=list, example=["Alan Turing", "Alonzo Church"])
    organizations: List[str] = Field(default_factory=list, example=["University of Cambridge", "Bletchley Park"])
    locations: List[str] = Field(default_factory=list, example=["United Kingdom"])


class QuizResponse(BaseModel):
    id: Optional[int] = Field(None, example=1)
    url: str = Field(..., example="https://en.wikipedia.org/wiki/Alan_Turing")
    title: str = Field(..., example="Alan Turing")
    summary: str = Field(
        ...,
        example="Alan Turing was a British mathematician and computer scientist who played a key role in modern computing."
    )
    key_entities: KeyEntities
    sections: List[str] = Field(default_factory=list, example=["Early life", "World War II", "Legacy"])
    quiz: List[QuizQuestion]
    related_topics: List[str] = Field(default_factory=list, example=["Cryptography", "Enigma machine", "Computer science history"])
