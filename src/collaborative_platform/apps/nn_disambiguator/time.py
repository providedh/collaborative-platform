import sys
from datetime import datetime
from timefhuman import timefhuman


def days_apart(d1, d2):
    if type(d1) == str:
        try:
            d1 = timefhuman(d1)
        except:
            return sys.maxsize
    if type(d2) == str:
        try:
            d2 = timefhuman(d2)
        except:
            return sys.maxsize

    if type(d1) == list and type(d2) == list:
        return min(
            abs(d1[0] - d2[0]).days,
            abs(d1[0] - d2[1]).days,
            abs(d1[1] - d2[0]).days,
            abs(d1[1] - d2[1]).days,
        )
    elif type(d1) == list:
        return min(
            abs(d1[0] - d2).days,
            abs(d1[1] - d2).days,
        )
    elif type(d2) == list:
        return min(
            abs(d1 - d2[0]).days,
            abs(d1 - d2[1]).days,
        )

    try:
        return abs(d1 - d2).days
    except:
        return sys.maxsize


def seconds_apart(t1, t2):
    if type(t1) == str:
        try:
            t1 = timefhuman(t1)
        except:
            return sys.maxsize
    if type(t2) == str:
        try:
            t2 = timefhuman(t2)
        except:
            return sys.maxsize

    d = datetime.min
    d1 = d.replace(hour=t1.hour, minute=t1.minute, second=t1.second)
    d2 = d.replace(hour=t1.hour, minute=t1.minute, second=t1.second)
    return abs(d1 - d2).seconds
