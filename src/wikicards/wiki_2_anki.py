import csv
import os
import re
from collections import Counter
from typing import List

from utils_i import wrap_into_list
from wikicards.entities import WikiCard


class Wiki2AnkiConverter:
    QUESTION_MARKERS = [
        'q:',
        '__q__:',
        '**q**:'
    ]
    QUESTION_IDENTIFIER_REGEX = r'(?P<identifier>/\d{4} \w{3} \d\d, \d\d:\d\d \d{4}/)'

    def __init__(self):
        self._base_wiki_path = '/home/mithrandir/Mednition/wiki_mednition/wiki_fresh/'
        self._anki_output_path = '/home/mithrandir/Projects/output/anki_cards.txt'
        self._identifier_regex = re.compile(self.QUESTION_IDENTIFIER_REGEX)
        self.no_identifier_counter = Counter()
        self.cards: List[WikiCard] = list()

    def _get_q_marker(self, text):
        text = text[:10].lower()
        for marker in self.QUESTION_MARKERS:
            if text.startswith(marker):
                return marker

    def _get_id(self, text):
        for match in re.finditer(self._identifier_regex, text):
            return match.group('identifier')

    def _create_card(self, text, filepath) -> (WikiCard, None):
        original_text = text
        text = text.strip()
        marker = self._get_q_marker(text)
        if not marker:
            return
        text = text[len(marker):].strip()
        identifier = self._get_id(text)
        if not identifier:
            self.no_identifier_counter[filepath] += 1
            return
        question, answer = text.split(identifier)
        return WikiCard(
            identifier=identifier,
            question=question.strip(),
            answer=answer.strip(),
            original_text=original_text,
            original_file=filepath
        )

    @wrap_into_list
    def _create_cards(self):
        for subdir, dirs, files in os.walk(self._base_wiki_path):
            for file in files:
                # print os.path.join(subdir, file)
                filepath = subdir + os.sep + file
                if not filepath.endswith(".md"):
                    continue
                with open(filepath) as f:
                    content = f.read().strip()
                if '---' not in content:
                    continue
                if content.startswith('#ankiskip'):
                    print(f'Skipping {file}')
                    continue
                cards = content.split('---')
                cards = [self._create_card(t, filepath) for t in cards]
                cards = [c for c in cards if c]
                yield from cards
                if cards:
                    print(f'Found {len(cards)} in {filepath}')

    def _verify_ids(self):
        ids = {c.identifier for c in self.cards}
        assert len(ids) == len(self.cards)

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

    def run(self):
        self.cards = self._create_cards()
        self._verify_ids()
        self._store_anki_cards()
        for filename, count in self.no_identifier_counter.most_common():
            print(filename, count)


class Anki2WikiConverter:
    def run(self):
        ...


if __name__ == '__main__':
    Wiki2AnkiConverter().run()
