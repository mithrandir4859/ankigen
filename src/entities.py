from typing import List, Set

from pydantic import BaseModel, Field


class Word:
    text: str
    frequency: int


class Translation(BaseModel):
    word: str
    confidence: int = None
    pos: str = None
    back_translations: List[str] = Field(default_factory=list)


class Synonym(BaseModel):
    word: str
    pos: str


class DictionaryCard(BaseModel):
    word: str
    translations: List[Translation] = Field(default_factory=list)
    synonyms: List[Synonym] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    too_similar: Set[str] = Field(default_factory=set)
