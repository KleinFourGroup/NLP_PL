
import os
import plyj.parser
import ExtractCode as e
import copy
import random

def matchPackages(sent, v_list, imports):
    staticFields = []
    for im in imports:
        end = im.split('.')[-1]
        for v_dec in v_list:
            sl = v_dec[1].split('.')
            if sl[0] == end:
                if len(sl) > 1:
                    v_dec[1] = im + '.' + '.'.join(sl[1:])
                else:
                    v_dec[1] = im
        for stat in sent:
            try:
                for i in range(len(stat)):
                    sl = stat[i].split('.')
                    if sl[0] == end:
                        if len(sl) > 1:
                            stat[i] = im + '.' + '.'.join(sl[1:])
                            staticFields.append(stat[i])
                        else:
                            stat[i] = im
            except:
                pass
    return staticFields

def resolveFields(sent, v_list, imports):
    fields = []
    for stat in sent:
        for i in range(len(stat)):
            sl = stat[i].split('.')
            if len(sl) > 1:
                for v_dec in v_list:
                    if v_dec[2] == sl[0]:
                        stat[i] = v_dec[1] + ':' + '.'.join(sl[1:])
                        fields.append(v_dec[1] + ':' + '.'.join(sl[1:]))
                for im in imports: #This shouldn't happen
                    end = im.split('.')[-1]
                    if sl[0] == end:
                        stat[i] = im + '::' + '.'.join(sl[1:])
    return fields

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
    
def isChar(s):
    try:
        return s[0] == "'" and s[-1] == "'"
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
                    sig.append("EXP")
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
                        elif isChar(stat[i]):
                            sig.append("char")
                        elif isBool(stat[i]):
                            sig.append("boolean")
                        elif '::' in stat[i]:
                            sig.append("FIELD")
                        else:
                            sig.append("UNK")
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
            if not (sig[i] == "EXP" or sig[i] == "FIELD"):
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
    
def getSeqs(cu, mode = "levels", lvars = []):
    v_list = copy.deepcopy(lvars)
    v_list.extend(copy.deepcopy(cu.v_list))
    sent = []
    sents = []
    if mode == "levels":
        for stat in cu.body:
            if not type(stat) == type(cu):
                sent.append(stat)
            else:
                sents.extend(getSeqs(stat, mode, v_list))
        if len(sent) > 0:
            sents.insert(0, (sent, v_list))
    elif mode == "contiguous":
        pass
    else:
        print "Mode '" + str(mode) + "' unknown"
    return sents

def prod(l1, l2):
    l = []
    for s1 in l1:
        for s2 in l2:
            n = copy.deepcopy(s1)
            n.extend(s2)
            l.append(n)
    return l

def purge(l):
    p = []
    toAdd = False
    for s in l:
        if len(s)>0:
            p.append(s)
        else:
            toAdd = True
    if toAdd:
        p.append([])
    return p

def getCFS(cu, pre = ""):
    #print pre + cu.name
    sents = [[]]
    dsents = []
    if cu.name == "IfThenElse" or cu.name == "Switch" or cu.name == "Catches":
        sents = []
        for c in cu.body:
            s, sd = getCFS(c, pre + '  ')
            sents.extend(s)
            dsents.extend(sd)
            #print pre + str(len(sents))# + ": " + '-'.join(map(str, map(len, sents)))
        if len(sents) == 0:
            sents = [[]]
    else:
        for stat in cu.body:
            if not type(stat) == type(cu):
                sents = prod(sents, [[stat]])
            else:
                s, sd = getCFS(stat, pre + '  ')
                if len(s) > 0:
                    sents = prod(sents, s)
                dsents.extend(sd)
            #print pre + str(len(sents))# + ": " + '-'.join(map(str, map(len, sents)))
    #print ']'
    if "Declaration" in cu.name:
        sents.extend(dsents)
        return [[]], purge(sents)
    else:
        return purge(sents), purge(dsents)

def getSentences(cu, mode = "cfs"):
    cu = copy.deepcopy(cu)
    cu.stripToFunctions()
    cu.renameVars()
    if mode == "cfs":
        sents, dsents = getCFS(cu)
        sents.extend(dsents)
        for i in range(len(sents)):
            sents[i] = (copy.deepcopy(sents[i]), copy.deepcopy(cu.dumpVars()))
        return sents
    else:
        sents = getSeqs(cu, mode)
        return copy.deepcopy(sents)
        
    
def main():
    par = plyj.parser.Parser()
    file_path = "../Java/Corpus/"
    cul = []
    vocab = {}
    sentlens = {}
    sf = []
    fields = []
    ctr = 1
    for subdir, dirs, files in os.walk(file_path):
        for f in files:
            if f.endswith(".java"):
                p = os.path.join(subdir, f)
                cus = e.ExtractCode(par, p)
                #cul.extend(cus)
            for i, cu in cus:
                #print cu.getStr()
                sents = getSentences(cu, "cfs")
                print str(ctr) + ": " + str(len(sents))
                ctr += 1
                for sent, vl in sents:
                    sf2 = matchPackages(sent, vl, i)
                    sf.extend(sf2)
                    #print str(len(sf)) + " importables"
                    resolveFunctions(sent, vl, i)
                    newsent = stripToAPI(sent, vl, i)
                    fi = resolveFields(newsent, vl, i)
                    fields.extend(fi)
                    #print str(len(fields)) + " fields"
                    if not len(newsent) in sentlens:
                        sentlens[len(newsent)] = 0
                    sentlens[len(newsent)] += 1
                    if len(newsent) > 0:
                        for stat in newsent:
                            s = getSig(stat, vl)
                            if not s[0] in vocab:
                                vocab[s[0]] = []
                            vocab[s[0]].append(s[1:])
            #break
    for s in vocab:
        print s
        for sig in resolveSigs(vocab[s]):
            print '\t' + e.nstr(sig)
    print len(vocab)
    print len(set(sf))
    print len(set(fields))
    print sentlens
        
if __name__ == "__main__":
    main()
