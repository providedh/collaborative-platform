import geopy.distance
from geopy import Nominatim

from collaborative_platform import settings

g = Nominatim(user_agent="PROVIDEDH Collaborative Platform")


def coordinates(query: str):
    res = g.geocode(query)
    if res is None:
        return 0, 0
    _, coords = res
    return coords


def distance(p1, p2):
    return geopy.distance.distance(p1, p2).km


def names_to_distance(q1: str, q2: str):
    return distance(coordinates(q1), coordinates(q2))


if __name__ == "__main__":
    c1 = coordinates("Salamanca, ES")
    c2 = coordinates("Warsaw, PL")
    print(c1)
    print(c2)
    print(distance(c1, c2))
