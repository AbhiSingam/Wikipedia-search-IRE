from base import convert_from_base
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

def calcScore(tf, idf, category):
    tf = convert_from_base(tf)
    if category == 0:
        return 5 * (tf/idf)
    return tf/idf


for q in queries:
    start = time()
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
    docScores = {}
    for i, tokens in enumerate(procFields):
        if i<6:
            for token in tokens:
                postList, idf = getCategory(token,i)
                for doc in postList:
                    if doc[:-2] not in docScores:
                        docScores[doc[:-2]] = 0
                    docScores[doc[:-2]] += calcScore(doc[-2:],idf,i)
        else:       # for a general query, we take scores from all places, but scale them down
            for j in range(6):
                for token in tokens:
                    postList, idf = getCategory(token,j)
                    for doc in postList:
                        if doc[:-2] not in docScores:
                            docScores[doc[:-2]] = 0
                        docScores[doc[:-2]] += (1/4 * calcScore(doc[-2:],idf,j))
    
    toSort = []
    for i in docScores:
        toSort.append([docScores[i],i])
    toSort = sorted(toSort,reverse=True)[:10]
    for doc in toSort:
        print(convert_from_base(doc[1]) + ",",docname[doc[1]])
    print(time() - start)


    