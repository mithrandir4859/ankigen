from collections import Counter

import nltk
import transliterate

from site_generator import get_repo_path


def get_texts(response):
    texts = set()
    if isinstance(response, dict):
        if text := response.get('Text'):
            texts.add(text)
        for key, value in response.items():
            texts.update(get_texts(value))
    elif isinstance(response, list):
        for item in response:
            texts.update(get_texts(item))
    return texts


def relevant(text: str):
    text = text.strip()
    if len(text) <= 4:
        return
    elif len(text) <= 5 and text[-1] == '.' and text[:-1].isalpha():
        return
    elif not has_enough_letters(text):
        return
    elif not comma_separated_phrases(text):
        return
    return True


def has_enough_letters(text, target=5):
    count = 0
    for letter in text:
        if letter.isalpha():
            count += 1
            if count >= target:
                return True


def comma_separated_phrases(text):
    for chunk in text.split(', '):
        if not chunk.replace(' ', '').isalpha():
            return
    return True


def get_filtered(texts):
    return {t for t in texts if relevant(t)}


def expand(texts):
    expanded = set()
    for text in texts:
        expanded.update(text.split(', '))
    return expanded


def split_languages(texts):
    ru = set()
    eng = set()
    for text in texts:
        if transliterate.translit(text, 'ru') == text:
            ru.add(text)
        else:
            eng.add(text)
    return ru, eng


def get_distance(t1, t2):
    return 100 * nltk.edit_distance(t1, t2) / max(min(len(t1), len(t2)), 1)


def get_distance_translit(eng, ru):
    assert transliterate.translit(ru, 'ru') == ru, ru
    eng_to_ru = transliterate.translit(eng, 'ru')
    distance1 = nltk.edit_distance(eng_to_ru, ru) / len(min(eng_to_ru, ru))

    ru_to_eng = transliterate.translit(ru, 'ru', reversed=True)
    distance2 = nltk.edit_distance(eng, ru_to_eng) / len(min(ru_to_eng, eng))
    return min(distance1, distance2)


def remove_near_duplicates_within(words):
    result = set(words)
    for main_word in sorted(words, key=lambda w: (len(w), w)):
        if main_word not in result:
            # already removed
            continue
        for secondary_word in list(result - {main_word}):
            if main_word[:-1] in secondary_word:
                result.remove(secondary_word)
    return result


def remove_near_duplicates(eng_synonyms, eng_word, threshold=40):
    filtered = set()
    for synonym in eng_synonyms:
        if get_distance(synonym, eng_word) <= threshold or contains(synonym, eng_word):
            continue
        filtered.add(synonym)
    return filtered


def contains(a, b):
    return a[:-1] in b or b[:-1] in a


def remove_near_duplicates_translit(ru_texts, eng_word, threshold=40):
    filtered = set()
    for ru_word in ru_texts:
        eng_to_ru = transliterate.translit(eng_word, 'ru')
        ru_to_eng = transliterate.translit(ru_word, 'ru', reversed=True)
        if min(get_distance(ru_word, eng_to_ru), get_distance(ru_to_eng, eng_word)) <= threshold:
            continue
        elif contains(eng_to_ru, ru_word) or contains(ru_to_eng, eng_word):
            continue
        filtered.add(ru_word)
    return filtered


def extract_card_pieces(word, response):
    texts = get_filtered(get_texts(response))
    texts = expand(texts)
    ru, eng = split_languages(texts)
    eng = remove_near_duplicates(eng, word)
    ru = remove_near_duplicates_translit(ru, word)
    eng = remove_near_duplicates_within(eng)
    ru = remove_near_duplicates_within(ru)
    return word, ru, eng


def main():
    from main import CachingProxyTranslator
    from _just_in_case.translation_lingvo import LingvoTranslator
    storage = CachingProxyTranslator(LingvoTranslator.create_instance()).storage

    counter = Counter()
    counter['total'] = len(storage)
    print(len(storage))

    with open(f'{get_repo_path()}/data/ankigen_output/variants.anki', 'w') as out:
        for word, response in storage.items():
            word, ru, eng = extract_card_pieces(word, response)
            if ru:
                counter['translated'] += 1
                counter['total_variants'] += len(ru | eng)
                out.write(word + '\n')
                out.write('; '.join(sorted(ru)) + '\n')
                out.write('; '.join(sorted(eng)) + '\n' * 2)
            else:
                counter['no_translation'] += 1
    print(counter)
    print('avg', counter['total_variants'] / counter['translated'])


if __name__ == '__main__':
    main()
