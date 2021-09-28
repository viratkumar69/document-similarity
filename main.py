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


def pipeline(file1, file2) -> float:
    with open(file1, "rb") as f:
        pdf1 = pdftotext.PDF(f)
    content1 = "\n".join(pdf1)

    with open(file2, "rb") as f:
        pdf2 = pdftotext.PDF(f)
    content2 = "\n".join(pdf2)
    with open('config.json', "r") as f:
        data = json.load(f)
    count_match = 0
    match = defaultdict()
    result = defaultdict()
    key_pair_document1 = defaultdict()
    key_pair_document2 = defaultdict()
    result["comments"] = ""
    for key in list(data.keys()):
        try:
            regex_match_document1 = re.findall(data[key], content1)
            regex_match_document2 = re.findall(data[key], content2)
            if len(regex_match_document1) > 0:
                key_pair_document1[key] = regex_match_document1[0].replace(key, "").replace(":", "").strip()
            if len(regex_match_document2) > 0:
                key_pair_document2[key] =  regex_match_document2[0].replace(key, "").replace(":", "").strip()
            match[key] = regex_match_document1[0] == regex_match_document2[0]
            if match[key]:
                count_match +=1
                result["comments"] = result["comments"] + "\n" + key +"\t matched"
        except Exception as e:
            print(e)
    result["similarity_score"] = count_match/len(list(data.keys()))
    result["flag"] = True if result["similarity_score"] > 0.4 else False 
    if match["Disease"] == False :
        result["flag"] = False
    result["Document_1_result"] = dict(key_pair_document1)
    result["Document_2_result"] = dict(key_pair_document2)
    return result




app.config['UPLOAD_FOLDER'] = os.getcwd()
app.config['MAX_CONTENT_PATH'] = 999999999

@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    f = request.files['file1']
    f.save("file1.pdf")
    f = request.files['file2']
    f.save("file2.pdf")
    similarity_score = pipeline("file1.pdf", "file2.pdf")

    return jsonify(similarity_score)
if __name__ == '__main__':
    app.run(host = '0.0.0.0',port = 5000 )
