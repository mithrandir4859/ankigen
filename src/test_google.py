import pytest

from google import GoogleResponseParser, GoogleTranslator


class TestGoogleResponseParser:
    @pytest.fixture
    def parser(self):
        return GoogleResponseParser()

    @pytest.fixture(scope='module')
    def translator(self):
        return GoogleTranslator()

    # def test_allusions_api(self, translator):
    #     response = translator('allusions')
    #
    #     assert response

    def test_allusions(self, parser):
        json_response = [
            [['намёки', 'allusions', None, None, 3, None, None, [[]],
              [[['cce7c67b3f2439089dd6b428e0b83b88', 'en_ru_2020q2.md']]]
              ], [None, None, 'namoki']], None, 'en', None, None, [
                ['allusions', None, [['намёки', 0, True, False, [3]], ['аллюзии', 0, True, False, [8]]],
                 [[0, 9]], 'allusions', 0, 0]], 0.7109375, [], [['en'], None, [0.7109375], ['en']], None,
            None, None, None, None, [['allusion']]
        ]

        card = parser.create_card('allusions', json_response)

        assert 'намёки' in {t.word for t in card.translations}
        assert 'аллюзии' in {t.word for t in card.translations}

    def test_beringed(self, parser):
        json_response = [
            [['беринг', 'beringed', None, None, 3, None, None, [[]],
              [[['cce7c67b3f2439089dd6b428e0b83b88', 'en_ru_2020q2.md']]]], [None, None, 'bering']], None,
            'en', None, None, [['beringed', None,
                                [['беринг', 0, True, False, [3]], ['взбалтывается', 0, True, False, [8]]],
                                [[0, 8]], 'beringed', 0, 0]], 0.28912842, [],
            [['en'], None, [0.28912842], ['en']]
        ]

        card = parser.create_card('beringed', json_response)

        assert card.translations

        assert 'взбалтывается' in {t.word for t in card.translations}
        assert 'беринг' in {t.word for t in card.translations}
