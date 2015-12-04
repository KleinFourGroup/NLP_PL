
import os
import plyj.parser
import ExtractCode as e
import copy
import random


import TypeUtils as t

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
                        if t.isInt(stat[i]):
                            sig.append("int")
                        elif t.isFloat(stat[i]):
                            sig.append("float")
                        elif t.isString(stat[i]):
                            sig.append("String")
                        elif t.isChar(stat[i]):
                            sig.append("char")
                        elif t.isBool(stat[i]):
                            sig.append("boolean")
                        elif ':' in stat[i]:
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
    
import ExtractSequences as seq
    
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
            if f.endswith(".java") and "5a8beeae20366b5094d0db8148e0563" not in f and "3cd87ee90872cfcb72b3cb3b773d8efa" not in f:
                p = os.path.join(subdir, f)
                cus = e.ExtractCode(par, p)
                #cul.extend(cus)
            for i, cu in cus:
                #print cu.getStr()
                sf2, fi, sents = seq.getSents(cu, i, "levels")
                sf.extend(sf2)
                fields.extend(fi)
                print str(ctr) + ": " + str(len(sents))
                ctr += 1
                for sent, vl in sents:
                    #print str(len(sf)) + " importables"
                    #print str(len(fields)) + " fields"
                    if not len(sent) in sentlens:
                        sentlens[len(sent)] = 0
                    sentlens[len(sent)] += 1
                    if len(sent) > 0:
                        for stat in sent:
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
