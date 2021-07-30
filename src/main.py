from collections import defaultdict
from tkinter import EW
from typing import Any, Dict, List
import numpy as np
import os
from sklearn.decomposition import PCA
import io

colours = defaultdict(lambda: 'lightblue', **{
    'af': '#F51AA4',
    'en': 'pink',
    'de': '#7CFFCB'
})

# These words were translated using a combination of google translate and my own translations.
# The latter few words were gotten from: https://www.englishclub.com/vocabulary/common-nouns-25.htm
all_words = {
    'af':['koning', 'hond', 'kat', 'koningin', 'boot', 'see', 'strand', 'kroon', 'seil', 'lewe', 'man', 'vrou', 'geskiedenis', 'verlede', 'now', 'toekoms'] + ['tyd', 'persoon', 'jaar', 'manier', 'dag', 'ding', 'man', 'wêreld', 'lewe', 'hand', 'deel', 'kind', 'oog', 'vrou', 'plek', 'werk', 'week', 'saak', 'punt', 'regering', 'geselskap', 'nommer', 'groep', 'probleem', 'feit',][:10],
    'en':['king', 'dog', 'cat', 'queen', 'boat', 'sea', 'beach', 'crown', 'sail', 'live', 'hamster', 'man', 'woman', 'royalty', 'history', 'story', 'past', 'present', 'future'] + ['time','person','year','way','day','thing','man','world','life','hand','part','child','eye','woman','place','work','week','case','point','government','company','number','group','problem','fact',][:10],
    'de':['König', 'hund', 'katze', 'Königin', 'boot', 'meer', 'strand', 'krone', 'segel', 'lebe', 'hamster', 'mann', 'frau', 'Königtum', 'geschichte', 'geschichte', 'Vergangenheit', 'jetzt', 'Zukunft'] + ['Zeit', 'Person', 'Jahr', 'Weg', 'Tag', 'Ding', 'Mann', 'Welt', 'Leben', 'Hand', 'Teil', 'Kind', 'Auge', 'Frau', 'Platz', 'Arbeit', 'Woche', 'Fall', 'Punkt', 'Regierung', 'Unternehmen', 'Nummer', 'Gruppe', 'Problem', 'Tatsache',][:10],
}
FILENAME = '~/Downloads/wiki.{lang}.align.vec'


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between a and b

    Returns:
        float: How similar two vectors ranging from being in opposite directions (-1) to being in the same direction (1)
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def write(dic: Dict[str, np.ndarray], name: str):
    """Writes the dictionary into a file using the fasttext format

    Args:
        dic (Dict[str, np.ndarray]): Dict of word -> vector
        name (str): The filename to write the dictionary to.
    """
    s = f"{len(dic)} 300\n"
    for key, value in dic.items():
        s += f"{key} {' '.join(map(str, value))}\n"
    with open(name, 'w+') as f:
        f.write(s)

def main(lang: str):
    """This goes over the words given in the below code inside a file FILENAME (with lang replaced with the given language)

        There must be a corresponding file in the path given by FILENAME. 
        This function writes some words into a smaller version of the given file, stored in 'smaller/{lang}_300_small_wiki.vec'
    Args:
        lang (str): The language to read and write.
    """
    name = FILENAME.format(lang=lang)
    words = all_words[lang]
    words = list(set(words))
    dic = {}
    # For each word,
    for word in words:
        # Look for it in the given file
        ans = os.popen(f"grep -i -m 1 '^{word} ' {name}").read()
        # a is the first line
        a = ans.split("\n")[0]
        if len(a) == 0:
            print(f"Word {word} is not found inside file {name}")
        # Of length 301, the first word is the actual word and the rest are the vector numbers.
        things = a.split(" ")
        dic[things[0].lower()] = np.array(list(map(float, things[1:])))
    # Save this
    write(dic, f'smaller/{lang}_300_small_wiki.vec')

def load_vectors(fname: str) -> Dict[str, np.ndarray]:
    """Takes in a filename and returns a dictionary of words -> np.ndarrays representing the word vectors.

    Args:
        fname (str): File to read from

    Returns:
        Dict[str, np.ndarray]
    """
    fin = io.open(fname, 'r', encoding='utf-8', newline='\n')
    n, d = map(int, fin.readline().split())
    data = {}
    for line in fin:
        tokens = line.rstrip().split(' ')
        data[tokens[0]] = np.array(list(map(float, tokens[1:])))
    return data

def save_js_dic(dic: Dict[str, np.ndarray], new_x: np.ndarray) -> Dict[str, Any]:
    """This takes in the dictionary, and the x values representing their reduced dimension representation
        and returns a dictionary that can be used in the javascript code for the displaying of the graph

    Args:
        dic (Dict[str, np.ndarray]): The words and their vectors
        new_x (np.ndarray): an np.ndarray of shape (len(dic), 2), containing the 2D representation of each word

    Returns:
        Dict[str, Any]: A JS object that contains node information.
    """
    keys = list(dic.keys())
    # we need a list of nodes and a distance matrix, which is actually the cosine similarity.
    dic_for_js = {
        'nodes': [],
        'dists': [[1 for _ in range(len(keys))] for _ in range(len(keys))]
    }
    # The colour of a word is determined by its language
    def col(w):
        return colours[w.split('_')[-1].lower()]

    # For all words
    for index, w1 in enumerate(keys):
        # for all pairs
        for index2, w2 in list(enumerate(keys))[index+1:]:
            va = dic[w1]
            vb = dic[w2]
            # write the distance
            sim = cosine_similarity(va, vb)
            dic_for_js['dists'][index][index2] = sim
            dic_for_js['dists'][index2][index] = sim

        # Add the node in, with it's PCA'd x and y position
        dic_for_js['nodes'].append({'id': index, 'label': w1, 'color': col(w1), 'x': new_x[index][0], 'y': new_x[index][1]})
    return (dic_for_js)

def make_js_dic_new_wiki(langs: List[str]):
    """This reads in the words and their vectors from the files, and writes the JS object representing all of the nodes
        to ../web/data.js

    Args:
        langs (List[str]): The list of languages
    """
    overall_dic = {}
    for lang in langs:
        # load the file
        file = f'smaller/{lang}_300_small_wiki.vec'
        dic = load_vectors(file)
        for k in dic:
            # add it to the dic with an underscore
            overall_dic[k + "_" + lang.upper()] = dic[k]

    # Do PCA to convert the 300D vectors to 2D
    X = np.array([overall_dic[k] for k in overall_dic])
    pca = PCA(n_components=2)
    new_x = pca.fit_transform(X)

    s = f"const data2 = {save_js_dic(overall_dic, new_x)}"
    with open('../web/data.js', 'w+') as f:
        f.write(s);



if __name__ == '__main__':
    langs = all_words.keys()
    for lang in langs:
        print(f"Parsing Language {lang}")
        main(lang)
    make_js_dic_new_wiki(langs); exit()
    