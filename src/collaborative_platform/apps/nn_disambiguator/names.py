import difflib
import editdistance
import fuzzy
import spacy

nlp = spacy.load('en_core_web_lg')


def ratcliff_obershelp_sim(s1: str, s2: str):
    if s1 == s2: return 0
    return difflib.SequenceMatcher(None, s1, s2).ratio()


def phonetics_sim(s1: str, s2: str):
    if s1 == s2: return 0
    return editdistance.eval(fuzzy.nysiis(s1), fuzzy.nysiis(s2))


def levenshtein_distance(s1: str, s2: str):
    if s1 is None or s2 is None: return -1
    return editdistance.eval(s1, s2)


def nlp_sim(s1: str, s2: str):
    tokens = nlp(f"{s1} {s2}")
    avsim = 0
    tokens_num_h = len(tokens) // 2
    for i in range(0, tokens_num_h):
        avsim += tokens[i].similarity(tokens[i + tokens_num_h])
    avsim /= tokens_num_h
    return avsim
