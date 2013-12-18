from collections import Counter


def get_mode(l):
    counter = Counter(l)
    return counter.most_common()[0][0]


def get_average(l):
    sum = 0
    for i in l:
        sum += i
    return sum / len(l)


def get_range(l):
    return max(l) - min(l)
