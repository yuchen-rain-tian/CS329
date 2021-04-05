import glob
import os
from types import SimpleNamespace
from typing import Iterable, Tuple, Any, List, Set

import ahocorasick


def create_ac(data: Iterable[Tuple[str, Any]]) -> ahocorasick.Automaton:
    """
    Creates the Aho-Corasick automation and adds all (span, value) pairs in the data and finalizes this matcher.
    :param data: a collection of (span, value) pairs.
    """
    AC = ahocorasick.Automaton(ahocorasick.STORE_ANY)

    for span, value in data:
        if span in AC:
            t = AC.get(span)
        else:
            t = SimpleNamespace(span=span, values=set())
            AC.add_word(span, t)
        t.values.add(value)

    AC.make_automaton()
    return AC


def read_gazetteers(dirname: str) -> ahocorasick.Automaton:
    data = []
    for filename in glob.glob(os.path.join(dirname, '*.txt')):
        label = os.path.basename(filename)[:-4]
        for line in open(filename):
            data.append((line.strip(), label))
    return create_ac(data)


def match(AC: ahocorasick.Automaton, tokens: List[str]) -> List[Tuple[str, int, int, Set[str]]]:
    """
    :param AC: the finalized Aho-Corasick automation.
    :param tokens: the list of input tokens.
    :return: a list of tuples where each tuple consists of
             - span: str,
             - start token index (inclusive): int
             - end token index (exclusive): int
             - a set of values for the span: Set[str]
    """
    smap, emap, idx = dict(), dict(), 0
    for i, token in enumerate(tokens):
        smap[idx] = i
        idx += len(token)
        emap[idx] = i
        idx += 1

    # find matches
    text = ' '.join(tokens)
    spans = []
    for eidx, t in AC.iter(text):
        eidx += 1
        sidx = eidx - len(t.span)
        sidx = smap.get(sidx, None)
        eidx = emap.get(eidx, None)
        if sidx is None or eidx is None: continue
        spans.append((t.span, sidx, eidx + 1, t.values))

    return spans


def remove_overlaps(entities: List[Tuple[str, int, int, Set[str]]]) -> List[Tuple[str, int, int, Set[str]]]:
    overlaps = []
    tmp = []

    for index0, e0 in enumerate(entities):
        for index1, e1 in enumerate(entities):
            if index0 >= index1 or e0 in overlaps or e1 in overlaps: continue
            elif e0 == entities[0]:
                tmp.append(e0)
                tmp.append(e1)
                break
            elif e0[1] < e1[1] < e0[2]:
                if len(e0[0].split()) < len(e1[0].split()):
                    # print(e0, e1)
                    overlaps.append(e0)
                    tmp.append(e1)
                    break
                else: overlaps.append(e1)
            else:
                tmp.append(e1)
                break

    if len(entities) == 1:
        tmp.append(entities[0])
        return tmp

    for match0 in tmp:
        for match1 in tmp:
            if match0 == match1: continue
            if match0[1] <= match1[1] <= match0[2]:
                if match1[0].split() > match0[0].split():
                    tmp.remove(match0)

    return tmp


def to_bilou(tokens: List[str], entities: List[Tuple[str, int, int, str]]) -> List[str]:
    sentence = ' '.join(tokens)
    nertags = {}

    for match in entities:
        ner = str(list(match[3]))
        if len(match[0].split()) == 1:
            nertags[match[0]] = 'U-' + ner
        elif len(match[0].split()) == 2:
            nertags[match[0]] = 'B-' + ner + ' L-' + ner
        else:
            itag = (len(match[0].split()) - 2) * (' I-' + ner)
            nertags[match[0]] = 'B-' + ner + itag + ' L-' + ner

    for original, transformed in nertags.items():
        if original in sentence:
            sentence = sentence.replace(original, transformed)

    output = sentence.split()

    for unassigned in output:
        if output[output.index(unassigned)] == tokens[output.index(unassigned)]:
            output[output.index(unassigned)] = 'O'

    return output



if __name__ == '__main__':
    gaz_dir = 'dat/ner'
    AC = read_gazetteers('dat/ner')

    tokens = 'Jinho from United States of America lives in Atlantic City of Georgia and I live in South Korea'.split()
    entities = match(AC, tokens)
    entities = remove_overlaps(entities)
    tags = to_bilou(tokens, entities)
    print(entities)
    for token, tag in zip(tokens, tags):
        print(token, tag)