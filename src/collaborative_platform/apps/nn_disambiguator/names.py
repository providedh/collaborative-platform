import difflib
import editdistance
import fuzzy
import spacy

nlp = spacy.load('en_core_web_lg')


def ratcliff_obershelp_sim(s1: str, s2: str) -> float:
    if s1 is None or s2 is None: return -1.
    if s1 == s2: return 1.
    return difflib.SequenceMatcher(None, s1, s2).ratio()


def phonetics_sim(s1: str, s2: str) -> int:
    if s1 is None or s2 is None: return -1
    if s1 == s2: return 0
    return editdistance.eval(fuzzy.nysiis(s1), fuzzy.nysiis(s2))


def levenshtein_distance(s1: str, s2: str) -> int:
    if s1 is None or s2 is None: return -1
    return editdistance.eval(s1, s2)


def nlp_sim(s1: str, s2: str) -> float:
    if s1 and s2:
        s1 = nlp(s1)
        s2 = nlp(s2)
        if s1.vector_norm and s2.vector_norm:
            return s1.similarity(s2)
    return 0
