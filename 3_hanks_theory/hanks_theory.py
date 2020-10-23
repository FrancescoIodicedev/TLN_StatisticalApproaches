import matplotlib.pyplot as plt
import nltk
import spacy
import numpy as np
from nltk import WordNetLemmatizer, Counter
from nltk.corpus import brown
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
import wsd_noun

lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_sm')

pronouns_persons = ['i', 'you', 'he', 'she', 'we', 'they', 'me']

pronouns_object = ['it']
ambiguous_terms = ['that', 'what', 'her']

person_supersense = 'noun.person'
entity_supersense = 'noun.entity'


def get_sentences_with_verb(verb):
    target_sentence = []
    for sentence in brown.sents():
        for word in sentence:
            if lemmatizer.lemmatize(word, 'v') == verb:
                # if has_subj_dobj(sentence, verb):
                target_sentence.append(' '.join(sentence))
    return target_sentence


def extract_subj_dobj(sentence, verb_base_form):
    token_s = nlp(sentence)
    for token in token_s:
        subj, dobj = '', ''
        if verb_base_form in token.text:
            for child in token.children:
                if child.dep_ == "nsubj":
                    # print('SOGGETTO : {}\n'.format(child.text))
                    subj = child.text
                if child.dep_ == "dobj":
                    # print('OGGETTO DIRETTO : {}\n'.format(child.text))
                    dobj = child.text
        if dobj != '' and subj != '':
            break
    return subj, dobj


def map_pronom_to_sense(word):
    if word.lower() in pronouns_persons:
        return person_supersense
    else:
        return entity_supersense


def is_pronom(word):
    pos_word = nltk.pos_tag(word_tokenize(word))
    return pos_word[0][1] == 'PRP'


def stringate_value(hypernom_subj, hypernom_dobj):
    return hypernom_subj.split('.')[1] + ':' + hypernom_dobj.split('.')[1]


def is_personal_noun(subj):
    char = subj[0:1]
    if len(wn.synsets(subj)) == 0 and char.isupper():
        return True
    return False


def plot_result(dataset, verb):
    # Add titles and axis names
    occurence, semantic_type = [], []
    for k in dataset:
        occurence.append(k[1])
        semantic_type.append(k[0].replace(':', '\n'))

    y_pos = np.arange(len(semantic_type))
    plt.bar(y_pos, occurence, align='center', alpha=0.5)
    plt.xticks(y_pos, semantic_type)
    plt.title('Semantic cluster of verb {}'.format(verb))
    plt.xlabel('Semantic types')
    plt.ylabel('Occurences')
    plt.show()


def take_second(elem):
    return elem[1]


def get_supersense(elem, sentence):
    hypernom, elem_disambigued  = '', None
    if is_pronom(elem):
        hypernom = map_pronom_to_sense(elem)
    elif is_personal_noun(elem):
        hypernom = person_supersense
    else:
        elem_disambigued = wsd_noun.lesk_algorithm(elem, sentence)
    if elem_disambigued is not None:
        hypernom = elem_disambigued._lexname
    return hypernom


def get_semantic_cluster(sentences, verb_base_form):
    filler1, filler2 = [], []
    sentences_analyzed, semantic_type = 0, []
    for s in sentences:
        subj, dobj = extract_subj_dobj(s, verb_base_form)

        if subj != '' and dobj != '':
            if subj.lower() not in ambiguous_terms and dobj.lower() not in ambiguous_terms:
                hypernom_subj = get_supersense(subj, s)
                hypernom_dobj = get_supersense(dobj, s)

                if hypernom_dobj != '' and hypernom_subj != '':
                    sentences_analyzed += 1
                    filler1.append(hypernom_subj)
                    filler2.append(hypernom_dobj)
                    semantic_values = stringate_value(hypernom_subj, hypernom_dobj)
                    semantic_type.append(semantic_values)

    return semantic_type, sentences_analyzed


if __name__ == '__main__':
    verbs_bf = ['build', 'love', 'eat']

    for verb_base_form in verbs_bf:

        sentences = get_sentences_with_verb(verb_base_form)
        print('*' * 50)
        print('\nCurrent verb base form : {}\n'.format(verb_base_form))
        semantic_cluster, sentences_analyzed = get_semantic_cluster(sentences, verb_base_form)
        print('------ End extraction-----------')

        # Print stats
        sts_semantic_cluster = Counter(semantic_cluster)
        common_semantic_cluster = sts_semantic_cluster.most_common(5)
        plot_result(common_semantic_cluster, verb_base_form)

        print('\nAnalized {} sentences \nFor the verb in base form : {} pair of semantic type are:\n'
              .format(sentences_analyzed, verb_base_form))

        for s in sts_semantic_cluster:
            print('\t< {} > Count {} '.format(s, sts_semantic_cluster[s]))

        print('*' * 50)
        print('\n\n\n')
