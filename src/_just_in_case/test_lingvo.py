import pytest

from main import CachingProxyTranslator
from _just_in_case.translation_lingvo import LingvoTranslator


class TestLingvoCardCreator:
    @pytest.fixture
    def translator(self):
        return CachingProxyTranslator(LingvoTranslator.create_instance())

    def test_basic(self, translator):
        response = translator('abomination')
        assert response


