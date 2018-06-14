# Natural Language Toolkit: Distance Metrics
#
# Copyright (C) 2001-2018 NLTK Project
# Author: Edward Loper <edloper@gmail.com>
#         Steven Bird <stevenbird1@gmail.com>
#         Tom Lippincott <tom@cs.columbia.edu>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT
#

"""
Distance Metrics.

Compute the distance between two items (usually strings).
As metrics, they must satisfy the following three requirements:

1. d(a, a) = 0
2. d(a, b) >= 0
3. d(a, c) <= d(a, b) + d(b, c)
"""

from __future__ import print_function
from __future__ import division
import math


def _edit_dist_init(len1, len2):
    lev = []
    for i in range(len1):
        lev.append([0] * len2)  # initialize 2D array to zero
    for i in range(len1):
        lev[i][0] = i           # column 0: 0,1,2,3,4,...
    for j in range(len2):
        lev[0][j] = j           # row 0: 0,1,2,3,4,...
    return lev


def _edit_dist_step(lev, i, j, s1, s2,
                    substitution_cost=1,
                    transpositions=False):
    c1 = s1[i - 1]
    c2 = s2[j - 1]

    # skipping a character in s1
    a = lev[i - 1][j] + 1
    # skipping a character in s2
    b = lev[i][j - 1] + 1
    # substitution
    c = lev[i - 1][j - 1] + (substitution_cost if c1 != c2 else 0)

    # transposition
    d = c + 1  # never picked by default
    if transpositions and i > 1 and j > 1:
        if s1[i - 2] == c2 and s2[j - 2] == c1:
            d = lev[i - 2][j - 2] + 1

    # pick the cheapest
    lev[i][j] = min(a, b, c, d)


def edit_distance(s1, s2, substitution_cost=1, transpositions=False):
    """
    Calculate the Levenshtein edit-distance between two strings.
    The edit distance is the number of characters that need to be
    substituted, inserted, or deleted, to transform s1 into s2.  For
    example, transforming "rain" to "shine" requires three steps,
    consisting of two substitutions and one insertion:
    "rain" -> "sain" -> "shin" -> "shine".  These operations could have
    been done in other orders, but at least three steps are needed.

    Allows specifying the cost of substitution edits (e.g., "a" -> "b"),
    because sometimes it makes sense to assign greater penalties to
    substitutions.

    This also optionally allows transposition edits (e.g., "ab" -> "ba"),
    though this is disabled by default.

    :param s1, s2: The strings to be analysed
    :param transpositions: Whether to allow transposition edits
    :type s1: str
    :type s2: str
    :type substitution_cost: int
    :type transpositions: bool
    :rtype int
    """
    # set up a 2-D array
    len1 = len(s1)
    len2 = len(s2)
    lev = _edit_dist_init(len1 + 1, len2 + 1)

    # iterate over the array
    for i in range(len1):
        for j in range(len2):
            _edit_dist_step(lev, i + 1, j + 1, s1, s2,
                            substitution_cost=substitution_cost,
                            transpositions=transpositions)
    return lev[len1][len2]


def binary_distance(label1, label2):
    """Simple equality test.

    0.0 if the labels are identical, 1.0 if they are different.

    >>> from nltk.metrics import binary_distance
    >>> binary_distance(1,1)
    0.0

    >>> binary_distance(1,3)
    1.0
    """

    return 0.0 if label1 == label2 else 1.0


def jaccard_distance(label1, label2):
    """Distance metric comparing set-similarity.

    """
    return (len(label1.union(label2)) -
            len(label1.intersection(label2)))/len(label1.union(label2))


def masi_distance(label1, label2):
    """Distance metric that takes into account partial agreement when multiple
    labels are assigned.

    >>> from nltk.metrics import masi_distance
    >>> masi_distance(set([1, 2]), set([1, 2, 3, 4]))
    0.665

    Passonneau 2006, Measuring Agreement on Set-Valued Items (MASI)
    for Semantic and Pragmatic Annotation.
    """

    len_intersection = len(label1.intersection(label2))
    len_union = len(label1.union(label2))
    len_label1 = len(label1)
    len_label2 = len(label2)
    if len_label1 == len_label2 and len_label1 == len_intersection:
        m = 1
    elif len_intersection == min(len_label1, len_label2):
        m = 0.67
    elif len_intersection > 0:
        m = 0.33
    else:
        m = 0

    return 1 - len_intersection / len_union * m


def interval_distance(label1, label2):
    """Krippendorff's interval distance metric

    >>> from nltk.metrics import interval_distance
    >>> interval_distance(1,10)
    81

    Krippendorff 1980, Content Analysis: An Introduction to its Methodology
    """

    try:
        return pow(label1 - label2, 2)
#        return pow(list(label1)[0]-list(label2)[0],2)
    except:
        print("non-numeric labels not supported with interval distance")


def presence(label):
    """Higher-order function to test presence of a given label
    """

    return lambda x, y: 1.0 * ((label in x) == (label in y))


