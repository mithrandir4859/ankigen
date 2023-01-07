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
    def load_cards(self) -> FManager:
        raise NotImplementedError


class FReaderFromFWiki(FReader):

    def load_cards(self) -> FManager:
        pass


class FReaderFromAnkiExport(FReader):
    def read_cards(self) -> FManager:
        pass


class FWriter:
    def write_cards(self, manager: FManager):
        raise NotImplementedError


class FWriter2AnkiImport(FWriter):

    def write_cards(self, manager: FManager):
        pass


class FWriter2Fwiki(FWriter):
    def __init__(self, fwiki_manager):
        self.fwiki_manager = fwiki_manager

    def write_cards(self, manager: FManager):
        pass


class Workflow:
    def run(self):
        raise NotImplementedError


class Workflow2Anki(Workflow):
    def run(self):
        pass


class Workflow2Fwiki(Workflow):
    def run(self):
        pass


class FconDi:
    def __init__(self, config):
        self.workflow_2_fwiki = Singleton(Workflow2Fwiki)
        self.workflow_2_anki = Singleton(Workflow2Anki)

        direction = config['direction']
        if direction == '2anki':
            self.workflow = self.workflow_2_anki
        elif direction == '2fwiki':
            self.workflow = self.workflow_2_fwiki
        else:
            raise ValueError(f'Invalid direction: {direction}')
        logger.info(f'Direction={direction}')


if __name__ == '__main__':
    setup_logger()
    di = FconDi(fcon_config)
    workflow = di.workflow()
    workflow.run()
