import spacy

nlp_model = spacy.load('en_core_web_sm')
SENTENCE_PATH = 'utils/sentences.txt'


def get_sentences(path):
    res = []
    with open(path, 'r') as file:
        lines = file.readlines()

    for line in lines:
        res.append(line)
    return res


# Possible tags to relate terms in sentence
def check_relation(token):
    if token.dep_ in ["ROOT", "adj", "attr", "agent", "amod"]:
        return True
    else:
        return False


# Possible tags to relate terms in sentence
def token_is_to_link(token):
    if token.dep_ in ["compound", "prep", "conj", "mod"]:
        return True
    else:
        return False


def extract_relations(tokens):
    subject, dobject, rel = '', '', ''
    tmp_subj, tmp_obj = '', ''

    for token in tokens:
        if token.dep_ == 'punct':
            continue
        # If current token is a relations
        if check_relation(token):
            rel += ' ' + token.lemma_
        # If current token is to link with other token (compund word, adj+noun)
        if token_is_to_link(token):
            if tmp_subj:
                tmp_subj += ' ' + token.text
            if tmp_obj:
                tmp_obj += ' ' + token.text
        # If current token is subject so attach current token's text
        # to other token, to link with the current (saved in tmp_subj)
        if "subj" in token.dep_:
            subject += ' ' + token.text
            subject = tmp_subj + ' ' + subject
            tmp_subj = ''
        # If current token is object so attach current token's text
        # to other token, to link with the current (saved in tmp_subj)
        if "obj" in token.dep_:
            dobject += ' ' + token.text
            dobject = tmp_obj + ' ' + dobject
            tmp_obj = ''

    return subject.strip(), rel.strip(), dobject.strip()


if __name__ == "__main__":
    sentences = get_sentences(SENTENCE_PATH)
    triples = []

    for sentence in sentences:
        print('\nSentence : {}'.format(sentence.replace('\n','')))
        # Pos tag + dependency relationship
        tokens = nlp_model(sentence)
        subj, rel, dobj = extract_relations(nlp_model(sentence))
        print('\t( {}, {}, {} )'.format(subj, rel, dobj ))
        triples.append((subj, rel, dobj))