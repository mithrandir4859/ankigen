import uuid
from typing import Dict

import nltk
import requests
from transliterate import translit

from config_gitignored import MICROSOFT_SUBSCRIPTION_KEY
from entities import DictionaryCard, Translation

MICROSOFT_BASE_PATH = 'https://api.cognitive.microsofttranslator.com'


class MicrosoftTranslator:
    @classmethod
    def create_instance(cls):
        return cls(MICROSOFT_SUBSCRIPTION_KEY)

    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {
            'Ocp-Apim-Subscription-Key': api_token,
            'Ocp-Apim-Subscription-Region': 'global',
            'Content-type': 'application/json',
        }
        self.params = {
            'api-version': '3.0',
            'from': 'en',
            'to': ['ru', ]
        }

    def __call__(self, word):
        return self.translate([word])[word]

    def translate(self, words) -> Dict[str, DictionaryCard]:
        response = requests.post(
            f'{MICROSOFT_BASE_PATH}/dictionary/lookup?api-version=3.0', params=self.params,
            headers={
                **self.headers,
                'X-ClientTraceId': str(uuid.uuid4())
            }, json=[{'text': word} for word in words]
        )
        if not response.ok:
            raise Exception(f'Failed to translate: {words}')
        response = response.json()
        result = dict()
        if len(response) != len(words):
            raise ValueError(f'res={len(response)}, words={len(words)}')
        for requested_word, card_json in zip(words, response):
            word = card_json['displaySource']
            normalized_word = card_json['normalizedSource']
            card = DictionaryCard(
                requested_word=requested_word,
                word=word,
                normalized_word=None if normalized_word.lower() == word else normalized_word,
                raw=card_json
            )
            for translation_json in card_json['translations']:
                translation = Translation(
                    word=translation_json['displayTarget'],
                    confidence=round(translation_json['confidence'] * 100)
                )
                for back_translation in translation_json['backTranslations']:
                    translation.back_translations.append(back_translation['displayText'])
                card.translations.append(translation)
            result[requested_word] = card
        return result


class MicrosoftCardCreator:
    @staticmethod
    def _get_distance(source, translation):
        distances = [
            nltk.edit_distance(translit(source, 'ru'), translation),
            nltk.edit_distance(source, translit(translation, 'ru', reversed=True)),
        ]
        return round(200 * min(distances) / (len(source) + len(translation)))

    @classmethod
    def create_card(cls, dictionary_card: DictionaryCard):
        source = dictionary_card.word
        translations = list()
        synonyms = list()
        dictionary_card.translations = sorted(dictionary_card.translations, key=lambda t: (-t.confidence, t.word))
        for t in dictionary_card.translations[:5]:
            distance = cls._get_distance(source, t.word)
            if distance < 40:
                print(f'Ignoring {t.word} for {source} because distance={distance} is too low')
                continue

            translations.append(t.word)
            for back_t in t.back_translations:
                if len(synonyms) > 5:
                    break
                if back_t not in synonyms and back_t != source:
                    synonyms.append(back_t)
        if translations:
            translations = f'<div>{", ".join(translations)}</div>'
            synonyms = f'<div>{", ".join(synonyms)}</div>'
            return f'{source}\t{translations + synonyms}'


if __name__ == '__main__':
    translator = MicrosoftTranslator.create_instance()
    r = translator.translate(['unquestionable', 'irrefutable', 'fasdfsdf'])
    print(r)
    print(translator('consciousness'))
