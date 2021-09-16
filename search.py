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

# snowman = SnowballStemmer('english')
# stop_words = set(nltk.corpus.stopwords.words('english'))

# def clean(text):
#     text = text.replace('"',r' ').replace('!',r' ').replace('@',r' ').replace('#',r' ').replace('&',r' ').replace('*',r' ').replace('(',r' ').replace(')',r' ').replace('-',r' ').replace('_',r' ').replace('+',r' ').replace('=',r' ').replace('{',r' ').replace('}',r' ').replace('[',r' ').replace(']',r' ').replace(':',r' ').replace(';',r' ').replace(',',r' ').replace('.',r' ').replace('<',r' ').replace('>',r' ').replace('/',r' ').replace('?',r' ').replace('\\',r' ').replace('^',r' ').replace('~',r' ').replace('|',r' ').replace("'",r' ').replace('`',r' ')
#     return text

# with open(sys.argv[1],"r") as f:
#     invindex = json.load(f)
#     query = sys.argv[2]
#     tokens = [w.lower() for w in clean(query.replace("t:",r' ').replace("i:",r' ').replace("b:",r' ').replace("c:",r' ').replace("r:",r' ').replace("l:",r' ')).split(" ") if w!=""]
#     stemmed = [snowman.stem(w) for w in tokens]

#     print("{")
#     for i, stem in enumerate(stemmed):
#         print('"' + tokens[i] + '":{')
#         print("\"title\":", end="")
#         print(str(invindex[stem][0]),end=",\n")
#         print("\"infobox\":", end="")
#         print(str(invindex[stem][1]),end=",\n")
#         print("\"body\":", end="")
#         print(str(invindex[stem][2]),end=",\n")
#         print("\"categories\":", end="")
#         print(str(invindex[stem][3]),end=",\n")
#         print("\"references\":", end="")
#         print(str(invindex[stem][4]),end=",\n")
#         print("\"links\":", end="")
#         print(str(invindex[stem][5]),end=",\n")
#         print("},")
#     print("}")

snowman = SnowballStemmer('english')
stop_words = set(nltk.corpus.stopwords.words('english'))
stemdict = {}
def snowball(token):
    if token not in stemdict:
        stemdict[token] = snowman.stem(token)
    return stemdict[token]

def process (text):
    # tokenization
    # tokens = nltk.word_tokenize(text)
    tokens = nltk.regexp_tokenize(text, pattern='\s+', gaps=True)
    # stopwords removal, case folding, and stemming
    tokens = [snowball(w) for w in tokens if not w in stop_words]
    return tokens

index_loc = sys.argv[1]
query_file = sys.argv[2]

with open(query_file,'r') as f:
    queries = f.readlines()

for q in queries:
    q = q.split(":")
    fields = ['','','','','','',''] # title infobox body category links references general
    if len(q) == 0:
        print("Error in parsing input file")
    elif len(q) == 1:
        # no field queries
        fields[6] = q[0]
    else:
        # has field queries
        if len(q[0]) == 0:
            print("Error in parsing general query")
        elif len(q[0]) == 1:
            # no general query
            for i in range(len(q)-1):
                fields[field_map[q[i][-1]]] = 
        else:
            # both field and general query
