import os
import regex as re
import math
import pickle


def get_files(dir, suffix):
    """
    Returns all the files in a folder ending with suffix
    :param dir:
    :param suffix:
    :return: the list of file names
    """
    files = []
    for file in os.listdir(dir):
        if file.endswith(suffix):
            files.append(file)
    return files


def compare(text1, text2):
    sum = 0
    absA = 0
    absB = 0
    for word in text1:
        sum += text1[word] * text2[word]
        absA += (text1[word])**2
        absB += (text2[word])**2
    return sum / (math.sqrt(absA) * math.sqrt(absB))


files = get_files("Selma", "txt")
print("files len ", len(files), files)
words = {}
text_sizes = {}
for file in files:
    text = open("./Selma/" + file, "r")
    text_sizes[file] = 0
    for m in re.finditer("\p{L}+", text.read().lower()):
        text_sizes[file] += 1
        word = m.group(0)
        if not word in words:
            words[word] = {}
        if not file in words[word]:
            words[word][file] = []
        words[word][file].append(m.start())

tfidfValues = {}
for file in files:
    text_size = text_sizes[file]
    tfidfValues[file] = {}
    for word in words:
        if file in words[word]:

            tf = len(words[word][file]) / text_size
            idf = math.log10(len(files) / len(words[word]))

            tfidf = tf * idf
            tfidfValues[file][word] = tfidf
        else:
            tfidfValues[file][word] = 0

matrix = {}
s = ""
for file in files:
    s += "\t" + file
print(s)
for file1 in files:
    row = file1
    for file2 in files:

        if not file1 in matrix:
            matrix[file1] = {}
        matrix[file1][file2] = compare(tfidfValues[file1], tfidfValues[file2])
        row += ("\t" +
                str(round(compare(tfidfValues[file1], tfidfValues[file2]), 10)))
    print(row)


#pickle.dump(tfidfValues, open("tfidfValues.p", "wb"))
