import csv
import os
import re
from collections import Counter
from typing import List

from utils_i import wrap_into_list
from fcon.entities import Fcard

BASE_WIKI_PATH = '/home/mithrandir/Mednition/wiki_mednition/wiki_fresh/'
BASE_ANKIGEN_PATH = '/home/mithrandir/Projects/ankigen_files/'


class FconFromFwiki:
    def _store_anki_cards(self):
        with open(self._anki_output_path, 'w') as out:
            writer = csv.DictWriter(out, fieldnames='identifier front back'.split(), delimiter='\t')
            print(f'Creating {len(self.cards)} cards')
            for card in self.cards:
                writer.writerow(dict(
                    identifier=card.identifier,
                    front=card.question,
                    back=card.answer
                ))


class Fcon2Fwiki:
    def __init__(self, cards_from_wiki):
        self._anki_cards_path = f'{BASE_ANKIGEN_PATH}/anki_export.txt'
        self.cards_from_anki = None
        self.cards_form_wiki = cards_from_wiki

    @wrap_into_list
    def _create_cards(self):
        with open(self._anki_cards_path) as f:
            for card in csv.DictReader(f, fieldnames='identifier front back'.split(), delimiter='\t'):
                yield Fcard(
                    identifier=card['identifier'],
                    question=card['front'],
                    answer=card['back']
                )

    def run(self):
        self.cards_from_anki = self._create_cards()
        cards_from_anki_dict = {c.identifier: c for c in self.cards_from_anki}
        cards_from_wiki_dict = {c.identifier: c for c in self.cards_form_wiki}
        identifiers = set(cards_from_anki_dict.keys()) | set(cards_from_wiki_dict.keys())
        print(f'Found {len(identifiers)} identifiers')

        for identifier in identifiers:
            anki_card = cards_from_anki_dict.get(identifier)
            wiki_card = cards_from_wiki_dict.get(identifier)
            # if not anki_card

            print(anki_card, wiki_card)


if __name__ == '__main__':
    wiki_anki_converter = FconFromFwiki()
    wiki_anki_converter.run()
    anki_2_wiki_converter = Fcon2Fwiki(cards_from_wiki=wiki_anki_converter.cards)
    anki_2_wiki_converter.run()
