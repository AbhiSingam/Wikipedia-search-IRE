import pickle
import sys
import re
import os
import sys
from time import time
import nltk
import xml.sax
import json
nltk.download('stopwords')
nltk.download('punkt')
from nltk.stem import SnowballStemmer

# inverted index will map from token to 6 different fields (Title, Infobox, Body, Category, Links and References in that specific order)
field_map = {'t':0,'i':1,'b':2,'c':3,'l':4,'r':5,}

snowman = SnowballStemmer('english')
stop_words = set(nltk.corpus.stopwords.words('english'))

def clean(text):
    text = text.replace('"',r' ').replace('!',r' ').replace('@',r' ').replace('#',r' ').replace('&',r' ').replace('*',r' ').replace('(',r' ').replace(')',r' ').replace('-',r' ').replace('_',r' ').replace('+',r' ').replace('=',r' ').replace('{',r' ').replace('}',r' ').replace('[',r' ').replace(']',r' ').replace(':',r' ').replace(';',r' ').replace(',',r' ').replace('.',r' ').replace('<',r' ').replace('>',r' ').replace('/',r' ').replace('?',r' ').replace('\\',r' ').replace('^',r' ').replace('~',r' ').replace('|',r' ').replace("'",r' ').replace('`',r' ')
    return text

with open(sys.argv[1],"r") as f:
    invindex = json.load(f)
    query = sys.argv[2]
    tokens = [w.lower() for w in clean(query.replace("t:",r' ').replace("i:",r' ').replace("b:",r' ').replace("c:",r' ').replace("r:",r' ').replace("l:",r' ')).split(" ") if w!=""]
    stemmed = [snowman.stem(w) for w in tokens]

    print("{")
    for i, stem in enumerate(stemmed):
        print('"' + tokens[i] + '":{')
        print("\"title\":", end="")
        print(str(invindex[stem][0]),end=",\n")
        print("\"infobox\":", end="")
        print(str(invindex[stem][1]),end=",\n")
        print("\"body\":", end="")
        print(str(invindex[stem][2]),end=",\n")
        print("\"categories\":", end="")
        print(str(invindex[stem][3]),end=",\n")
        print("\"references\":", end="")
        print(str(invindex[stem][4]),end=",\n")
        print("\"links\":", end="")
        print(str(invindex[stem][5]),end=",\n")
        print("},")
    print("}")