from nltk import ngrams
from nltk.metrics import jaccard_distance


def bow_overlap(tokens1, tokens2, n=1):
    grams = set(ngrams(tokens1, n))
    grams2 = set(ngrams(tokens2, n))

    result = 1 - jaccard_distance(grams, grams2)
    return result


def bow_pos_overlap(tokens1, tags1, tokens2, tags2, n=1):
    return bow_overlap(zip(tokens1, tags1), zip(tokens2, tags2))
