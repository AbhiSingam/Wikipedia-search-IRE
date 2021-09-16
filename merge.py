import os
from time import time
from base import convert_to_base, convert_from_base
buffers = []
linesRead = []
startTime = time()

# def loadMore(f,i):
#     buffers[i] = f.readlines()[linesRead[i]:linesRead[i]+70000]

def read7(f):
    out = []
    for i in range(7):
        out.append(f.readline())
    return out

dumpNum = 7

# mergesort all the files together
fs = []
indexes = []
remain = []

for i in range(dumpNum+1):
    fs.append(open(os.path.join("./indexes/",str(i) + ".txt"),"r"))
    remain.append(i)
    indexes.append(['','','','','','',''])

last_inserted = "!"
count = 0
indf = []
to_write = []
# indf.append(open(os.path.join("./indexes/","index"+str(len(indf))+".txt"),"a"))
iter = 0
while(len(remain) > 0):
    iter += 1
    # print(iter)
    # if iter > 1000:
    #     break
    if iter % 50000 == 0:
        print(iter)
        print(time() - startTime)
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
        if count % 1000000 == 0:
            if len(indf) > 0:
                indf[-1].close()
            indf.append(open(os.path.join("./indexes/","index"+str(len(indf))+".txt"),"a"))
        count += 1
        to_write = indexes[ind]
        last_inserted = indexes[ind][0].split()[0]
        indexes[ind] = ['','','','','','','']

for line in to_write:
    indf[-1].write(line)
indf[-1].close()
for f in fs:
    f.close()
# fs = []
# fs.append(open("./indexes/0.txt","r"))
# for i in range(10):
#     print(read7(fs[0])[0])