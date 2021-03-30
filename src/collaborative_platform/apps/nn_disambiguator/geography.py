import sys
from typing import Tuple

import geopy.distance
from django.db.models import Q
from geopy import Nominatim

from apps.nn_disambiguator.models import APIRequestCache

g = Nominatim(user_agent="PROVIDEDH Collaborative Platform")


def coordinates(query: str) -> Tuple[float, float]:
    if query is None:
        return 0., 0.
    cache, created = APIRequestCache.objects.filter(p1=query).get_or_create()
    if created:
        res = g.geocode(query)
        if res is None:
            return 0., 0.
        _, coords = res
        cache.p1 = query
        cache.result = coords
        cache.save()

    return cache.result


def distance(p1, p2):
    if p1 is None or p2 is None:
        return sys.maxsize
    cache, created = APIRequestCache.objects.filter((Q(p1=p1) & Q(p2=p2)) | (Q(p1=p2) & Q(p2=p1))).get_or_create()
    if created:
        cache.p1 = p1
        cache.p2 = p2
        cache.result = geopy.distance.distance(p1, p2).km
        cache.save()
    return cache.result


def names_to_distance(q1: str, q2: str):
    if q1 is None or q2 is None:
        return sys.maxsize
    cache, created = APIRequestCache.objects.filter((Q(p1=q1) & Q(p2=q2)) | (Q(p1=q2) & Q(p2=q1))).get_or_create()
    if created:
        cache.p1 = q1
        cache.p2 = q2
        cache.result = distance(coordinates(q1), coordinates(q2))
        cache.save()
    return cache.result
