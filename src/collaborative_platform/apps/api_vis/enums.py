from datetime import date, time
from enum import Enum

from django.contrib.gis.geos import Point


class TypeChoice(Enum):
    str = str
    int = int
    float = float
    date = date
    time = time
    point = Point
