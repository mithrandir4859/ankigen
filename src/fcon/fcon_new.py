from typing import List

from config_new import fcon_config
from di import Singleton
from fcon.entities import Fcard

import logging

from utils_i import setup_logger

logger = logging.getLogger('root')


class FManager:
    def __init__(self, cards: List[Fcard]):
        self._cards = {c.identifier: c for c in cards}


class FReader:
    def read_cards(self) -> FManager:
        raise NotImplementedError


class FReaderFromFWiki(FReader):
    def __init__(self, paths):
        self.paths = paths

    def read_cards(self) -> FManager:
        print('why')


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
        fwiki_manager = self.reader.load_cards()

        pass


class Workflow:
    def __init__(self, reader: FReader, writer: FWriter):
        self.reader = reader
        self.writer = writer

    def run(self):
        f_manager = self.reader.load_cards()
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
