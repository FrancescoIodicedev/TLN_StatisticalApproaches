from collections import Counter
import spacy
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from spacy_wordnet.wordnet_annotator import WordnetAnnotator
import xlrd

lemmatizer = WordNetLemmatizer()
nlp = spacy.load('en_core_web_lg')
nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

PATH_DEFINITION = 'utils/content-to-form.xlsx'
PATH_TARGET_TERM = 'utils/target.txt'
PUNTUATION_SET = '.,:;!?()”“…'


# Per descrive un concetto t :
# 1: includerlo in una tassonomia (individuare l'iperonimo) -> Circoscrizione del concetto t //GENUS
# 2: tutto ciò  che caratterizza quel concetto in maniera differenziale (discriminante) //DIFFERENTIA
#
# Sister term di t : tutti i figli del padre di t

def load_definition(path):
    wkb = xlrd.open_workbook(path)
    sheet = wkb.sheet_by_index(0)
    matrix = []
    for row in range(sheet.nrows):
        cols = []
        for col in range(sheet.ncols):
            cols.append(sheet.cell_value(row, col))
        matrix.append(cols)
    return matrix[1:]


def load_terms_target(path):
    res = []
    with open(path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        res.append(line)
    return res


def remove_punctuation(string):
    chars = '.,:;!?()”“…-'
    for c in chars:
        string = string.replace(c, '')
    string = string.replace("’s", '')
    return string


def content_to_form(definition_list, max_terms_in_context, max_genus):
    domain, context = [], []
    stop_words = stopwords.words('english')

    for definition in definition_list:
        # 1 Estrazione termini rilevanti
        text = nlp(definition)
        subjs = filter(lambda token: token.dep_ == 'ROOT', text)

        relevant_words = filter(lambda token:
                                token.text.lower() not in stop_words and
                                token.text.lower() not in PUNTUATION_SET, text)
        relevant_words = list(relevant_words)

        # 2 Costruzione Domain + Context
        # Domain = soggetti delle frasi + wordnet domain of them
        # Context = sfera semantica i termini rilevanti di ogni definizione
        domain.extend(list(map(lambda t: t.text, subjs)))
        for token in relevant_words:
            domain.extend(token._.wordnet.wordnet_domains())
            context.append(token.text)

    # 3 Termini con frequenza maggiore
    candidate_genus = Counter(domain).most_common(max_genus)
    common_context = Counter(context).most_common(max_terms_in_context)
    s_context = ' '.join(list(map(lambda c: lemmatizer.lemmatize(c[0]), common_context)))

    print('Context obtained : {}'.format(s_context))
    print('Genus obtained : {}'.format(candidate_genus))

    # 4 Per ogni synset di un dominio, cerco tra gli iponimi quello che  ha score
    # di similarità maggiore rispetto al contesto
    best_synset = None
    best_score = 0
    for lemma in candidate_genus:
        # 5 Valutazione di ogni synset esplorato
        synset, score = get_best_synset(wn.synsets(lemmatizer.lemmatize(lemma[0])), s_context)
        if score > best_score:
            best_synset = synset
            best_score = score

    return best_synset, best_score


def get_best_synset(synsets, context):
    best_synset, best_score = None, 0

    for s in synsets:
        score = get_syn_score(s, context)
        #print('Hyper visited {} with score {}'.format(hyp, score))
        if score > best_score and s._pos == 'n':
            best_synset = s
            best_score = score
        for hyp in s.hyponyms():
            score = get_syn_score(hyp, context)
            #print('Hyp visited {} with score {}'.format(hyp, score))
            if score > best_score and s._pos == 'n':
                best_synset = hyp
                best_score = score

    return best_synset, best_score


def get_syn_score(synset, context):
    stop_words = stopwords.words('english')
    definition = nlp(remove_punctuation(synset.definition()))
    contex_nlp = nlp(context)
    definition_tokenized = nlp(' '.join([lemmatizer.lemmatize(str(t)) for t in definition if str(t) not in stop_words]))
    context_tokenized = nlp(' '.join([str(t) for t in contex_nlp if str(t) not in stop_words]))
    return definition_tokenized.similarity(context_tokenized)


if __name__ == '__main__':
    data = load_definition(PATH_DEFINITION)
    target = load_terms_target(PATH_TARGET_TERM)
    max_term_in_context = 20
    max_genus = 15

    for i, def_list in enumerate(data):
        print('*'*100)
        print('Target terms : {}'.format(target[i]))
        syns, sim = content_to_form(def_list, max_term_in_context, max_genus)
        print(f'Similarity: {sim} with {syns} \nDef : {syns.definition()}\n')
        print('*'*100)
        print('\n')

