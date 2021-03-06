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
docname = {}
num_inv_tokens = 0
dumpNum = 0
count = 0
# empty_ind_list = [set(),set(),set(),set(),set(),set()]
# empty_ind_list = [list(),list(),list(),list(),list(),list()]
# empty_ind_list = [dict(),dict(),dict(),dict(),dict(),dict()]
# def setUniv(id)

def read7(f):
    out = []
    for i in range(7):
        out.append(f.readline())
    return out

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
        global dumpNum, invindex, count
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
                # num_inv_tokens += len(invindex.keys())
                print("DUMPED")
                dumpIt(dumpNum)
                dumpNum+=1
                invindex={}
            docname[self.id]=self.title.lower()
            process(clean(self.title.lower()),self.id,'t')
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
        count2 = 0
        x=0
        while line != '':
            # Get next line from file 
            # line = lines[count]
            # count += 1
            line = f.readline()
            WikiParse.feed(line)
            if count2%50000==0:
                print(count2)
                print(time()-start)
            count2 += 1
            # if dumpNum == 3:
            #     break
        print(time()-start)
except:
    print('''  ^~^  ,\n ('Y') )\n /   \/ \n(\|||/)\nPls gib Path properly''')

dumpIt(dumpNum)
with open(os.path.join(sys.argv[2],"docname.json"), "w+") as f:
    json.dump(docname,f)


# mergesort all the files together
fs = []
indexes = []
remain = []

for i in range(dumpNum+1):
    fs.append(open(os.path.join("./indexes/",str(i) + ".txt"),"r"))
    remain.append(i)
    indexes.append(['','','','','','',''])

last_inserted = "!"
count3 = 0
indf = []
to_write = []
docend = {}
print("\n\nMERGING\n\n")
# indf.append(open(os.path.join("./indexes/","index"+str(len(indf))+".txt"),"a"))
iter = 0
while(len(remain) > 0):
    iter += 1
    # print(iter)
    # if iter > 1000:
    #     break
    if iter % 100000 == 0:
        print("Merge:",str(iter))
        print(time() - start)
    to_find_min = []
    for i in remain:
        if indexes[i] == ['','','','','','','']:
            indexes[i]=read7(fs[i])
        if indexes[i] == ['','','','','','','']:
            remain.remove(i)
        else:
            to_find_min.append(indexes[i])
    if(len(to_find_min) == 0):
        break
    # print("++++++++++++++++")
    # print(to_find_min)
    # print("++++++++++++++++")
    ind = indexes.index(min(to_find_min))
    # print("----------------")
    # print(ind)
    # print(indexes[ind])
    # print("----------------")
    if last_inserted == indexes[ind][0].split()[0]:
        # print(last_inserted,indexes[ind][0].split(),"###")
        # print("if")
        # append the doc ids
        if(len(to_write) == 0):
            # to_write = indexes[ind]
            for line in to_write:
                indf[-1].write(line)
        else:
            for i in range(1,7):
                to_write[i] = to_write[i][:-1] + indexes[ind][i]
            num1 = convert_from_base(to_write[0].split()[1])
            num2 = convert_from_base(indexes[ind][0].split()[1])
            numFinal = convert_to_base(num1+num2)
            to_write[0] = to_write[0].split()[0] + " " + str(numFinal) + "\n"
        indexes[ind] = ['','','','','','','']
    else:
        # append the entire index
        # indf[-1].write(to_write)
        # print("else")x
        for line in to_write:
            indf[-1].write(line)
        if count3 % 1000000 == 0:
            if len(indf) > 0:
                docend[str(len(indf)-1)] = last_inserted
                indf[-1].close()
            indf.append(open(os.path.join("./indexes/","index"+str(len(indf))+".txt"),"a"))
        count3 += 1
        to_write = indexes[ind]
        last_inserted = indexes[ind][0].split()[0]
        indexes[ind] = ['','','','','','','']

docend[str(len(indf)-1)] = last_inserted
for line in to_write:
    indf[-1].write(line)
indf[-1].close()
for f in fs:
    f.close()

with open(os.path.join(sys.argv[2],"docend.json"), "w+") as f:
    json.dump(docend,f)

temp = os.listdir(sys.argv[2])
tot_ind_size = 0
for filename in temp:
    if filename[:5] == "index":
        curfile = os.path.join(sys.argv[2],filename)
        tot_ind_size += os.path.getsize(curfile)
        num_inv_tokens += (sum(1 for line in open(curfile)))//7


with open(sys.argv[3], "w+") as f:
    f.write(str(tot_ind_size/1000000000) + "\n")
    f.write(str(dumpNum) + '\n')
    f.write(str(num_inv_tokens) + '\n')
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