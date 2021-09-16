import pickle
import sys
import re
import os
import sys
from time import time
import nltk
import xml.sax
import json
# nltk.download('stopwords')
# nltk.download('punkt')
from nltk.stem import SnowballStemmer

# inverted index will map from token to 6 different fields (Title, Infobox, Body, Category, Links and References in that specific order)
field_map = {'t':0,'i':1,'b':2,'c':3,'l':4,'r':5,}

snowman = SnowballStemmer('english')
stop_words = set(nltk.corpus.stopwords.words('english'))
stemdict = {}
index_loc = sys.argv[1]
query_file = sys.argv[2]
# query_file = sys.argv[1]

with open(os.path.join(index_loc,"docend.json"),"r") as f:
    docend = json.load(f)

with open(os.path.join(index_loc,"docname.json"),"r") as f:
    docname = json.load(f)

with open(query_file,'r') as f:
    queries = f.readlines()

def snowball(token):
    if token not in stemdict:
        stemdict[token] = snowman.stem(token)
    return stemdict[token]

def clean(text):
    text = text.replace('"',r' ').replace('!',r' ').replace('@',r' ').replace('#',r' ').replace('&',r' ').replace('*',r' ').replace('(',r' ').replace(')',r' ').replace('-',r' ').replace('_',r' ').replace('+',r' ').replace('=',r' ').replace('{',r' ').replace('}',r' ').replace('[',r' ').replace(']',r' ').replace(':',r' ').replace(';',r' ').replace(',',r' ').replace('.',r' ').replace('<',r' ').replace('>',r' ').replace('/',r' ').replace('?',r' ').replace('\\',r' ').replace('^',r' ').replace('~',r' ').replace('|',r' ').replace("'",r' ').replace('`',r' ').replace('$',r' ').replace('%',r' ')
    return text

def process (text):
    text = clean(text)
    tokens = nltk.regexp_tokenize(text, pattern='\s+', gaps=True)
    tokens = [snowball(w) for w in tokens if not w in stop_words]
    return tokens

def read7(f):
    out = []
    for i in range(7):
        out.append(f.readline())
    return out

def getCategory (token, category):

    file = ""

    for i in docend.keys():
        if token < docend[i]:
            file = os.path.join(sys.argv[1],"index" + i + ".txt")

    with open(file, "r") as f:
        cur = []
        while cur != ['','','','','','','']:
            cur = read7(f)
            if cur[0].split()[0] == token:
                return cur[1+category], cur[0].split()[1]
    return [], 1

for q in queries:
    print(q)
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
                if i<len(q)-2:
                    fields[field_map[q[i][-1]]] = q[i+1][:-1]
                else:
                    fields[field_map[q[i][-1]]] = q[i+1]
        else:
            # both field and general query
            fields[6] = q[0][:-1]
            for i in range(len(q)-1):
                if i<len(q)-2:
                    fields[field_map[q[i][-1]]] = q[i+1][:-1]
                else:
                    fields[field_map[q[i][-1]]] = q[i+1]
    # print(fields)
    procFields = []
    for field in fields:
        procFields.append(process(field))
        # print(field)
    # print(procFields)
    # print("\n")

    # getting posting lists and document frequency value

    