from pydantic import BaseModel
from typing import List, Optional


class QuestionRequest(BaseModel):
    query: str
    # number of valid questions desired
    num_questions: int = 5


class QuestionResponse(BaseModel):
    # return list of valid questions (could be less than requested if iterations ended)
    questions: List[str]
    evaluation: str
    iterations: int
    passed: bool
