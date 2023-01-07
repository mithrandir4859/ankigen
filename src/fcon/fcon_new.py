import os
import re
from collections import Counter
from typing import List

from config_new import fcon_config
from di import Singleton
from fcon.entities import Fcard

import logging

from utils_i import setup_logger, wrap_into_list

logger = logging.getLogger('root')


class FManager:
    def __init__(self, cards: List[Fcard]):
        self._cards = {c.identifier: c for c in cards}
        self._ids = sorted(self._cards.keys())

    def __len__(self):
        return len(self._cards)

    def __iter__(self):
        yield from self._cards.values()

    def keys(self):
        return set(self._cards.keys())

    def values(self):
        return self._cards.values()

    def __getitem__(self, item):
        if isinstance(item, int):
            item = self._ids[item]
        return self._cards[item]

    def __str__(self):
        return f'FManager(len={len(self)})'

    __repr__ = __str__


class FReader:
    def read_cards(self) -> FManager:
        raise NotImplementedError


class FReaderFromFWiki(FReader):
    QUESTION_MARKERS = [
        'q:',
        '__q__:',
        '**q**:'
    ]
    QUESTION_IDENTIFIER_REGEX = r'(?P<identifier>/\d{4} \w{3} \d\d, \d\d:\d\d \d{4}/)'

    def __init__(self, paths):
        self.paths = paths
        self._identifier_regex = re.compile(self.QUESTION_IDENTIFIER_REGEX)
        self.no_identifier_counter = Counter()
        self.cards: List[Fcard] = list()

    def read_cards(self) -> FManager:
        cards = self._create_cards()
        self._verify_ids()
        for filename, count in self.no_identifier_counter.most_common():
            logger.info(f'{filename}, {count}')
        return FManager(cards)

    def _get_q_marker(self, text):
        text = text[:10].lower()
        for marker in self.QUESTION_MARKERS:
            if text.startswith(marker):
                return marker

    def _get_id(self, text):
        for match in re.finditer(self._identifier_regex, text):
            return match.group('identifier')

    def _create_card(self, text, filepath) -> (Fcard, None):
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
        return Fcard(
            identifier=identifier,
            question=question.strip(),
            answer=answer.strip(),
            original_text=original_text,
            original_file=filepath
        )

    @wrap_into_list
    def _create_cards(self):
        for path_ in self.paths:
            if not os.path.exists(path_):
                raise FileNotFoundError(path_)
            for subdir, dirs, files in os.walk(path_):
                for file in files:
                    filepath = subdir + os.sep + file
                    if not filepath.endswith('.md'):
                        continue
                    with open(filepath) as f:
                        content = f.read().strip()
                    if '---' not in content:
                        continue
                    if content.startswith('#ankiskip'):
                        logger.info(f'Skipping {file}')
                        continue
                    cards = content.split('---')
                    cards = [self._create_card(t, filepath) for t in cards]
                    cards = [c for c in cards if c]
                    if cards:
                        yield from cards
                        logger.info(f'Found {len(cards)} in {filepath}')

    def _verify_ids(self):
        ids = {c.identifier for c in self.cards}
        assert len(ids) == len(self.cards)


class FReaderFromAnkiExport(FReader):
    def __init__(self, path):
        self.path = path

    def read_cards(self) -> FManager:
        pass


class FWriter:
    def write_cards(self, manager: FManager):
        raise NotImplementedError


class FWriter2AnkiImport(FWriter):
    def __init__(self, paths):
        self.paths = paths

    def write_cards(self, manager: FManager):
        pass


class FWriter2Fwiki(FWriter):
    def __init__(self, reader: FReaderFromFWiki):
        self.reader = reader

    def write_cards(self, manager: FManager):
        fwiki_manager = self.reader.read_cards()

        pass


class Workflow:
    def __init__(self, reader: FReader, writer: FWriter):
        self.reader = reader
        self.writer = writer

    def run(self):
        f_manager = self.reader.read_cards()
        self.writer.write_cards(f_manager)
        logger.info('Workflow finished')


class FconDi:
    def __init__(self, config):
        direction = config['direction']
        reader_from_wiki = Singleton(
            FReaderFromFWiki, paths=config['fwiki_paths']
        )
        if direction == '2anki':
            self.reader = reader_from_wiki
            self.writer = Singleton(
                FWriter2AnkiImport, paths=config['import_2_anki_paths']
            )
        elif direction == '2fwiki':
            self.reader = Singleton(
                FReaderFromAnkiExport, path=config['export_from_anki_path']
            )
            self.writer = Singleton(
                FWriter2Fwiki, reader=reader_from_wiki
            )
        else:
            raise ValueError(f'Invalid direction: {direction}')

        self.workflow = Singleton(Workflow, reader=self.reader, writer=self.writer)
        logger.info(f'Direction={direction}')


if __name__ == '__main__':
    setup_logger()
    di = FconDi(fcon_config)
    workflow = di.workflow()
    workflow.run()
