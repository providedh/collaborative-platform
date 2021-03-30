from apps.nn_disambiguator.geography import *
import pytest


@pytest.mark.django_db
class TestGeography:
    def test_coordinates(self):
        assert coordinates("Salamanca, ES") == (40.9651572, -5.6640182)
        assert coordinates("Warsaw, PL") == (52.2319581, 21.0067249)

    def test_distance(self):
        assert distance((0, 0), (0, 0)) == 0.
        assert 7521 < distance((0, 0), (52, 52)) < 7522

    def test_names_to_distance(self):
        assert 2376 < names_to_distance("Salamanca, ES", "Warsaw, PL") < 2382
