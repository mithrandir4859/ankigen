import csv
import os
import re
from collections import Counter, defaultdict
from typing import List, Iterable, Set, Collection

from config_new import fcon_config
from di import Singleton
from fcon.entities import Fcard

import logging

from utils_i import setup_logger, wrap_into_list

ANKISKIP_TAG = '#ankiskip'

logger = logging.getLogger('root')


class FManager:
    def __init__(self, cards: List[Fcard]):
        self._cards = {c.identifier: c for c in cards}
        self._ids = sorted(self._cards.keys())

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self) -> Iterable[Fcard]:
        yield from self._cards.values()

    def keys(self) -> Set[str]:
        return set(self._cards.keys())

    def values(self) -> Collection[Fcard]:
        return self._cards.values()

    def __getitem__(self, item) -> Fcard:
        if isinstance(item, int):
            item = self._ids[item]
        return self._cards[item]

    def get(self, key) -> Fcard:
        return self._cards.get(key)

    def __str__(self) -> str:
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
    KILLER_TAGS = ANKISKIP_TAG, '#wip'

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

    def _is_good_card(self, card: Fcard):
        if not card.answer or card.answer == '#todo':
            logger.info(f'Card {card.identifier} was skipped because the answer is empty')
            return
        if card.answer.startswith('tags:') and '\n' not in card.answer:
            logger.info(f'Card {card.identifier} was skipped because it contains only tags')
            return
        for tag in self.KILLER_TAGS:
            if tag in card.answer or tag in card.question:
                logger.info(f'Card {card.identifier} was skipped because it contains {ANKISKIP_TAG}')
                return
        return True

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
        card = Fcard(
            identifier=identifier,
            question=question.strip(),
            answer=answer.strip(),
            original_text=original_text,
            original_file=filepath
        )
        if self._is_good_card(card):
            return card

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
                    if content.startswith(ANKISKIP_TAG):
                        logger.info(f'Skipping {file}')
                        continue
                    cards = content.split('---')
                    cards = [self._create_card(t, filepath) for t in cards]
                    cards = [c for c in cards if c]
                    if cards:
                        yield from cards
                        logger.info(f'Found {len(cards)} cards in {file}')

    def _verify_ids(self):
        ids = {c.identifier for c in self.cards}
        assert len(ids) == len(self.cards)


class FReaderFromAnkiExport(FReader):
    def __init__(self, path):
        self.path = path

    def read_cards(self) -> FManager:
        cards = self._read_cards()
        return FManager(cards)

    @wrap_into_list
    def _read_cards(self):
        with open(self.path) as f:
            for card in csv.DictReader(f, fieldnames='identifier front back'.split(), delimiter='\t'):
                yield Fcard(
                    identifier=card['identifier'],
                    question=self._to_markdown(card['front']),
                    answer=self._to_markdown(card['back'])
                )

    @staticmethod
    def _to_markdown(html_text):
        return html_text.replace('<br>', '\n').replace('&nbsp;', ' ').replace('&gt;', '>').replace('&amp;', '&')


class FWriter:
    def write_cards(self, manager: FManager):
        raise NotImplementedError


class FWriter2AnkiImport(FWriter):
    def __init__(self, paths):
        self.paths = paths

    def write_cards(self, manager: FManager):
        for path_ in self.paths:
            with open(path_, 'w') as out:
                writer = csv.DictWriter(out, fieldnames='identifier front back'.split(), delimiter='\t')
                logger.info(f'Creating {len(manager)} cards in {path_}')
                for card in manager:
                    writer.writerow(dict(
                        identifier=card.identifier,
                        front=card.question,
                        back=card.answer
                    ))


class FWriter2Fwiki(FWriter):
    def __init__(self, reader: FReaderFromFWiki):
        self.reader = reader

    def write_cards(self, manager_from_anki: FManager):
        existing_fwiki_manager = self.reader.read_cards()
        intersection = manager_from_anki.keys() & existing_fwiki_manager.keys()
        logger.info(
            f'existing in fwiki: {len(existing_fwiki_manager)}, '
            f'exported from Anki: {len(manager_from_anki)}, '
            f'intersection: {len(intersection)}'
        )
        grouped_anki_cards = self._get_anki_cards_grouped_by_file(
            existing_fwiki_manager, manager_from_anki
        )
        logger.info(f'Matched fcards in {len(grouped_anki_cards)} files')
        for original_file, cards in grouped_anki_cards.items():
            self._update_file(original_file, cards, existing_fwiki_manager)

    @classmethod
    def _update_file(cls, original_file, cards_from_anki, existing_fwiki_manager):
        logger.info(f'There are {len(cards_from_anki)} cards for {original_file.split("/")[-1]}')
        with open(original_file, 'r') as f:
            content = f.read()
        for anki_card in cards_from_anki:
            existing_card = existing_fwiki_manager[anki_card.identifier]
            assert existing_card.original_file == original_file
            assert existing_card.original_text in content
            replacement = cls._to_str(anki_card)
            content = content.replace(existing_card.original_text, replacement)
        with open(original_file, 'w') as out:
            out.write(content.strip())

    @staticmethod
    def _to_str(card: Fcard):
        lines = [
            f'q: {card.question}',
            card.identifier,
            card.answer,
        ]
        result = '\n'.join(lines)
        result = f'\n{result}\n\n'
        return result

    @staticmethod
    def _is_too_much_html(text):
        count = min(text.count('<'), text.count('>'))
        if count > 10:
            return count
        return 0

    @classmethod
    def _get_anki_cards_grouped_by_file(cls, existing_fwiki_manager, manager_from_anki):
        groups = defaultdict(list)
        for card in manager_from_anki:
            if too_much := cls._is_too_much_html(card.answer):
                logger.error(f'Too much html: {too_much} for {card.identifier}, q: {card.question[:66]}')
                continue
            existing_card = existing_fwiki_manager.get(card.identifier)
            if not existing_card:
                logger.warning(f'There is no fwiki card for {card.identifier}')
                continue
            groups[existing_card.original_file].append(card)
        return dict(groups)


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
