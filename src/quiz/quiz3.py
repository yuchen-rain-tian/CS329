import pickle
from collections import Counter
from typing import List, Tuple, Dict, Any

DUMMY = '!@#$'


def read_data(filename: str):
    data, sentence = [], []
    fin = open(filename)

    for line in fin:
        l = line.split()
        if l:
            sentence.append((l[0], l[1]))
        else:
            data.append(sentence)
            sentence = []

    return data


path = './'  # path to the cs329 directory
trn_data = read_data(path + 'dat/pos/wsj-pos.trn.gold.tsv')
dev_data = read_data(path + 'dat/pos/wsj-pos.dev.gold.tsv')


def to_probs(model: Dict[Any, Counter]) -> Dict[str, List[Tuple[str, float]]]:
    probs = dict()
    for feature, counter in model.items():
        ts = counter.most_common()
        total = sum([count for _, count in ts])
        probs[feature] = [(label, count/total) for label, count in ts]
    return probs


def evaluate(data: List[List[Tuple[str, str]]], *args):
    total, correct = 0, 0
    for sentence in data:
        tokens, gold = tuple(zip(*sentence))
        pred = [t[0] for t in predict(tokens, *args)]
        total += len(tokens)
        correct += len([1 for g, p in zip(gold, pred) if g == p])
    accuracy = 100.0 * correct / total
    return accuracy


def create_cw_dict(data: List[List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, float]]]:
    model = dict()
    for sentence in data:
        for word, pos in sentence:
            model.setdefault(word, Counter()).update([pos])
    return to_probs(model)


def create_pw_dict(data: List[List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, float]]]:
    model = dict()
    for sentence in data:
        for i, (_, curr_pos) in enumerate(sentence):
            prev_word = sentence[i-1][0] if i > 0 else DUMMY
            model.setdefault(prev_word, Counter()).update([curr_pos])
    return to_probs(model)


def create_nw_dict(data: List[List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, float]]]:
    model = dict()
    for sentence in data:
        for i, (_, curr_pos) in enumerate(sentence):
            next_word = sentence[i+1][0] if i+1 < len(sentence) else DUMMY
            model.setdefault(next_word, Counter()).update([curr_pos])
    return to_probs(model)


def create_pp_dict(data: List[List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, float]]]:
    model = dict()
    for sentence in data:
        for i, (_, curr_pos) in enumerate(sentence):
            prev_pos = sentence[i-1][1] if i > 0 else DUMMY
            model.setdefault(prev_pos, Counter()).update([curr_pos])
    return to_probs(model)


def create_nwpw_dict(data: List[List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, float]]]:
    model = dict()
    for sentence in data:
        for i, (_, curr_pos) in enumerate(sentence):
            next_word = sentence[i+1][0] if i+1 < len(sentence) else DUMMY
            prev_word = sentence[i-1][0] if i > 0 else DUMMY
            model.setdefault((prev_word, next_word), Counter()).update([curr_pos])
    return to_probs(model)


def create_ppnp_dict(data: List[List[Tuple[str, str]]]) -> Dict[str, List[Tuple[str, float]]]:
    model = dict()
    for sentence in data:
        for i, (_, curr_pos) in enumerate(sentence):
            prev_pos = sentence[i-1][1] if i > 0 else DUMMY
            next_pos = sentence[i+1][1] if i+1 < len(sentence) else DUMMY
            model.setdefault((prev_pos, next_pos), Counter()).update([curr_pos])
    return to_probs(model)


def train(trn_data: List[List[Tuple[str, str]]], dev_data: List[List[Tuple[str, str]]]) -> Tuple:
    cw_dict = create_cw_dict(trn_data)
    pw_dict = create_pw_dict(trn_data)
    nw_dict = create_nw_dict(trn_data)
    pp_dict = create_pp_dict(trn_data)
    nwpw_dict = create_nwpw_dict(trn_data)
    ppnp_dict = create_ppnp_dict(trn_data)


    best_acc, best_args = -1, None
    grid = [1, 0.5, 0.1]

    for cw_weight in grid:
        cw_weight = 1
        for pp_weight in grid:
            for pw_weight in grid:
                for nw_weight in grid:
                    for nwpw_weight in grid:
                        for ppnp_weight in grid:
                            args = (cw_dict, pp_dict, pw_dict, nw_dict, nwpw_dict, ppnp_dict, cw_weight, pp_weight, pw_weight, nw_weight, nwpw_weight, ppnp_weight)
                            acc = evaluate(dev_data, *args)
                            print('{:5.2f}% - cw: {:3.1f}, pp: {:3.1f}, pw: {:3.1f}, nw: {:3.1f}, nwpw: {:3.1f}, ppnp: {:3.1f}'.format(acc, cw_weight, pp_weight, pw_weight, nw_weight, nwpw_weight, ppnp_weight))
                            if acc > best_acc: best_acc, best_args = acc, args

    return best_args


def predict(tokens: List[str], *args) -> List[Tuple[str, float]]:
    cw_dict, pp_dict, pw_dict, nw_dict, nwpw_dict, ppnp_dict, cw_weight, pp_weight, pw_weight, nw_weight, nwpw_weight, ppnp_weight = args
    output = []

    for i in range(len(tokens)):
        scores = dict()
        curr_word = tokens[i]
        prev_pos = output[i-1][0] if i > 0 else DUMMY
        prev_word = tokens[i-1] if i > 0 else DUMMY
        next_word = tokens[i+1] if i+1 < len(tokens) else DUMMY
        next_pos = output[i+1][0] if i+1 < len(output) else DUMMY

        for pos, prob in cw_dict.get(curr_word, list()):
            scores[pos] = scores.get(pos, 0) + prob * cw_weight

        for pos, prob in pp_dict.get(prev_pos, list()):
            scores[pos] = scores.get(pos, 0) + prob * pp_weight

        for pos, prob in pw_dict.get(prev_word, list()):
            scores[pos] = scores.get(pos, 0) + prob * pw_weight

        for pos, prob in nw_dict.get(next_word, list()):
            scores[pos] = scores.get(pos, 0) + prob * nw_weight

        for pos, prob in nwpw_dict.get((prev_word, next_word), list()):
            scores[pos] = scores.get(pos, 0) + prob * nwpw_weight

        for pos, prob in ppnp_dict.get((prev_pos, next_pos), list()):
            scores[pos] = scores.get(pos, 0) + prob * nwpw_weight

        o = max(scores.items(), key=lambda t: t[1]) if scores else ('XX', 0.0)
        output.append(o)

    return output


if __name__ == '__main__':
    path = './'  # path to the cs329 directory
    trn_data = read_data(path + 'dat/pos/wsj-pos.trn.gold.tsv')
    dev_data = read_data(path + 'dat/pos/wsj-pos.dev.gold.tsv')
    model_path = path + 'src/quiz/quiz3.pkl'

    # save model
    args = train(trn_data, dev_data)
    pickle.dump(args, open(model_path, 'wb'))
    # load model
    args = pickle.load(open(model_path, 'rb'))
    print(evaluate(dev_data, *args))