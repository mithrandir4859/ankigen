import string
from collections import Counter

with open('/home/irrefutable/Projects/ankigen/data/traffic_rules_portuguese.txt', 'r') as f:
    rules = f.read()

print(len(rules.split()))

words = [
    w.strip().lower() for w in rules.split() if w.strip() and not w.strip().isdigit()
]

translate_table = dict((ord(char), None) for char in string.punctuation)

words = [
    w.translate(translate_table) for w in words
]


def proper_word(w: str):
    for letter in w:
        if letter.isdigit():
            return False
    alpha = 0
    for letter in w:
        if letter.isalpha():
            alpha += 1
    if alpha < 2:
        return False
    return True


words = [w for w in words if proper_word(w)]

harry_potter_words = 76944
print(len(words) * 100 / harry_potter_words)

word_counter = Counter(words)
print(f'Unique words: {len(word_counter)}')

frequent_words = 0
print(len(word_counter) / 100)
for word, count in word_counter.most_common():
    if count > 2:
        frequent_words += 1
        # print(count, word)
        print(word)
print(f'Frequent words: {frequent_words}')