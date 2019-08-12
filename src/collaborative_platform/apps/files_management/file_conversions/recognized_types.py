from enum import Enum


class FileType(Enum):
    XML = 1
    CSV = 2
    TSV = 3
    OTHER = 99


class XMLType(Enum):
    TEI_P5 = 1
    TEI_P4 = 2
    OTHER = 99
