import re

word2num = {'twenty': '20', 'thirty': '30',
            'forty': '40', 'fifty': '50',
            'sixty': '60', 'seventy': '70',
            'eighty': '80', 'ninety': '90',
            'hundred': '100', 'thousand': '1000',
            'million': '1000000', 'billion': '1000000000',
            'one':   '1', 'eleven':     '11',
            'two':   '2', 'twelve':     '12',
            'three': '3', 'thirteen':   '13',
            'four':  '4', 'fourteen':   '14',
            'five':  '5', 'fifteen':    '15',
            'six':   '6', 'sixteen':    '16',
            'seven': '7', 'seventeen':  '17',
            'eight': '8', 'eighteen':   '18',
            'nine':  '9', 'nineteen':   '19'}


def normalize(text):
    cardinals = re.compile('|'.join(word2num.keys()))
    match = cardinals.finditer(text)

    prev_idx = 0
    tokens = []
    calc = []
    final_sentence = []


    for m in match:
        # print(m)
        t = text[prev_idx:m.start()]
        if t:
            tokens.append(t.strip())
            t = m.group().strip()
            t = t.replace(t, word2num[t])
            tokens.append(t)
        prev_idx = m.end()

    tokens = [x for x in tokens if x != '']

    if prev_idx != 0:
        if m.end() != len(text)-1:
            tokens.append(text[m.end():].strip())
    else:
        print("No cardinals detected")

    for t in tokens:
        if t.isdigit():
            calc.append(t)
        elif len(calc) > 1:
            result = int(calc[0])
            for c in range(len(calc)-1):
                if len(calc[c]) < len(calc[c+1]):
                    result *= int(calc[c+1])
                elif len(calc[c]) > len(calc[c+1]):
                    result += int(calc[c+1])

            for i in range(len(calc)):
                final_sentence.pop()
            final_sentence.append(str(result))
            calc = []

        elif len(calc) == 1 or len(calc) == 0:
            calc = []

        final_sentence.append(t)

    text = " ".join(final_sentence)
    print(text)

    return text

if __name__ == '__main__':
    S = [
        'I met twelve people',
        'I have one brother and two sisters',
        'A year has three hundred sixty five days',
        'I made a million dollars'
    ]

    T = [
        'I met 12 people',
        'I have 1 brother and 2 sisters',
        'A year has 365 days',
        'I made 1000000 dollars'
    ]

    correct = 0
    for s, t in zip(S, T):
        if normalize(s) == t:
            correct += 1

    print('Score: {}/{}'.format(correct, len(S)))

