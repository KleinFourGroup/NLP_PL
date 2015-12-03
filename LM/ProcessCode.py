
import os
import plyj.parser
import ExtractCode as e
import copy
import random

def matchPackages(sent, v_list, imports):
    for v_dec in v_list:
        for im in imports:
            end = im.split('.')[-1]
            if v_dec[1] == end:
                v_dec[1] = im
    for stat in sent:
        try:
            for i in range(len(stat)):
                for im in imports:
                    end = im.split('.')[-1]
                    if stat[i] == end:
                        stat[i] = im
        except:
            pass

def resolveFields(sent, v_list, imports):
    for stat in sent:
        for i in range(len(stat)):
            if len(stat[i].split('.')) > 1:
                for v_dec in v_list:
                    if v_dec[2] == stat[i].split('.')[0]:
                        stat[i] = v_dec[1] + ':' + '.'.join(stat[i].split('.')[1:])
                for im in imports:
                    end = im.split('.')[-1]
                    if stat[i].split('.')[0] == end:
                        stat[i] = im + '::' + '.'.join(stat[i].split('.')[1:])

def resolveFunctions(sent, v_list, imports):
    for stat in sent:
        try:
            if stat[0] == "call":
                for v_dec in v_list:
                    if v_dec[2] == stat[3]:
                        stat[1] = v_dec[1] + '$' + stat[1]
                for im in imports:
                    if im == stat[3]:
                        stat[1] = im + '$' + stat[1]
                        stat[3] = "this"
        except:
            pass

def stripToAPI(sent, v_list, imports):
    newsent = []
    for stat in sent:
        try:
            if stat[0] == "call":
                if stat[1].split('.')[0] == "android":
                    newsent.append(stat)
        except:
            pass
    return newsent

def isInt(s):
    try:
        int(s)
        return True
    except:
        return False
    
def isFloat(s):
    try:
        int(s)
        return True
    except:
        return False
    
def isString(s):
    try:
        isStr = False
        if s[0] == '"' and s[-1] == '"':
            isStr = True
            for j in range(1, len(s) - 1):
                if s[j] == '"' and not s[j-1] == '\\':
                    isStr = False
        return isStr
    except:
        return False
    
def isBool(s):
    return s == "true" or s == "false"

def getSig(stat, v_list):
    sig = []
    try:
        if stat[0] == "call":
            sig.append(stat[1])
            for i in range(2, len(stat)):
                if stat[i] == "@0" or stat[i] == "this":
                    sig.append(stat[i])
                elif stat[i][0] == '@':
                    sig.append("UNK")
                else:
                    b = True
                    for var in v_list:
                        if stat[i] == var[2]:
                            sig.append(var[1])
                            b = False
                    if b:
                        if isInt(stat[i]):
                            sig.append("int")
                        elif isFloat(stat[i]):
                            sig.append("float")
                        elif isString(stat[i]):
                            sig.append("String")
                        elif isBool(stat[i]):
                            sig.append("boolean")
                        elif ':' in stat[i]:
                            sig.append("FIELD")
                        else:
                            sig.append(stat[i])
    except:
        pass
    return sig

def resolveSigs(siglist):
    sigs = {}
    for sig in siglist:
        l = len(sig)
        if not l in sigs:
            sigs[l] = [set(["UNK"]) for i in range(l)]
        for i in range(l):
            sigs[l][i].add(sig[i])
    strsigs = []
    for l in sigs:
        line = []
        for i in range(l):
            if len(sigs[l][i]) > 1:
                sigs[l][i].remove("UNK")
            line.append('/'.join(sigs[l][i]))
        strsigs.append(line)
    return strsigs
    
def getSentences(cu, mode = "levels", lvars = []):
    v_list = copy.deepcopy(lvars)
    v_list.extend(copy.deepcopy(cu.v_list))
    sent = []
    sents = []
    if mode == "levels":
        for stat in cu.body:
            if not type(stat) == type(cu):
                sent.append(stat)
            else:
                sents.extend(getSentences(stat, mode, v_list))
        if len(sent) > 0:
            sents.insert(0, (v_list, sent))
    elif mode == "contiguous":
        pass
    else:
        print "Mode '" + str(mode) + "' unknown"
    return sents

def main():
    par = plyj.parser.Parser()
    file_path = "../Java/Corpus/"
    cul = []
    vocab = {}
    for subdir, dirs, files in os.walk(file_path):
        for f in files:
            if f.endswith(".java"):
                p = os.path.join(subdir, f)
                cus = e.ExtractCode(par, p)
                cul.extend(cus)
    for i, cu in cul:
        sents = getSentences(cu)
        #print cu.getStr()
        for vl, sent in sents:
            matchPackages(sent, vl, i)
            resolveFields(sent, vl, i)
            resolveFunctions(sent, vl, i)
            newsent = stripToAPI(sent, vl, i)
            if len(newsent) > 0:
                for stat in newsent:
                    s = getSig(stat, vl)
                    if not s[0] in vocab:
                        vocab[s[0]] = []
                    vocab[s[0]].append(s[1:])
    for s in vocab:
        print s
        for sig in resolveSigs(vocab[s]):
            print '\t' + e.nstr(sig)
        
if __name__ == "__main__":
    main()
