import datetime
from typing import List

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    author_id: str = 'Mithrandir'
    created_ts: datetime.datetime
    creation_algorithm_id: str = ''
    source: str = ''  # url or local filepath


class Fcard(BaseModel):
    identifier: str
    question: str
    answer: str
    tags: List[str] = Field(default_factory=list)
    original_text: str = None
    original_file: str = None


class WikiCardPair:
    anki_card: Fcard
    wiki_card: Fcard

    @property
    def identifier(self):
        assert self.anki_card.identifier == self.wiki_card.identifier
        return self.anki_card.identifier