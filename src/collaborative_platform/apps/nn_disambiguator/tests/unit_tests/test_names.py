import pytest

from apps.nn_disambiguator.names import *


class TestNames:
    def test_ratcliff_obershelp_sim(self):
        assert ratcliff_obershelp_sim('a', 'a') == 1.
        assert ratcliff_obershelp_sim('a', 'b') == 0.
        assert 0.11 < ratcliff_obershelp_sim('Ratcliff', 'Obershelp') < 0.12

    def test_phonetics_sim(self):
        assert phonetics_sim('a', 'a') == 0
        assert phonetics_sim('a', 'b') == 1
        assert phonetics_sim('phonetics', 'similarity') == 6

    def test_levenshtein_distance(self):
        assert levenshtein_distance('a', 'a') == 0
        assert levenshtein_distance('a', 'b') == 1
        assert levenshtein_distance('levenshtein', 'distance') == 10

    def test_nlp_sim(self):
        assert nlp_sim('a', 'a') == 1.
        assert 0.25 < nlp_sim('Amber', 'Zebra') < 0.26
        assert 0.84 < nlp_sim("James Bond Junior", "Jamie Bond Jr.") < 0.85
