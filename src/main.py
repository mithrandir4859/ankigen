import shelve
import traceback
from collections import Counter

from requests import HTTPError

from config_gitignored import NAMESPACE
from google import GoogleTranslator, GoogleResponseParser, CardEnricher, AnkiCardCreator
from utils import get_repo_path


class CachingProxyTranslator:
    def __init__(self, delegate, cache_only=False):
        self.delegate = delegate
        name = type(delegate).__name__.lower()
        self.storage = shelve.open(f'{get_repo_path()}/data/dictionaries/{name}')
        print(f'Cache has {len(self.storage)} entries')
        self.cache_only = cache_only

    def __call__(self, word):
        if translation := self.storage.get(word):
            return translation
        elif self.cache_only:
            return
        translation = self.delegate(word)
        self.storage[word] = translation
        return translation

    def close(self):
        self.storage.sync()
        self.storage.close()


class BatchTranslator:
    def __init__(self, namespace):
        self.translator = CachingProxyTranslator(GoogleTranslator())
        self.namespace = namespace
        self.card_creator = GoogleResponseParser()
        self.stats = Counter()
        print(f'namespace={namespace}')

    def _get_path(self, filename):
        return f'{get_repo_path()}/data/namespaces/{self.namespace}/{filename}'

    def _load_words(self):
        words = set()
        with open(self._get_path('words.txt')) as f:
            for word in f.readlines():
                words.add(word.strip())
        words.discard('')
        return sorted(words)

    def _create_anki_cards(self, words):
        for word in words:
            try:
                response = self.translator(word)
                if not response:
                    print(f'skipping: {word}')
                    continue
                card = self.card_creator.create_card(word, response)
                CardEnricher.enrich(card)
                anki_card = AnkiCardCreator.create_card(card)
                if not anki_card:
                    print(f'empty card for: {word}')
                yield anki_card
                if len(card.too_similar) > 1:
                    # print(f'too similar: {word}, {card.too_similar}')
                    self.stats['has_too_similar'] += 1
                    self.stats['too_similar_count'] += len(card.too_similar)
                if not card.translations:
                    print(f'No translations for: {word}')
                    self.stats['no_translation_count'] += 1
                else:
                    self.stats['success_count'] += 1
            except HTTPError as ex:
                if ex.args[0] == 429:
                    print('too many requests')
                else:
                    traceback.print_exc()
                self.translator.cache_only = True
            except Exception:
                traceback.print_exc()

    def run(self):
        words = self._load_words()
        self.stats['raw_words_count'] = len(words)
        print(f'Loaded {len(words)} words: {" ".join(words[:10])}...')
        try:
            with open(self._get_path('anki.cards'), 'w') as out:
                for card in self._create_anki_cards(words):
                    if card:
                        out.write(card + '\n')
        finally:
            self.translator.close()
            print(self.stats)
            print(AnkiCardCreator.pos)


if __name__ == '__main__':
    BatchTranslator(NAMESPACE).run()
