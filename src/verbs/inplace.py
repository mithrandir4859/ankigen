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


def main():
    verbs = list(load_verbs())
    print(f'Found {len(verbs)} verbs')
    verbs_filepath = f'{get_repo_path()}/data/pt_verbs_cards.txt'
    with open(verbs_filepath, 'w') as out:
        for card in create_cards(verbs):
            out.write(card + '\n')
            print(card)


if __name__ == '__main__':
    main()
