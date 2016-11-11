"""
CoNLL-X and CoNLL-U file readers and writers
"""
__author__ = "Pierre Nugues"

import os
import operator


def get_files(dir, suffix):
    """
    Returns all the files in a folder ending with suffix
    Recursive version
    :param dir:
    :param suffix:
    :return: the list of file names
    """
    files = []
    for file in os.listdir(dir):
        path = dir + '/' + file
        if os.path.isdir(path):
            files += get_files(path, suffix)
        elif os.path.isfile(path) and file.endswith(suffix):
            files.append(path)
    return files


def read_sentences(file):
    """
    Creates a list of sentences from the corpus
    Each sentence is a string
    :param file:
    :return:
    """
    f = open(file).read().strip()
    sentences = f.split('\n\n')
    return sentences


def split_rows(sentences, column_names):
    """
    Creates a list of sentence where each sentence is a list of lines
    Each line is a dictionary of columns
    :param sentences:
    :param column_names:
    :return:
    """
    new_sentences = []
    root_values = ['0', 'ROOT', 'ROOT', 'ROOT',
                   'ROOT', 'ROOT', '0', 'ROOT', '0', 'ROOT']
    start = [dict(zip(column_names, root_values))]
    for sentence in sentences:
        rows = sentence.split('\n')
        sentence = [dict(zip(column_names, row.split()))
                    for row in rows if row[0] != '#']
        sentence = start + sentence
        new_sentences.append(sentence)
    return new_sentences


def save(file, formatted_corpus, column_names):
    f_out = open(file, 'w')
    for sentence in formatted_corpus:
        for row in sentence[1:]:
            # print(row, flush=True)
            for col in column_names[:-1]:
                if col in row:
                    f_out.write(row[col] + '\t')
                else:
                    f_out.write('_\t')
            col = column_names[-1]
            if col in row:
                f_out.write(row[col] + '\n')
            else:
                f_out.write('_\n')
        f_out.write('\n')
    f_out.close()


def myExit(number, amount):
    if number > amount:
        quit()


def myFunction(formatted_corpus):
    count = {}
    countNumber = 0
    for sentence in formatted_corpus:

        for word in sentence:
            """
            print(word)
            myExit(countNumber, 5)
            countNumber += 1
            """
            if word["deprel"] == "SS":
                subjectWord = word['form'].lower()
                verb = word["head"]
                verb = sentence[int(verb)]
                for obj in sentence:
                    if obj["deprel"] == "OO" and obj["head"] == verb['id']:
                        objWord = obj["form"].lower()
                        verbWord = verb['form'].lower()
                        if (subjectWord, verbWord, objWord) in count:
                            count[(subjectWord, verbWord, objWord)] += 1
                        else:
                            count[(subjectWord, verbWord, objWord)] = 1

                    """
                    print(verb)
                    quit()
                    if(countNumber > 3):
                        quit()
                    countNumber += 1
                    if (subject, verb) in count:
                        count[(subject, verb)] += 1
                    else:
                        count[(subject, verb)] = 1
                    """

    sorted_x = sorted(count.items(), key=operator.itemgetter(1))
    return sorted_x[-5:]

if __name__ == '__main__':
    column_names_2006 = ['id', 'form', 'lemma', 'cpostag',
                         'postag', 'feats', 'head', 'deprel', 'phead', 'pdeprel']
    train_file = './swedish_talbanken05_train.conll'
    # train_file = 'test_x'
    test_file = './swedish_talbanken05_test.conll'

    sentences = read_sentences(train_file)
    formatted_corpus = split_rows(sentences, column_names_2006)
    print(myFunction(formatted_corpus))

    column_names_u = ['id', 'form', 'lemma', 'upostag',
                      'xpostag', 'feats', 'head', 'deprel', 'deps', 'misc']
    """
    filesTest = [
        './Universal/ud-treebanks-v1.3/UD_Swedish/sv-ud-train.conllu',
        './Universal/ud-treebanks-v1.3/UD_English/en-ud-train.conllu',
        './Universal/ud-treebanks-v1.3/UD_Chinese/zh-ud-train.conllu'

    ]
    for train_file in filesTest:
        print(train_file)
        sentences = read_sentences(train_file)
        formatted_corpus = split_rows(sentences, column_names_u)
        result = myFunction(formatted_corpus)
        print(result)
        print("========NEW========")
    """
