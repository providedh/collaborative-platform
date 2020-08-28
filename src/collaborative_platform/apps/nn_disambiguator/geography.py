from typing import Tuple

import geopy.distance
from geopy import Nominatim

g = Nominatim(user_agent="PROVIDEDH Collaborative Platform")


def coordinates(query: str) -> Tuple[float, float]:
    res = g.geocode(query)
    if res is None:
        return 0., 0.
    _, coords = res
    return coords


def distance(p1, p2):
    return geopy.distance.distance(p1, p2).km


def names_to_distance(q1: str, q2: str):
    return distance(coordinates(q1), coordinates(q2))
