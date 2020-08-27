import re
import sys
from typing import Optional, Union
from datetime import datetime
import maya
from timefhuman import timefhuman

max_seconds_apart = 24 * 60 * 60
max_days_apart = 365 * 1000


def to_datetime(text: str) -> Optional[datetime]:
    text = re.sub("([0-9]+)_([0-9]+?)_([0-9]+)", r"\1/\2/\3", text)
    text = re.sub("([0-9]+)_([0-9]+)", r"\1:\2", text)

    try:
        dt_maya = maya.parse(text).datetime().replace(tzinfo=None)
        if not dt_maya:
            raise Exception
        return dt_maya
    except:
        try:
            dt_tfh = timefhuman(text)
            if type(dt_tfh) == list:
                return dt_tfh[0]
            else:
                return dt_tfh
        except:
            return None


def days_apart(d1: Union[datetime, str], d2: Union[datetime, str]) -> int:
    if type(d1) == str:
        d1 = to_datetime(d1)
        if d1 is None:
            return max_days_apart
    if type(d2) == str:
        d2 = to_datetime(d2)
        if d2 is None:
            return max_days_apart

    try:
        return abs(d1 - d2).days
    except:
        return max_days_apart


def seconds_apart(t1: Union[datetime.time, str], t2: Union[datetime.time, str]) -> int:
    if type(t1) == str:
        t1 = to_datetime(t1)
        if t1 is None:
            return max_seconds_apart
    if type(t2) == str:
        t2 = to_datetime(t2)
        if t2 is None:
            return max_seconds_apart

    d = datetime.min
    d1 = d.replace(hour=t1.hour, minute=t1.minute, second=t1.second)
    d2 = d.replace(hour=t2.hour, minute=t2.minute, second=t2.second)
    return abs(d1 - d2).seconds
