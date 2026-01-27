from pydantic import BaseModel
from typing import List

class IngestResponse(BaseModel):
    message: str
    table_of_contents: List[str]
