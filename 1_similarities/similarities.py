from itertools import combinations
from nltk.corpus import stopwords
import xlrd
from nltk.stem import PorterStemmer
from prettytable import PrettyTable
import numpy as np

porter_stemmer = PorterStemmer()
PATH_DEFINITION = 'definizioni.xlsx'


def load_definition(path):
    wkb = xlrd.open_workbook(path)
    sheet = wkb.sheet_by_index(0)
    matrix = []
    for col in range(sheet.ncols):
        rows = []
        for row in range(sheet.nrows):
            rows.append(sheet.cell_value(row, col))
        matrix.append(rows)
    return matrix[1:]


# aggregate term for each definition to find relevant terms for every term to describe
# return a map with
#  [ { term_A, { termA1: occ_termA1 , termA2: occ_termA2  .. termA3: occ_termA3 },
#    { term_B, { ..} ... ]
#   @ term_A to describe
#   @ termA1 , termA2 ..  : all terms in definition
#   @ Occ_termA1 .. occurences term termA1

def remove_punctuation(string):
    chars = '.,:;!?()”“…-'
    for c in chars:
        string = string.replace(c, '')
    string = string.replace("’s", '')
    return string


def clean_data(matrix):
    map_result = {}
    stop_words = stopwords.words('english')

    for col in range(len(matrix)):
        all_terms = []
        for row in range(len(matrix[col])):
            if row == 0:
                concept = matrix[col][row].split(' ')
                map_result[concept[1]] = ''
            else:
                terms = matrix[col][row].split(' ')
                for t in terms:
                    if t.strip() != '':
                        # remove puntuation & getting stem
                        primitive_term = remove_punctuation(porter_stemmer.stem(t.lower()))
                        # remove stopword
                        if primitive_term not in stop_words:
                            all_terms.append(primitive_term)
                        # print('For the terms: {} the stemming is {}'.format(t,stem_of_t))
        term_occ = get_occurrences_of_words(all_terms)
        map_result[concept[1]] = term_occ
    return map_result


# return a set for each definition with terms orderder by relevance
def performs_statistics_on_defs(matrix, stats):
    freq_on_def_terms = {}
    stop_words = stopwords.words('english')

    for defs in matrix:
        terms_freq = []
        for i, gloss in enumerate(defs):
            if i == 0:
                keyname = gloss.split(' ')[1]
            else:
                terms = gloss.split(' ')
                stemming_term = []
                for t in terms:
                    if t.strip() != '':
                        # remove puntuation & getting stem
                        primitive_term = remove_punctuation(porter_stemmer.stem(t.lower()))
                        # remove stopword
                        if primitive_term not in stop_words:
                            stemming_term.append(primitive_term)
                # order terms on frequency of every terms in every definition of current concept
                terms_freq.append(order_on_occurrences(stemming_term, stats[keyname]))
            freq_on_def_terms[keyname] = terms_freq
    return freq_on_def_terms


def get_occurrences_of_words(terms):
    result = []
    for w in set(terms):
        val = terms.count(w)
        # if val > 1:
        result.append([w, val])
    result.sort(key=take_second, reverse=True)
    return result


def order_on_occurrences(terms, sts_key_def):
    ordered_terms = []
    index = 0
    while index < len(sts_key_def):
        if sts_key_def[index][0] in terms:
            ordered_terms.append(sts_key_def[index][0])
        index = index + 1
    return ordered_terms


def take_second(elem):
    return elem[1]


# normalized cardinality of list as parametres
def normalize_cardinality(list1, list2):
    min_length = len(list2)
    if len(list1) < len(list2):
        min_length = len(list1)
    return set(list1[0:min_length]), set(list2[0:min_length])


def get_definitions_similarity(def_terms1, def_terms2):
    def_terms1, def_terms2 = normalize_cardinality(def_terms1, def_terms2)
    overlap = def_terms1.intersection(def_terms2)
    similarity = len(overlap) * 100 / len(def_terms1)
    return similarity


if __name__ == '__main__':
    # 1 Caricamento dei dati sulle definizioni
    matrix = load_definition(PATH_DEFINITION)
    frequency, decimal_places = 1, 2
    # 2 Preprocessing
    sts_all_defs = clean_data(matrix)
    topic_single_def = performs_statistics_on_defs(matrix, sts_all_defs)

    # 3 Calcolo similarità tra definizioni
    mean_similarity = {}
    for key in topic_single_def:
        similarity = []
        for s1, s2 in list(combinations(topic_single_def[key], 2)):
            if s1 != s2:
                if len(s1) > 2 and len(s2) > 2:
                    similarity.append(float(get_definitions_similarity(s1, s2)))
        key_val = key.split('_')[:2]
        mean_similarity[' '.join(key_val)] = np.mean(similarity)

    # 4 Aggregazione sulle due dimensioni
    dimension = [['astratto', 'concreto'], ['generico', 'specifico']]
    report = PrettyTable(['Result', dimension[0][0], dimension[0][1]])

    # 5 Interpretazione dei risultati e scrittura di un piccolo report
    for specificity in dimension[1]:
        sim_value = [specificity]
        for concreteness in dimension[0]:
            key = concreteness + ' ' + specificity
            sim_value.append(round(mean_similarity[key], decimal_places))
        report.add_row(sim_value)

    print(report)
