from typing import List

from pydantic import BaseModel, Field


class WikiCard(BaseModel):
    identifier: str
    question: str
    answer: str
    tags: List[str] = Field(default_factory=list)
    original_text: str
    original_file: str


