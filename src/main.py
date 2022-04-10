import shelve
import time
import traceback
from collections import Counter

from requests import HTTPError

from config_gitignored import NAMESPACE, EXCLUDE_WORDS_FROM, CACHE_NAME, LANGUAGE
from google import GoogleTranslator, GoogleResponseParser, CardEnricher, AnkiCardCreator
from utils import get_repo_path


class CachingProxyTranslator:
    def __init__(self, delegate, cache_only=False, cache_name=None):
        self.delegate = delegate
        cache_name = cache_name or type(delegate).__name__.lower()
        self.storage = shelve.open(f'{get_repo_path()}/data/dictionaries/{cache_name}')
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
        self.translator = CachingProxyTranslator(GoogleTranslator(dest='uk', src=LANGUAGE), cache_name=CACHE_NAME)
        self.namespace = namespace
        self.card_creator = GoogleResponseParser()
        self.stats = Counter()
        print(f'namespace={namespace}')

    def _get_path(self, filename, namespace=None):
        return f'{get_repo_path()}/data/namespaces/{namespace or self.namespace}/{filename}'

    def _load_words(self, namespace=None):
        words = set()
        with open(self._get_path('words.txt', namespace)) as f:
            for word in f.readlines():
                words.add(word.strip())
        words.discard('')
        return words

    def _load_simple_words(self, namespace=None):
        words = list()
        with open(self._get_path('words.txt', namespace)) as f:
            for word in f.readlines():
                words.append(word.strip())
        return words

    def _load_with_exclusion(self):
        words = self._load_words()
        self.stats['raw_words_before_exclusion'] = len(words)
        for namespace in EXCLUDE_WORDS_FROM:
            ex = self._load_words(namespace)
            words -= ex
            self.stats[f'words_from_{namespace}'] = len(ex)
        self.stats['raw_words_after_exclusion'] = len(words)
        return sorted(words)

    def _create_card(self, word):
        response = self.translator(word)
        if not response:
            print(f'skipping: {word}')
            return
        card = self.card_creator.create_card(word, response)
        CardEnricher.enrich(card)
        anki_card = AnkiCardCreator.create_card(card)
        if not anki_card:
            print(f'empty card for: {word}')
        if len(card.too_similar) > 1:
            # print(f'too similar: {word}, {card.too_similar}')
            self.stats['has_too_similar'] += 1
            self.stats['too_similar_count'] += len(card.too_similar)
        if not card.translations:
            print(f'No translations for: {word}')
            self.stats['no_translation_count'] += 1
        else:
            self.stats['success_count'] += 1
        return anki_card

    def _create_anki_cards(self, words):
        for word in words:
            while True:
                try:
                    if card := self._create_card(word):
                        yield card
                except HTTPError as ex:
                    if ex.args[0] == 429:
                        print('Too many requests, sleeping')
                        time.sleep(60)
                        continue
                    traceback.print_exc()
                except Exception as ex:
                    if 'Network is unreachable' in str(ex):
                        print('Network is unreachable')
                        time.sleep(3)
                        continue
                    traceback.print_exc()
                break

    def run(self):
        # words = self._load_with_exclusion()
        words = self._load_simple_words()
        print(f'Loaded {len(words)} words: {" ".join(words[:10])}...')
        try:
            with open(self._get_path('anki.cards'), 'w') as out:
                for card in self._create_anki_cards(words):
                    if card:
                        out.write(card + '\n')
                        print(f'Created: {card}')
        finally:
            self.translator.close()
            print(self.stats)
            print(AnkiCardCreator.pos)


if __name__ == '__main__':
    BatchTranslator(NAMESPACE).run()
