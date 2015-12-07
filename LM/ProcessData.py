import os
import plyj.parser
import ExtractCode as e
import ExtractSequences as seq
import TypeUtils as t
import sys
import pickle
import numpy as np
from sklearn import linear_model

def build_meth_vocab(vocab_file, meth_file):
    vocab_file.seek(0)
    meth_file.seek(0)
    vocab = {}
    last_func = ""
    for line in vocab_file:
        if not line[0] == '\t':
            last_func = line.split()[0]
            vocab[last_func] = {}
        else:
            n = len(line.split())
            vocab[last_func][n] = {}
            for i in range(n):
                vocab[last_func][n][i-1] = {}
    for line in meth_file:
        parts = line.split('#')
        if len(parts) > 1:
            call = t.splitLit(parts[0])
            func = call[0]
            args = call[1:]
            print call
            n = len(args)
            for i in range(n):
                if not args[i] in vocab[func][n][i-1]:
                    vocab[func][n][i-1][args[i]] = 0
                vocab[func][n][i-1][args[i]] += 1
    return vocab

def getReducedLines(meth_file):
    meth_file.seek(0)
    sents = []
    sent = []
    for line in meth_file:
        if not line[0] == '<':
            parts = line.split('#')
            inf = tuple(parts[1].split())
            call = t.splitLit(parts[0])
            func = call[0]
            n = len(call) - 1
            stat = (func, n)
            sent.append((stat, inf))
        else:
            sent.append((line[:-1], ()))
        if line == "<END>\n":
            sents.append(sent)
            sent = []
    return sents

def getVarLines(var_file):
    var_file.seek(0)
    sents = []
    sent = []
    for line in var_file:
        if not line[0] == '<':
            parts = line.split('|')
            inf = tuple(map(int, parts[1].split()))
            call = t.splitLit(parts[0])
            func = call[0]
            n = len(call) - 1
            stat = (func, n, inf)
            sent.append(stat)
        else:
            sent.append(line[:-1])
        if line == "<END>\n":
            sents.append(sent)
            sent = []
    return sents
            


def getNTuples(sents, words2index, mode):
    ngrams = {}
    N1p = {}
    ch = {}
    for s in sents:
        for i in range(2, len(s)):
            if mode == "meth":
                stat = s[i][0]
                stat1 = s[i-1][0]
                stat2 = s[i-2][0]
            elif mode == "var":
                stat = s[i]
                stat1 = s[i-1]
                stat2 = s[i-2]
            tri = (words2index[stat2], words2index[stat1], words2index[stat])
            if not tri in ngrams:
                ngrams[tri] = 0
            ngrams[tri] += 1
        for i in range(1, len(s)):
            if mode == "meth":
                stat = s[i][0]
                stat1 = s[i-1][0]
            elif mode == "var":
                stat = s[i]
                stat1 = s[i-1]
            bi  = (words2index[stat1], words2index[stat])
            if not bi in ngrams:
                ngrams[bi] = 0
            ngrams[bi] += 1
        for i in range(0, len(s)):
            if mode == "meth":
                stat = s[i][0]
            elif mode == "var":
                stat = s[i]
            uni = tuple([words2index[stat]])
            if not uni in ngrams:
                ngrams[uni] = 0
            ngrams[uni] += 1
    for ng in ngrams:
        if len(ng):
            newg = ng[:-1]
            if not newg in N1p:
                N1p[newg] = 0
            N1p[newg] += 1
            if not newg in ch:
                ch[newg] = 0
            ch[newg] += ngrams[ng]
    return ngrams, N1p, ch

def main():
    #par = plyj.parser.Parser()
    modes = ["cfs", "levels"]
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "levels"
    if mode not in modes:
        mode = "levels"
    data_path = "../Data/Raw"
    new_path = "../Data/Revised"
    ####
    meth_name = "method_sentences_" + mode + ".txt"
    var_name = "variable_sentences_" + mode + ".txt"
    vocab_name = "vocab_" + mode + ".txt"
    counts_name = "counts_" + mode + ".txt"
    memm_name = "memm_" + mode + ".txt"
    ####
    meth_file = open(os.path.join(data_path, meth_name), 'r')
    var_file = open(os.path.join(data_path, var_name), 'r')
    vocab_file = open(os.path.join(data_path, vocab_name), 'r')
    nvocab_file = open(os.path.join(new_path, vocab_name), 'wb')
    count_file = open(os.path.join(new_path, counts_name), 'wb')
    memm_file = open(os.path.join(new_path, memm_name), 'wb')
    ####
    meth_sigs = build_meth_vocab(vocab_file, meth_file)
    meth_vocab_list = {}
    ctr = 0
    for f in meth_sigs:
        print f
        for n in meth_sigs[f]:
            if not (f,n) in meth_vocab_list:
                meth_vocab_list[(f, n)] = ctr
                ctr += 1
            print '\t' + str(n) + " | ",
            for i in range(n):
                print str(i-1) + ":( ",
                for ty in meth_sigs[f][n][i-1]:
                    print ty + '/' + str(meth_sigs[f][n][i-1][ty]) + ' ', 
                print ") ",
            print
    meth_vocab_list["<END>"] = ctr
    meth_vocab_list["<S1>"] = ctr+1
    meth_vocab_list["<S2>"] = ctr+2
    pot_var_vocab_list = {}
    ctr = 0
    for k in meth_vocab_list:
        if type(k) is not str:
            f, n = k
            for s in t.powerset([i-1 for i in range(n)]):
                pot_var_vocab_list[(f, n, tuple(s))] = ctr
                ctr += 1
    pot_var_vocab_list["<END>"] = ctr
    pot_var_vocab_list["<S1>"] = ctr+1
    pot_var_vocab_list["<S2>"] = ctr+2
    vsents = getVarLines(var_file)
    act_var_vocab_list = {}
    ctr = 0
    for s in vsents:
        for stat in s:
            if not stat in act_var_vocab_list:
                act_var_vocab_list[stat] = ctr
                ctr += 1
    pickle.dump((meth_sigs, meth_vocab_list, pot_var_vocab_list, act_var_vocab_list), nvocab_file)
    nvocab_file.close()
    print len(meth_vocab_list)
    print len(pot_var_vocab_list)
    print len(act_var_vocab_list)
    meth_sents = getReducedLines(meth_file)
    meth_sents = seq.getFeatures(meth_sents)
    X = [meth_sents[i][j][1] for i in range(len(meth_sents)) for j in range(len(meth_sents[i]))]
    print len(X)
    y = [meth_vocab_list[meth_sents[i][j][0]] for i in range(len(meth_sents)) for j in range(len(meth_sents[i]))]
    meth_ngram, meth_N1p, meth_ch = getNTuples(meth_sents, meth_vocab_list, "meth")
    print "N-GRAMS"
    pot_var_ngram, pot_var_N1p, pot_var_ch = getNTuples(vsents, pot_var_vocab_list, "var")
    print "N-GRAMS"
    act_var_ngram, act_var_N1p, act_var_ch = getNTuples(vsents, act_var_vocab_list, "var")
    print "N-GRAMS"
    pickle.dump(((meth_ngram, meth_N1p, meth_ch), (pot_var_ngram, pot_var_N1p, pot_var_ch), (act_var_ngram, act_var_N1p, act_var_ch)), count_file)
    count_file.close()
    MEMM = linear_model.LogisticRegression()
    if not mode == "cfs":
        MEMM.fit(X,y)
    pickle.dump(MEMM, memm_file)
    meth_file.close()
    var_file.close()
    memm_file.close()
        
if __name__ == "__main__":
    main()
