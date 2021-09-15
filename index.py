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
from base import convert_to_base, convert_from_base

# inverted index will map from token to 6 different fields (Title, Infobox, Body, Category, Links and References in that specific order)
field_map = {'t':0,'i':1,'b':2,'c':3,'l':4,'r':5,}
invindex = {}
num_inv_tokens = 0
dumpNum = 1
count = 0
# empty_ind_list = [set(),set(),set(),set(),set(),set()]
# empty_ind_list = [list(),list(),list(),list(),list(),list()]
# empty_ind_list = [dict(),dict(),dict(),dict(),dict(),dict()]
# def setUniv(id)

def dumpIt(num):
    keys = sorted(invindex.keys())
    to_write=""
    for k in keys:
        to_write += k + " " + convert_to_base(invindex[k][6]) + "\n"
        for i in range(6):
            docs = sorted(invindex[k][i].keys())
            for id in docs:
                freq = convert_to_base(invindex[k][i][id])
                while(len(freq)<2):
                    freq = "0" + freq
                to_write += convert_to_base(id) + freq + " "
            to_write += "\n"
    with open(os.path.join(sys.argv[2],str(num) + ".txt"), "a") as f:
        f.write(to_write)
                

# def addToPosting (tok, category, id):
#     e_id = convert_to_base(id)
#     for idtf in invindex[tok][field_map[category]]:
#         if idtf[:-2] == e_id:
#             newtf = convert_to_base(convert_from_base(idtf[-2:])+1)
#             while len(newtf) < 2:
#                 newtf = "0" + newtf
#             idtf = idtf[:-2] + newtf
#             return
#     invindex[tok][field_map[category]].append(e_id + "01")
#     return

def addToIndex (tokens, id, category):
    for tok in tokens:
        if not tok.isalnum():
            continue
        if tok not in invindex:
            invindex[tok]=[dict(),dict(),dict(),dict(),dict(),dict(),0]
        if id not in invindex[tok][field_map[category]]:
            invindex[tok][field_map[category]][id] = 0
        invindex[tok][field_map[category]][id] += 1
        invindex[tok][6] += 1
        

snowman = SnowballStemmer('english')
stop_words = set(nltk.corpus.stopwords.words('english'))
stemdict = {}
def snowball(token):
    if token not in stemdict:
        stemdict[token] = snowman.stem(token)
    return stemdict[token]

def process (text, id, category):
    # tokenization
    # tokens = nltk.word_tokenize(text)
    tokens = nltk.regexp_tokenize(text, pattern='\s+', gaps=True)
    # stopwords removal, case folding, and stemming
    tokens = [snowball(w) for w in tokens if not w in stop_words]
    addToIndex(tokens, id, category)

def clean(text):
    text = text.replace('"',r' ').replace('!',r' ').replace('@',r' ').replace('#',r' ').replace('&',r' ').replace('*',r' ').replace('(',r' ').replace(')',r' ').replace('-',r' ').replace('_',r' ').replace('+',r' ').replace('=',r' ').replace('{',r' ').replace('}',r' ').replace('[',r' ').replace(']',r' ').replace(':',r' ').replace(';',r' ').replace(',',r' ').replace('.',r' ').replace('<',r' ').replace('>',r' ').replace('/',r' ').replace('?',r' ').replace('\\',r' ').replace('^',r' ').replace('~',r' ').replace('|',r' ').replace("'",r' ').replace('`',r' ').replace('$',r' ').replace('%',r' ')
    return text


