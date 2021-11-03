from collections import defaultdict

from googletrans import Translator
from requests import HTTPError

from entities import DictionaryCard, Translation, Synonym
from src.utils import get_near_duplicates, get_near_duplicates_translit, remove_near_duplicates_within


class GoogleTranslator:
    def __init__(self):
        self.translator = Translator()

    def __call__(self, text):
        assert text, text
        result = self.translator.translate(text, dest='ru', src='en')
        response = result._response
        if response.is_error:
            raise HTTPError(response.status_code, response)
        return response.json()


class AnkiCardCreator:
    pos = set()

    @classmethod
    def _get_words(cls, translations, card):
        translations_before = [t for t in translations if t.word not in card.too_similar]
        translations_deduplicated = remove_near_duplicates_within([t.word for t in translations_before])
        if len(translations_before) - len(translations_deduplicated) > 4:
            print('before:', [t.word for t in translations_before])
        words = list()
        for translation in translations:
            if translation.word not in translations_deduplicated:
                continue
            text = translation.word
            if translation.confidence and translation.confidence > 1:
                text += f' ({translation.confidence})'
            words.append(text)
            if len(words) >= 5:
                break
        return words

    @classmethod
    def create_card(cls, card: DictionaryCard) -> (str, None):
        pos_translations = defaultdict(list)
        for translation in card.translations:
            pos_translations[translation.pos].append(translation)
            cls.pos.add(translation.pos)
        anki_note_lines = list()
        for pos, translations in pos_translations.items():
            if translations := cls._get_words(translations, card):
                anki_note_lines.append(', '.join(translations))
        if not anki_note_lines:
            return
        synonyms = ', '.join(remove_near_duplicates_within(
            [s.word for s in card.synonyms if s.word not in card.too_similar]
        ))
        card = f'{card.word}\t'
        for line in anki_note_lines:
            card += f'<div>{line}</div>'
        if synonyms:
            card += '<br />'
            card += f'<div>synonyms: {synonyms}</div>'

        return card


class GoogleResponseParser:
    @classmethod
    def _get_safely(cls, a_list, index, default=None):
        if len(a_list) > index:
            return a_list[index]
        return default

    @classmethod
    def _get_translations(cls, response: list):
        for translation in response[1] or list():
            pos = translation[0]
            for t in translation[2]:
                try:
                    word, back_translations, *_ = t
                except ValueError:
                    continue
                confidence = cls._get_safely(t, index=3, default=1)
                yield Translation(
                    word=word,
                    confidence=max((confidence or 0) * 1000, 1),
                    back_translations=back_translations,
                    pos=pos
                )

    @classmethod
    def _get_translations_less_nice(cls, response: list):
        for item0 in response[5] or list():
            for item3 in item0[2]:
                yield Translation(word=item3[0])

    @classmethod
    def create_card(cls, initial_word: str, response: list) -> DictionaryCard:
        card = DictionaryCard(word=initial_word)
        for func in [
            cls._get_translations,
            cls._get_translations_less_nice
        ]:
            # noinspection PyArgumentList
            card.translations += func(response)
            if card.translations:
                break

        if len(response) > 11:
            for pos, synonyms, _ in response[11] or list():
                for synonyms2 in synonyms:
                    for synonym in synonyms2[0]:
                        card.synonyms.append(Synonym(pos=pos, word=synonym))

        if len(response) > 13:
            for example in response[13] or list():
                for example in example:
                    card.examples.append(example[0])

        return card


class CardEnricher:
    @classmethod
    def enrich(cls, card: DictionaryCard):
        card.too_similar.update(get_near_duplicates({s.word for s in card.synonyms}, card.word))
        card.too_similar.update(get_near_duplicates_translit(
            ru_words=[t.word for t in card.translations], eng_word=card.word
        ))
        # card.too_similar.discard(card.word)


if __name__ == '__main__':
    import json

    print(json.dumps(GoogleTranslator()('irrefutable'), indent=4, ensure_ascii=False))
