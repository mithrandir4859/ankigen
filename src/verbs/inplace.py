from collections import defaultdict
from typing import Dict

from pydantic import BaseModel, Field

from utils import get_repo_path


class Verb(BaseModel):
    word: str
    pronoun_forms: Dict[str, str] = Field(default_factory=dict)


def load_verbs():
    verbs_filepath = f'{get_repo_path()}/data/pt_verbs.txt'
    with open(verbs_filepath, 'r') as f:
        verbs = f.read()

    for raw_verb in verbs.split('-'):
        raw_verb = raw_verb.strip()
        if not raw_verb:
            continue
        lines = raw_verb.split('\n')
        assert len(lines) == 8
        verb = Verb(word=lines[0].strip().lower())
        for line in lines[1:]:
            form = line.split()[-1]
            noun = line.replace(form, '').replace(' ', '').strip()
            verb.pronoun_forms[noun] = form
        yield verb


def create_cards(verbs):
    for verb in verbs:
        for noun, form in verb.pronoun_forms.items():
            card = f'{verb.word}: {noun}\t'
            card += f'<div>{noun} <b>{form}</b></div>'
            yield card


def create_comparative_table(verbs):
    row_dicts = defaultdict(dict)
    for verb in verbs:
        for pronoun, form in verb.pronoun_forms.items():
            row_dicts[verb.word][pronoun] = form
    header = ['eu', 'tu', 'ele/ela', 'você', 'nós', 'eles/elas', 'vocês', ]
    row_lists = [[''] + header]
    for main_form, row_dict in row_dicts.items():
        row_lists.append([main_form] + [row_dict[k] for k in header])
    return row_lists


def main():
    verbs = list(load_verbs())
    print(f'Found {len(verbs)} verbs')
    verbs_filepath = f'{get_repo_path()}/data/pt_verbs_cards.txt'
    with open(verbs_filepath, 'w') as out:
        for card in create_cards(verbs):
            out.write(card + '\n')
    verbs_filepath = f'{get_repo_path()}/data/pt_verbs_comparative.csv'
    with open(verbs_filepath, 'w') as out:
        for row in create_comparative_table(verbs):
            out.write(','.join(row) + '\n')


if __name__ == '__main__':
    main()