def bruhThisIsGonnaBeAPain(text, id):

    # Categories
    lowered = text.lower()
    Categories = ""
    res = re.search(r'\[\[category:(.*?)\]\]',lowered)
    while res != None:
        Categories += lowered[res.span()[0]+11:res.span()[1]-2] + ' '
        lowered = lowered[:res.span()[0]] + lowered[res.span()[1]:]
        res = re.search(r'\[\[category:(.*?)\]\]',lowered)
    process(clean(Categories), id, 'c')

    # References
    ref_text = ""
    res1 = re.search(r'=( *)references( *)(=+)',lowered)
    if res1 != None:
        res2 = re.search(r'(==(.*?)==|\n\{\{(?!reflist)|\n\[)',lowered[res1.span()[1]:])
        ans = -1
        if res2 != None:
            ans = res2.span()[0]+res1.span()[1]
        ref_text+=lowered[res1.span()[1]:ans]
        lowered = lowered[:res1.span()[0]] + lowered[ans:]
    process(clean(ref_text), id, 'r')

  # External Links
    ext_text = ""
    res1 = re.search(r'=( *)external links( *)(=+)',lowered)
    # print(res1)/
    if res1 != None:
        res2 = re.search(r'\n\n',lowered[res1.span()[1]:])
        ans = -1
        if res2 != None:
        # print(res2)
            ans = res2.span()[0] + res1.span()[1]
        ext_text+=lowered[res1.span()[1]:ans]
        lowered = lowered[:res1.span()[0]] + lowered[ans:]
        # print(ext_text)
    process(clean(ext_text), id, 'l')

  # Infobox
    lowered = re.sub(r'(\ *)\n','',lowered)
    InfoBox = ""
    res = re.search(r'\{\{infobox(.*?)\}\}[^\|]',lowered)
    while res != None:
        InfoBox += lowered[res.span()[0]:res.span()[1]-1] + ' '
        lowered = lowered[:res.span()[0]] + lowered[res.span()[1]-1:]
        res = re.search(r'\{\{infobox(.*?)\}\}(\ *?)[^\|]',lowered)
    process(clean(InfoBox), id, 'i')

    process(clean(lowered), id, 'b')

class WikiXmlHandler(xml.sax.handler.ContentHandler):
    """Content handler for Wiki XML data using SAX"""
    def __init__(self):
        xml.sax.handler.ContentHandler.__init__(self)
        self.buffer = ""
        self.doc_id = 0
        self.mode = "none"
        self.title = ''
        

    def characters(self, content):
        """Characters between opening and closing tags"""
        if self.mode != "none":
            self.buffer += content
    def startElement(self, name, attrs):
        """Opening tag of element"""
        if name == "page":
            self.mode = "page"
        elif name == "revision":
            self.mode = "revision"
        self.buffer=""
        
    def endElement(self, name):
        global num_inv_tokens, dumpNum, invindex, count
        """Closing tag of element"""
        if self.mode == "page" and name == "title":
            self.title = self.buffer
            self.buffer = ""
        elif self.mode == "page" and name == "id":
            self.id = int(float(self.buffer))
            self.buffer = ""
            count += 1
            if(count % 50000 == 0):
                # dump and empty invindex
                num_inv_tokens += len(invindex.keys())
                print("DUMPED")
                dumpIt(dumpNum)
                dumpNum+=1
                invindex={}
            process(clean(self.title),self.id,'t')
        elif self.mode == "revision" and name == "text":
            bruhThisIsGonnaBeAPain(self.buffer, self.id)

WikiParse = xml.sax.make_parser()
WikiParse.setContentHandler(WikiXmlHandler())

if len(sys.argv) != 4:
    print('''  ^~^  ,\n ('Y') )\n /   \/ \n(\|||/)\nPls gib arguments properly, exacc 3''')

try:
    with open(sys.argv[1], "r") as f:
        start = time()
        line = " "
        count = 0
        x=0
        while line != '':
            # Get next line from file 
            # line = lines[count]
            # count += 1
            line = f.readline()
            WikiParse.feed(line)
            if count%10000==0:
                print(count)
                print(time()-start)
            count += 1
        print(time()-start)
except:
    print('''  ^~^  ,\n ('Y') )\n /   \/ \n(\|||/)\nPls gib Path properly''')

dumpIt(dumpNum)
with open(sys.argv[3], "w+") as f:
    f.write(str(num_inv_tokens) + '\n')
    f.write(str(dumpNum) + '\n')
    # get size of all index files combined

# print("dumping")
# start = time()
# try:
#     with open(os.path.join(sys.argv[2],"index.json"), "w+") as f:
#         for tok in invindex:
#             for i in range(6):
#                 invindex[tok][i] = list(invindex[tok][i])
#         # print(type(invindex))
#         json.dump(invindex,f)
#     # fakedump(invindex,os.path.join(sys.argv[2],"index.json"))
# except:
#     print('''  ^~^  ,\n ('Y') )\n /   \/ \n(\|||/)\nPls gib Path properly''')
print(time()-start)
print(count)