import csv
import json
import math
from collections import Counter

from nltk import wordpunct_tokenize
from nltk.corpus import stopwords, words

from site_generator import get_repo_path

ENG_STOPWORDS = set(stopwords.words('english'))
ENG_WORDS = set(words.words())


class WordsExtractor:
    HEADER = 'word frequency'.split()
    ENDINGS = 'ing', 'ed', 's'

    @classmethod
    def create_instance(cls, source='dune'):
        return cls(source)

    def __init__(self, source):
        self.stats = Counter()
        self.frequency_base = None
        self.source = source

    def _get_word_wo_endings(self, word):
        for e in self.ENDINGS:
            if word.endswith(e):
                w = word[:-len(e)]
                if len(w) > 2 and w in ENG_WORDS and w not in ENG_STOPWORDS:
                    return w
        if word.endswith('ed') and word[:-1] in ENG_WORDS:
            return word[:-1]
        return word

    def _get_word_counter(self, text):
        self.stats['text_len'] = len(text)
        text = wordpunct_tokenize(text)
        self.stats['word_count'] = self.frequency_base = len(text)

        counter = Counter(text)
        self.stats['word_count_unique_initial'] = len(counter)

        normalized_counter = Counter()
        for word, count in counter.items():
            word = ''.join(letter for letter in word.lower() if letter.isalpha())
            if not word or word in ENG_STOPWORDS:
                continue
            if word not in normalized_counter:
                word = self._get_word_wo_endings(word)
            normalized_counter[word] += count
        self.stats['word_count_unique_post_normalization'] = len(normalized_counter)
        del counter
        self.stats['word_count_total_post_normalization'] = sum(normalized_counter.values())
        return normalized_counter

    def main(self):
        with open(f'{get_repo_path()}/data/{self.source}.txt') as f:
            text = f.read()
        counter = self._get_word_counter(text)
        del text
        self._store_words(counter)
        self._store_stats()

    def _get_frequency(self, count):
        return round(math.log2(count / self.frequency_base * 10e6))

    def _store_stats(self):
        with open(f'{get_repo_path()}/data/ankigen_output/{self.source}_stats.json', 'w') as out:
            print(json.dumps(self.stats, indent=4))
            json.dump(self.stats, out, indent=4)

    def _store_words(self, counter):
        with open(f'{get_repo_path()}/data/ankigen_output/{self.source}.txt', 'w') as out:
            out = csv.DictWriter(out, fieldnames=self.HEADER)
            out.writeheader()
            for word, count in sorted(counter.most_common(), key=lambda t: (-t[1], t[0])):
                row = dict(word=word, frequency=self._get_frequency(count))
                out.writerow(row)


if __name__ == '__main__':
    WordsExtractor.create_instance().main()
