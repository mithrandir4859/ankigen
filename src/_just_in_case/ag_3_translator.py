import csv
import json
import random
import shelve
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import tqdm

from config_gitignored import LIMIT
from _just_in_case.translation_microsoft import MicrosoftTranslator
from src.ankigen.utils import chunker
from site_generator import get_repo_path


class TranslationManager:
    def __init__(self, source='dune'):
        self.translator = MicrosoftTranslator.create_instance()
        self.pool = ThreadPoolExecutor(max_workers=16)
        self.source = source
        self.storage = shelve.open(f'{get_repo_path()}/data/ankigen_output/{self.source}_dict')
        self.stats = dict()
        self.words_translated_ok_count = 0
        self.words_translated_no_translation_count = 0

    def _load_words(self):
        with open(f'{get_repo_path()}/data/ankigen_output/{self.source}.txt') as f:
            return list(csv.DictReader(f))

    def main(self):
        words = self._load_words()
        random.shuffle(words)
        words = words[:LIMIT]
        self.stats['words_count_initial'] = len(words)
        translated_words = set(self.storage.keys())
        self.stats['words_translated_previously'] = len(translated_words)
        words = sorted({w['word'] for w in words} - translated_words)
        mid = len(words) // 2
        delta = 10
        print(len(words), ' '.join(words[:delta] + words[mid:mid+delta] + words[-delta:]))
        self.stats['words_count_filtered'] = len(words)

        futures = list()
        chunks = chunker(words, 10)
        for chunk in chunks:
            futures.append(self.pool.submit(self.translator.translate, chunk))
        try:
            for future in tqdm.tqdm(as_completed(futures), total=len(chunks), smoothing=0):
                result = future.result()
                for word, dictionary_card in result.items():
                    self.storage[word] = dictionary_card
                    if dictionary_card.translations:
                        self.words_translated_ok_count += 1
                    else:
                        self.words_translated_no_translation_count += 1
                        print(f'No translation for: {word}')
        except Exception:
            traceback.print_exc()
        finally:
            self.storage.sync()
            self.storage.close()

        self.stats.update(
            words_translated_ok_count=self.words_translated_ok_count,
            words_translated_no_translation_count=self.words_translated_no_translation_count
        )
        print(json.dumps(self.stats, indent=4))


if __name__ == '__main__':
    TranslationManager().main()
