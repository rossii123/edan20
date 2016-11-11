import os
import re

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

files = get_files("Selma", "txt")
words = {}
for file in files:

    text = open("./Selma/" + file, "r")
    for m in re.finditer(r"\w+", text.read()):

        word = m.group(0)
        print(m.start())
        if not word in words:
            words[word] = {}
        if not str(file) in words[word]:
            words[word][str(file)] = []
        words[word][str(file)].append[m.start()]

#print(words["hej"])
