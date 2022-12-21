import os
import subprocess

import nltk
import transliterate


def get_repo_path(repo_name='ankigen'):
    abs_path = os.path.dirname(os.path.abspath(__file__))
    join_abs_path = abs_path.split(os.sep)
    path_to_data_list = join_abs_path[:join_abs_path.index(repo_name) + 1]
    return os.sep.join(path_to_data_list)


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
    return sorted(result, key=lambda word: words.index(word))


def get_near_duplicates(synonyms, word, threshold=40):
    for synonym in synonyms:
        if get_distance(synonym, word) <= threshold or contains(synonym, word):
            yield word


def contains(a, b):
    return a[:-1] in b or b[:-1] in a


def get_near_duplicates_translit(ru_words, eng_word, threshold=40):
    eng_to_ru = transliterate.translit(eng_word, 'ru')
    for ru_word in ru_words:
        ru_to_eng = transliterate.translit(ru_word, 'ru', reversed=True)
        if min(get_distance(ru_word, eng_to_ru), get_distance(ru_to_eng, eng_word)) <= threshold:
            yield ru_word
        elif contains(eng_to_ru, ru_word) or contains(ru_to_eng, eng_word):
            yield ru_word


def pronounce(text):
    command = 'espeak  -s 155 -a 200'.split()
    command.append(text)
    subprocess.run(command)


def chunker(seq, size):
    return list(seq[pos:pos + size] for pos in range(0, len(seq), size))


if __name__ == '__main__':
    pronounce('you gotta be kidding me')
