from pydantic import BaseModel
from typing import List, Optional

class QuestionRequest(BaseModel):
    query: str

class QuestionResponse(BaseModel):
    questions: str
    evaluation: str
    iterations: int
    passed: bool
