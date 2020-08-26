import re
import sys
from datetime import datetime
from typing import Optional

import maya
from timefhuman import timefhuman


def to_datetime(text: str) -> Optional[datetime]:
    text = re.sub("([0-9]+)_([0-9]+?)_([0-9]+)", r"\1/\2/\3", text)
    text = re.sub("([0-9]+)_([0-9]+)", r"\1:\2", text)

    try:
        dt_maya = maya.parse(text).datetime()
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


def days_apart(d1, d2) -> int:
    if type(d1) == str:
        d1 = to_datetime(d1)
        if d1 is None:
            return sys.maxsize
    if type(d2) == str:
        d2 = to_datetime(d2)
        if d2 is None:
            return sys.maxsize

    try:
        return abs(d1 - d2).days
    except:
        return sys.maxsize


def seconds_apart(t1, t2) -> int:
    if type(t1) == str:
        t1 = to_datetime(t1)
        if t1 is None:
            return sys.maxsize
    if type(t2) == str:
        t2 = to_datetime(t2)
        if t2 is None:
            return sys.maxsize

    d = datetime.min
    d1 = d.replace(hour=t1.hour, minute=t1.minute, second=t1.second)
    d2 = d.replace(hour=t2.hour, minute=t2.minute, second=t2.second)
    return abs(d1 - d2).seconds
