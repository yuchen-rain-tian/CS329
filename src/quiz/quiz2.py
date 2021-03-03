from typing import Set, Optional, List
from nltk.corpus.reader import Synset
from nltk.corpus import wordnet as wn


def antonyms(sense) -> Set[Synset]:
    antonym = set()

    word = wn.synset(sense)
    for lemma in word.lemmas():
        if lemma.antonyms():
            for ant in lemma.antonyms():
                syns = set(wn.synsets(ant.name()))
                for x in syns:
                    antonym.add(x)

    return antonym


def paths(sense_0: str, sense_1: str) -> List[List[Synset]]:
    synset_0 = wn.synset(sense_0)
    synset_1 = wn.synset(sense_1)
    hypernym_paths_0 = synset_0.hypernym_paths()
    hypernym_paths_1 = synset_1.hypernym_paths()
    lch = synset_0.lowest_common_hypernyms(synset_1)


    sense0lchpath = []
    sense1lchpath = []
    paths = []

    for hypernym in lch:
        for sense0hyp in hypernym_paths_0:
            sense0path = []
            sense0hyp.reverse()
            for hyps0 in sense0hyp:
                sense0path.append(hyps0)
                if hyps0 == hypernym and sense0path not in sense0lchpath:
                    sense0lchpath.append(sense0path)
                    break


    for hypernym in lch:
        for sense1hyp in hypernym_paths_1:
            sense1path = []
            sense1hyp.reverse()
            for hyps1 in sense1hyp:
                if hyps1 == hypernym and sense1path not in sense1lchpath:
                    sense1path.reverse()
                    sense1lchpath.append(sense1path)
                    break
                sense1path.append(hyps1)


    for path0 in sense0lchpath:
        for path1 in sense1lchpath:
            paths.append(path0 + path1)

    allpaths = []
    for path in paths:
        if path not in allpaths:
            allpaths.append(path)

    return allpaths

if __name__ == '__main__':
    print(antonyms('nonspecific.a.01'))

    for path in paths('boy.n.01', 'girl.n.01'):
        print([s.name() for s in path])