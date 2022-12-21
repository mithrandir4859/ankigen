import csv
import shelve

from site_generator import get_repo_path


class CardsCreator:
    def __init__(self, source='dune'):
        self.source = source
        self.storage = shelve.open(f'{get_repo_path()}/data/ankigen_output/{self.source}_dict')
        self.stats = dict()

        self.f = open(f'{get_repo_path()}/data/ankigen_output/{self.source}_too_similar.csv', 'w')
        self.writer_similar = csv.DictWriter(self.f, fieldnames='source translation distance'.split())
        self.writer_similar.writeheader()




if __name__ == '__main__':
    CardsCreator().main()
