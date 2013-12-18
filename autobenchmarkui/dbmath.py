import math


def mean(sequence):
    """
    :param sequence: An iterable to process
    :return: The mean average of the iterable items
    """
    return sum(sequence) / len(sequence)


def median(sequence):
    """
    Gets the median value of an iterable.

    :param sequence: An iterable that has a sort() method.
    :return: The Median value of the iterable
    """

    # We don't add one to the median because lists are zero indexed
    return sorted(sequence)[int((len(sequence)) / 2)]


def standard_deviation(allvalues):
    """
    If you want to know how this works, read this:

    http://www.mathsisfun.com/data/standard-deviation.html

    :param allvalues: a list of values to create the standard deviation
    from.

    :return: The standard devation
    """
    squareddiffs = []
    means = mean(allvalues)
    for value in allvalues:
        squareddiffs.append(math.pow((means - value), 2))
    return mean(squareddiffs)
