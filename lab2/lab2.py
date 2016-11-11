
"""
Concordance program to find all the concordances
of a pattern surrounded by width characters.
Usage: python concord.py file pattern width
"""
__author__ = "Pierre Nugues"

import sys

file_name = "Selma.txt"
pattern = "Nils"
width = 10
try:
    file = open(file_name)
except:
    print("Could not open file", file_name)
    exit(0)

text = file.read()
testText = "Jag vet inte att det ska vara så. Men det kan inte vara så svårt att säga nej! Eller är det de?"

"""
Tokenizers
Usage: python tokenizer.py < corpus.txt
"""
__author__ = "Pierre Nugues"

import sys
import regex as re


def tokenize4(text):
    """uses the punctuation and symbols to break the text into words
    returns a list of words"""
    spaced_tokens = re.sub('([\p{S}\p{P}])', r' \1 ', text)
    one_token_per_line = re.sub('\s+', '\n', spaced_tokens)
    tokens = one_token_per_line.split()
    return tokens


def setTag(words):
    tagedList = []
    pattern = re.compile("[\.\?\!]")
    start = True
    for word in words:
        tagedWord = word
        if pattern.match(word) and not start:
            start = True
            tagedWord = "</s>"
        elif word.istitle() and start:
            start = False
            tagedList.append("<s>")
        tagedList.append(tagedWord.lower())
    return tagedList


def count_ngrams(words, n):
    ngrams = [tuple(words[inx:inx + n])
              for inx in range(len(words) - n + 1)]
    # "\t".join(words[inx:inx + n])
    frequencies = {}
    for ngram in ngrams:
        if ngram in frequencies:
            frequencies[ngram] += 1
        else:
            frequencies[ngram] = 1
    return frequencies


def sentence_prob_uni(words, frequency_unigrams):
    sentences = {}
    current_prob = 1
    current_sentence = ""
    N = len(words)
    for word in words:
        if word == "</s>":
            sentences[current_sentence] = current_prob
            current_prob = 1
            current_sentence = ""
        elif not word == "<s>":
            current_prob *= frequency_unigrams[(word,)] / N
            current_sentence += " " + word
    return sentences


def sentence_prob_bi(words):
    unigram_freq = count_ngrams(words, 1)
    bigram_freq = count_ngrams(words, 2)
    sentences = {}
    current_prob = 1
    current_sentence = ""
    N = len(words)
    for i in range(N - 1):
        if words[i] == "</s>":
            sentences[current_sentence] = current_prob
            current_prob = 1
            current_sentence = ""
        ci = unigram_freq[(words[i],)]
        ciCi = bigram_freq[(words[i], words[i + 1])]
        p = ciCi / ci
        current_prob *= p
        current_sentence += words[i] + " "
    return sentences

import math


def bigrams(words, testWords):
    print("Bigram model")

    unigram_freq = count_ngrams(words, 1)
    bigram_freq = count_ngrams(words, 2)
    current_prob = 1
    current_sentence = ""
    sentences = {}
    N = len(testWords)
    for i in range(N):
        if testWords[i] == "</s>":
            sentences[current_sentence] = current_prob
            print("Prob. bigrams: " + str(current_prob))
            entropy = math.log2(current_prob) * \
                (-1 / len(tokenize4(current_sentence)))
            current_prob = 1
            current_sentence = ""

            print("Entropy rate: " + str(entropy))
            perplexity = math.pow(2, entropy)
            print("Perplexity " + str(perplexity))
        ci = unigram_freq[(testWords[i],)]
        if not i == N - 1:
            nextWord = testWords[i + 1]
            try:
                ciCi = bigram_freq[(testWords[i], testWords[i + 1])]
                p = ciCi / ci
            except:
                p = ci / len(words)

            current_prob *= p
            current_sentence += testWords[i] + " "
            print(testWords[i] + "\t" + str(nextWord) +
                  "\t" + str(ciCi) + "\t" + str(ci) + "\t" + str(p))

    return sentences

def unigrams(words, testWords):
    print("Unigram model")

    unigram_freq = count_ngrams(words, 1)
    bigram_freq = count_ngrams(words, 2)
    current_prob = 1
    current_sentence = ""
    sentences = {}
    N = len(testWords)
    for i in range(N):
        if testWords[i] == "</s>":
            sentences[current_sentence] = current_prob
            print("Prob. Unigram: " + str(current_prob))
            entropy = math.log2(current_prob) * \
                (-1 / len(tokenize4(current_sentence)))
            current_prob = 1
            current_sentence = ""

            print("Entropy rate: " + str(entropy))
            perplexity = math.pow(2, entropy)
            print("Perplexity " + str(perplexity))
        ci = unigram_freq[(testWords[i],)]
        if not i == N - 1:
            nextWord = testWords[i + 1]
            p = ci / len(words)

            current_prob *= p
            current_sentence += testWords[i] + " "
            print(testWords[i] + "\t" + str(nextWord) +
                   "\t" + str(ci) + "\t" + str(len(words)) + "\t" + str(p))

    return sentences

if __name__ == '__main__':
    words = tokenize4(text)
    words = setTag(words)
    n = 1
    frequency_ngrams = count_ngrams(words, n)
    suma = 0
    """for ngram in frequency_ngrams:
        print(frequency_ngrams[ngram], "\t", ngram)
        suma += frequency_ngrams[ngram]
"""
    testText = "Det var en gång en katt som hette Nils."
    testWords = tokenize4(testText)
    testWords = setTag(testWords)
    unigrams(tokenize4(text),  tokenize4(testText))
    bigrams(words, testWords)
