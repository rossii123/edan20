"""
Gold standard parser
"""
__author__ = "Pierre Nugues"

from sklearn import preprocessing
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import accuracy_score
from sklearn import linear_model

import transition
import conll
import features
from sklearn.externals import joblib
from pathlib import Path



def reference(stack, queue, state):
    """
    Gold standard parsing
    Produces a sequence of transitions from a manually-annotated corpus:
    sh, re, ra.deprel, la.deprel
    :param stack: The stack
    :param queue: The input list
    :param state: The set of relations already parsed
    :return: the transition and the grammatical function (deprel) in the
    form of transition.deprel
    """
    #if stack:
        #print("Stack0: " + stack[0]["form"] + ", Queue0:" + queue[0]["form"] + ", State:" + str(state))


    # Right arc

    if stack and stack[0]['id'] == queue[0]['head']:
        #print('ra', queue[0]['deprel'], stack[0]['cpostag'], queue[0]['cpostag'])
        deprel = '.' + queue[0]['deprel']
        stack, queue, state = transition.right_arc(stack, queue, state)
        return stack, queue, state, 'ra' + deprel
    # Left arc
    if stack and queue[0]['id'] == stack[0]['head']:
        #print('la', stack[0]['deprel'], stack[0]['cpostag'], queue[0]['cpostag'])
        deprel = '.' + stack[0]['deprel']
        stack, queue, state = transition.left_arc(stack, queue, state)
        return stack, queue, state, 'la' + deprel
    # Reduce
    if stack and transition.can_reduce(stack, state):
        for word in stack:
            if (word['id'] == queue[0]['head'] or
                        word['head'] == queue[0]['id']):
                #print('re', stack[0]['cpostag'], queue[0]['cpostag'])
                stack, queue, state = transition.reduce(stack, queue, state)
                return stack, queue, state, 're'
    # Shift
    #print('sh', [], queue[0]['cpostag'])
    stack, queue, state = transition.shift(stack, queue, state)
    #print("=============")
    return stack, queue, state, 'sh'

def extract(stack, queue, state, feature_names, sentence):
    features = {}
    features["can_reduce"] = str(transition.can_reduce(stack, state))
    features["can_leftarc"] = str(transition.can_leftarc(stack, state))

    if stack:
        features["stack0_postag"] = stack[0]["postag"]
        features["stack0_form"] = stack[0]["form"]
    else:
        features["stack0_postag"] = "nil"
        features["stack0_form"] = "nil"
    if len(stack) > 1:
        features["stack1_postag"] = stack[1]["postag"]
        features["stack1_form"] = stack[1]["form"]
    else:
        features["stack1_postag"] = "nil"
        features["stack1_form"] = "nil"

    if queue:
        features["queue0_postag"] = queue[0]["postag"]
        features["queue0_form"] = queue[0]["form"]
    else:
        features["queue0_postag"] = "nil"
        features["queue0_form"] = "nil"
    if len(queue) > 1:
        features["queue1_postag"] = queue[1]["postag"]
        features["queue1_form"] = queue[1]["form"]
    else:
        features["queue1_postag"] = "nil"
        features["queue1_form"] = "nil"

    features["nextWord_form"] = "nil"
    features["nextWord_postag"] = "nil"
    if int(queue[0]["id"]) < len(sentence)-1:
        w = sentence[int(queue[0]["id"]) +1]
        features["nextWord_form"] = w['form']
        features["nextWord_postag"] = w['postag']

    features["prevWord_form"] = "nil"
    features["prevWord_postag"] = "nil"
    if int(queue[0]["id"]) > 0:
        w = sentence[int(queue[0]["id"]) -1]
        features["prevWord_form"] = w['form']
        features["prevWord_postag"] = w['postag']

    return features

def calculateSomething(filen, model=None, dict_vect=None, label_enc = None):
        column_names_2006 = ['id', 'form', 'lemma', 'cpostag', 'postag', 'feats', 'head', 'deprel', 'phead', 'pdeprel']
        column_names_2006_test = ['id', 'form', 'lemma', 'cpostag', 'postag', 'feats']
        sentences = conll.read_sentences(filen)
        formatted_corpus = conll.split_rows(sentences, column_names_2006)
        sent_cnt = 0
        X_unEncoded = []
        y_unEncoded = []
        for sentence in formatted_corpus:
            sent_cnt += 1
            #if sent_cnt % 1000 == 0:
            #    print(sent_cnt, 'sentences on', len(formatted_corpus), flush=True)
            stack = []
            queue = list(sentence)
            state = {}
            state['heads'] = {}
            state['heads']['0'] = '0'
            state['deprels'] = {}
            state['deprels']['0'] = 'ROOT'
            transitions = []
            while queue:

                featureRow = extract(stack, queue, state, [], sentence)
                if model is None or dict_vect is None or label_enc is None:
                    stack, queue, state, trans = reference(stack, queue, state)
                    transitions.append(trans)
                else:
                    featureRow_encoded = dict_vect.transform(featureRow)
                    trans_nr = model.predict(featureRow_encoded)
                    trans = le.inverse_transform(trans_nr)
                    print(trans[0])

                    stack, queue, graph, trans = parse_ml(stack, queue, graph, trans)

                X_unEncoded.append(featureRow)
                y_unEncoded.append(trans)

            stack, state = transition.empty_stack(stack, state)

            #print('Equal graphs:', transition.equal_graphs(sentence, state))

            # Poorman's projectivization to have well-formed graphs.
            for word in sentence:
                word['head'] = state['heads'][word['id']]
        return X_unEncoded, y_unEncoded


if __name__ == '__main__':
    train_file = './data/swedish_talbanken05_train.conll'
    test_file = './data/swedish_talbanken05_test.conll'

    X_unEncoded, y_unEncoded  = calculateSomething(train_file)
    X_test_U, y_test_U  = calculateSomething(train_file)


    print("Vectorizing and encoding..")
    le = preprocessing.LabelEncoder()
    y = le.fit_transform(y_unEncoded)
    v = DictVectorizer(sparse=True)
    X = v.fit_transform(X_unEncoded)




    my_file = Path("classifier.pkl")
    model = 0
    if my_file.is_file():
        print("Loading model..")
        model = joblib.load('classifier.pkl')
    else:
        print("Training model..")
        classifier = linear_model.LogisticRegression(penalty='l2', dual=True, solver='liblinear')
        model = classifier.fit(X, y)
        print("Saving classifier..")
        joblib.dump(classifier, 'classifier.pkl')
    print("Predicting..")
    y_pred = model.predict(X)
    aS = accuracy_score(y,y_pred)
    print("Accuracy on train data:" + str(aS))
    y_U = le.transform(y_test_U)
    X_U = v.transform(X_test_U)
    y_pred_U = model.predict(X_U)
    aS_test = accuracy_score(y_U,y_pred_U)
    print("Accuracy on test (blind) data:" + str(aS_test))
    test_file = './data/swedish_talbanken05_test_blind.conll'
    X_test_U, y_test_U = calculateSomething(test_file, model, v, le)
