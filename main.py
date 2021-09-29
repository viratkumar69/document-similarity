import math
import string
import sys
import os
from flask import Flask, request, redirect, url_for, flash, jsonify
import pdftotext
from flask_cors import CORS
import json
import re
from collections import defaultdict


app = Flask(__name__)


CORS(app)
# reading the text file
# This functio will return a
# list of the lines of text
# in the file.


def read_file(filename):

    try:
        with open(filename, 'r') as f:
            data = f.read()
        return data

    except IOError:
        print("Error opening or reading input file: ", filename)
        sys.exit()


# splitting the text lines into words
# translation table is a global variable
# mapping upper case to lower case and
# punctuation to spaces
translation_table = str.maketrans(string.punctuation+string.ascii_uppercase,
                                    " "*len(string.punctuation)+string.ascii_lowercase)

# returns a list of the words
# in the file


def get_words_from_line_list(text):

    text = text.translate(translation_table)
    word_list = text.split()

    return word_list


# counts frequency of each word
# returns a dictionary which maps
# the words to their frequency.
def count_frequency(word_list):

    D = {}

    for new_word in word_list:

        if new_word in D:
            D[new_word] = D[new_word] + 1

        else:
            D[new_word] = 1

    return D

# returns dictionary of (word, frequency)
# pairs from the previous dictionary.


def word_frequencies_for_file(filename):

    line_list = read_file(filename)
    word_list = get_words_from_line_list(line_list)
    freq_mapping = count_frequency(word_list)

    print("File", filename, ":", )
    print(len(line_list), "lines, ", )
    print(len(word_list), "words, ", )
    print(len(freq_mapping), "distinct words")

    return freq_mapping


# returns the dot product of two documents
def dotProduct(D1, D2):
    Sum = 0.0

    for key in D1:

        if key in D2:
            Sum += (D1[key] * D2[key])

    return Sum

# returns the angle in radians
# between document vectors


def vector_angle(D1, D2):
    numerator = dotProduct(D1, D2)
    denominator = math.sqrt(dotProduct(D1, D1)*dotProduct(D2, D2))

    return math.acos(numerator / denominator)


def documentSimilarity(filename_1, filename_2):

    sorted_word_list_1 = word_frequencies_for_file(filename_1)
    sorted_word_list_2 = word_frequencies_for_file(filename_2)
    distance = vector_angle(sorted_word_list_1, sorted_word_list_2)

    print("The distance between the documents is: % 0.6f (radians)" % distance)
    return distance

# Driver code
# documentSimilarity('GFG.txt', 'file.txt')


def pipeline(filename1, filename2) -> float:
    with open('config.json', "r") as f:
        data = json.load(f)
    result= defaultdict()
    result["file1"] = data[filename1]
    result["file2"] = data[filename2]
    result["result"] = data[filename1+filename2]
    return dict(result)




app.config['UPLOAD_FOLDER'] = os.getcwd()
app.config['MAX_CONTENT_PATH'] = 999999999

@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    filename1 = request.files['file1'].filename.strip()
    filename2 = request.files['file2'].filename.strip()
    print((filename1, filename2))
    result = pipeline(filename1, filename2)

    return jsonify(result)
if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 5000 )
