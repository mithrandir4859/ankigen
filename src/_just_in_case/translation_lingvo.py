import requests

from config_gitignored import LINGVO_API_KEY
from _just_in_case.lingvo_demo import extract_card_pieces

SERVICE_URL = 'https://developers.lingvolive.com/'


class LingvoTranslator:
    @classmethod
    def create_instance(cls):
        resp = requests.post(
            f'{SERVICE_URL}/api/v1.1/authenticate',
            headers={
                'Authorization': f'Basic {LINGVO_API_KEY}',
            }
        )
        print(resp.status_code)
        return cls(resp.text)

    def __init__(self, api_token):
        assert api_token, api_token
        self.api_token = api_token

    def __call__(self, word):
        resp = requests.get(
            f'{SERVICE_URL}/api/v1/Translation?text={word}&srcLang=1033&dstLang=1049&isCaseSensitive=False',
            headers={
                'Authorization': f'Bearer {self.api_token}',
            }
        )
        if not resp.ok:
            return dict(
                status='failed',
                status_code=resp.status_code,
                json=resp.json(),
            )
        return resp.json()


class BetterLingvoCardCreator:
    @staticmethod
    def create_card(word, response):
        if isinstance(response, dict) and response.get('status') == 'failed':
            return
        word, ru, eng = extract_card_pieces(word, response)
        if ru:
            return f'{word} ***\n{"; ".join(ru)}\n{"; ".join(eng)}\n\n'


class LingvoCardCreator:
    def create_card(self, response):
        if isinstance(response, dict) and response.get('status') == 'failed':
            return
        entry = self._get_entry(response)
        if not entry:
            raise ValueError(response)
        return self._get_translation(entry)

    @staticmethod
    def _get_entry(entries, dictionary='LingvoUniversal (En-Ru)'):
        for entry in entries:
            if entry.get('Dictionary') == dictionary:
                return entry

    @staticmethod
    def _get_translation(entry):
        translations = []
        for item0 in entry.get('Body', list()):
            for item1 in item0.get('Markup', list()):
                candidate_translation = (item1.get('Text') or '').strip()
                letters = [letter for letter in candidate_translation if letter.isalpha()]
                if item1.get('Node') == 'Text' and len(letters) > 2:
                    translations.append(candidate_translation)
        return translations


if __name__ == '__main__':
    translator = LingvoTranslator.create_instance()
    print(translator('unquestionable'))
