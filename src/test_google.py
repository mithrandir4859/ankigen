import pytest

from google import GoogleResponseParser, GoogleTranslator


class TestGoogleResponseParser:
    @pytest.fixture
    def parser(self):
        return GoogleResponseParser()

    @pytest.fixture(scope='module')
    def translator(self):
        return GoogleTranslator()

    def test_allusions_api(self, translator):
        response = translator('stirred')

        assert response

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


class TestGoogleResponseParserPortuguese:
    @pytest.fixture
    def parser(self):
        return GoogleResponseParser()

    @pytest.fixture(scope='module')
    def translator(self):
        return GoogleTranslator(dest='ru', src='pt')

    def test_menina(self, translator):
        response = translator('menina')

        assert response == [[['девочка', 'menina', None, None, 10], [None, None, 'devochka']], None, 'pt', None, None, [
            ['menina', None, [['девочка', 0, True, False, [10]], ['девушка', 0, True, False, [11]]], [[0, 6]], 'menina',
             0, 0]], 1, [], [['pt'], None, [1], ['pt']], None, None, [['имя существительное', [
            [['garota', 'moça', 'mulher', 'brasa', 'rapariga'], ''],
            [['garota', 'mulher', 'namorada', 'amante', 'rapariga'], ''],
            [['devassa', 'prostituta', 'mulher da vida', 'puta', 'rapariga'], ''],
            [['senhorita', 'garota', 'moça', 'rapariga'], '']], 'menina']], None, None, [['menino']]]


class TestGoogleResponseParserPortuguese2:
    @pytest.fixture
    def parser(self):
        return GoogleResponseParser()

    @pytest.fixture(scope='module')
    def translator(self):
        return GoogleTranslator(dest='uk', src='pt')

    def test_menina(self, translator, parser):
        response = translator('menina')

        assert response == [[['дівчина', 'menina', None, None, 11, None, None, [[]],
                              [[['ac6faa6f1887d7a3559f8fc4a759008a', 'tea_SouthSlavicA_en2bebsbghrsrsluk_2021q3.md']]]],
                             [None, None, 'divchyna']], None, 'pt', None, None, [['menina', None,
                                                                                  [['дівчина', 0, True, False, [11]],
                                                                                   ['дівчинка', 0, True, False, [11]]],
                                                                                  [[0, 6]], 'menina', 0, 0]], 1, [],
                            [['pt'], None, [1], ['pt']], None, None, [['іменник', [
                [['garota', 'moça', 'mulher', 'brasa', 'rapariga'], ''],
                [['garota', 'mulher', 'namorada', 'amante', 'rapariga'], ''],
                [['devassa', 'prostituta', 'mulher da vida', 'puta', 'rapariga'], ''],
                [['senhorita', 'garota', 'moça', 'rapariga'], '']], 'menina']], None, None, [['menino']]]

        card = parser.create_card('menina', response)

        assert {'дівчинка', 'дівчина'} == {t.word for t in card.translations}