def fractional_presence(label):
    return lambda x, y:\
        abs(((1.0 / len(x)) - (1.0 / len(y)))) * (label in x and label in y) \
        or 0.0 * (label not in x and label not in y) \
        or abs((1.0 / len(x))) * (label in x and label not in y) \
        or ((1.0 / len(y))) * (label not in x and label in y)


def custom_distance(file):
    data = {}
    with open(file, 'r') as infile:
        for l in infile:
            labelA, labelB, dist = l.strip().split("\t")
            labelA = frozenset([labelA])
            labelB = frozenset([labelB])
            data[frozenset([labelA, labelB])] = float(dist)
    return lambda x, y: data[frozenset([x, y])]


def jaro_similarity(s1, s2):
    """
    Computes the Jaro similarity between 2 sequences from:

        Matthew A. Jaro (1989). Advances in record linkage methodology
        as applied to the 1985 census of Tampa Florida. Journal of the
        American Statistical Association. 84 (406): 414–20.

    The Jaro distance between is the min no. of single-character transpositions
    required to change one word into another. The Jaro similarity formula from
    https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance :

        jaro_sim = 0 if m = 0 else 1/3 * (m/|s_1| + m/s_2 + (m-t)/m)

    where:
        - |s_i| is the length of string s_i
        - m is the no. of matching characters
        - t is the half no. of possible transpositions.
    """
    # First, store the length of the strings
    # because they will be re-used several times.
    len_s1, len_s2 = len(s1), len(s2)

    # The upper bound of the distanc for being a matched character.
    match_bound = math.floor( max(len(s1), len(s2)) / 2 ) - 1

    # Initialize the counts for matches and transpositions.
    matches = 0  # no.of matched characters in s1 and s2
    transpositions = 0  # no. transpositions between s1 and s2

    # Iterate through sequences, check for matches and compute transpositions.
    for ch1 in s1:     # Iterate through each character.
        if ch1 in s2:  # Check whether the
            pos1 = s1.index(ch1)
            pos2 = s2.index(ch1)
            if(abs(pos1-pos2) <= match_bound):
                matches += 1
                if(pos1 != pos2):
                    transpositions += 1
                    
    if matches = 0:
        return 0
    else:
        return 1/3 * ( matches/len_s1 + 
                       matches/len_s2 + 
                      (matches-transpositions//2) / matches 
                     )


def jaro_winkler_similarity(s1, s2, p=0.1, max_l=None):
    """
    The Jaro Winkler distance is an extension of the Jaro similarity in:

        William E. Winkler. 1990. String Comparator Metrics and Enhanced
        Decision Rules in the Fellegi-Sunter Model of Record Linkage.
        Proceedings of the Section on Survey Research Methods.
        American Statistical Association: 354–359.

    such that:

        jaro_winkler_sim = jaro_sim + ( l * p * (1 - jaro_sim) )

    where,

        - jaro_sim is the output from the Jaro Similarity, see jaro_similarity()
        - l is the length of common prefix at the start of the string
            - this implementation provides an upperbound for the l value
              to keep the prefixes
        - p is the constant scaling factor to overweigh common prefixes.
          The Jaro-Winkler similarity will fall within the [0, 1] bound,
          given that max(p)<=0.25 , default is p=0.1 in Winkler (1990)

    """
    # Compute the Jaro similarity
    jaro_sim = jaro_similarity(s1, s2)

    # Initialize the upper bound for the no. of prefixes.
    # if user did not pre-define the upperbound, use length of s1
    max_l = max_l if max_l else len(s1)

    # Compute the prefix matches.
    l = 0
    for i in range(len(s1)):
        if s1[i] == s2[i]:
            l += 1
        else:
            break
        if l == max_l:
            break
    # Return the similarity value as described in docstring.
    return jaro_sim + ( l * p * (1 - jaro_sim) )



def demo():
    string_distance_examples = [
        ("rain", "shine"), ("abcdef", "acbdef"), ("language", "lnaguaeg"),
        ("language", "lnaugage"), ("language", "lngauage")]

    for s1, s2 in string_distance_examples:
        print("Edit distance btwn '%s' and '%s':" % (s1, s2),
              edit_distance(s1, s2))
        print("Edit dist with transpositions btwn '%s' and '%s':" % (s1, s2),
              edit_distance(s1, s2, transpositions=True))
        print("Jaro similarity btwn '%s' and '%s':" % (s1, s2),
              jaro_similarity(s1, s2))
        print("Jaro-Winkler similarity btwn '%s' and '%s':" % (s1, s2),
              jaro_winkler_similarity(s1, s2))
        print("Jaro-Winkler similarity btwn '%s' and '%s':" % (s1, s2),
              1 - jaro_winkler_similarity(s1, s2))
        print()

    s1 = set([1, 2, 3, 4])
    s2 = set([3, 4, 5])
    print("s1:", s1)
    print("s2:", s2)
    print("Binary distance:", binary_distance(s1, s2))
    print("Jaccard distance:", jaccard_distance(s1, s2))
    print("MASI distance:", masi_distance(s1, s2))


if __name__ == '__main__':
    demo()
