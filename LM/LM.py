import math
import pickle
import os
import random
import ExtractSequences as seq
import operator

def ngramProb(ngram, words2index, ngrams, N1p, ch):
    if len(ngram) == 0:
        return 1.0 / (len(words2index) - 2)
    else:
        pre = tuple([words2index[w] for w in ngram[:-1]])
        nxt = tuple([words2index[w] for w in ngram[1:]])
        cur = tuple([words2index[w] for w in ngram])
        #print ngram, pre, nxt, cur
        if cur in ngrams:
            mle = ngrams[cur] * 1.0/ ch[pre]
        else:
            mle = 0.0
        #print ngrams[cur], ch[pre], mle
        if pre in ch:
            l1 = ch[pre] * 1.0 / (ch[pre] + N1p[pre])
            l2 = N1p[pre] * 1.0 / (ch[pre] + N1p[pre])
        else:
            l1 = 0
            l2 = 1
        return l1*mle + l2*ngramProb(ngram[1:], words2index, ngrams, N1p, ch)


def seqProb(seq, dat, mode = "ngram"):
    LL = 0
    if mode == "ngram":
        n, words2index, ngrams, N1p, ch = dat
        for i in range(2, len(seq)):
            ng = [seq[j] for j in range(i - n+1, i + 1)]
            for i in range(len(ng)):
                if type(ng[i]) is not str:
                    ng[i] = ng[i][0]
            #print ng
            p = ngramProb(ng, words2index, ngrams, N1p, ch)
            #print ng, p
            LL += math.log(p)
    elif mode == "MEMM":
        memm = dat
        for stat in seq:
            if type(stat) == tuple:
                fcall, tags = stat
                P = memm.predict_log_proba(tags)[0]
                for i in range(len(memm.classes_)):
                    if fcall == memm.classes_[i]:
                        LL += P[i]
    return LL

def seqProb(seq, dat, mode = "ngram"):
    LL = 0
    if mode == "ngram":
        n, words2index, ngrams, N1p, ch = dat
        for i in range(2, len(seq)):
            ng = [seq[j] for j in range(i - n+1, i + 1)]
            for i in range(len(ng)):
                if type(ng[i]) is not str:
                    ng[i] = ng[i][0]
            #print ng
            p = ngramProb(ng, words2index, ngrams, N1p, ch)
            #print ng, p
            LL += math.log(p)
    elif mode == "MEMM":
        memm, words2index = dat
        for stat in seq:
            if type(stat) == tuple:
                fcall, tags = stat
                P = memm.predict_log_proba(tags)[0]
                for i in range(len(memm.classes_)):
                    if words2index[fcall] == memm.classes_[i]:
                        LL += P[i]
    return LL

def varSeqProb(seq, dat):
    LL = 0
    n, words2index, ngrams, N1p, ch = dat
    for i in range(2, len(seq)):
        ng = [seq[j] for j in range(i - n+1, i + 1)]
        #print ng
        p = ngramProb(ng, words2index, ngrams, N1p, ch)
        #print ng, p
        LL += math.log(p)
    return LL

def pickType(dic, ty):
    n = 0
    m = 0
    for k in dic:
        if "<type>" in k or k[6:] in ty:
            m += 1
    for k in dic:
        if m == 0:
            if not '<type>' in k:
                n += dic[k]
        else:
            if (not "<type>" in k and not (k == 'UNK' or k == 'EXP' or k == 'FIELD')) or (k[6:] in ty):
                n += dic[k]
    if n == 0:
        return None
    ind =  random.randint(1, n)
    n = 0
    k = None
    for k in dic:
        if not "<type>" in k or k[6:] in ty:
            n += dic[k]
        if n >= k:
            break
    return k

def var_guesses(word, cu, meth_sigs, n):
    potsig = meth_sigs[word[0]][word[1]]
    vl = cu.getUNKVL()
    ty = set([t for s, t, v in vl])
    sigl = {}
    for i in range(n):
        sig = {}
        for p in potsig:
            sig[p] = pickType(potsig[p], ty)
            if sig[p] is None:
                return {}
            if '<type>' in sig[p]:
                opt = [var for s, t, var in vl if t == sig[p][6:]]
                try:
                    sig[p] = random.choice(opt)
                except:
                    return {}
        line = ["???" for i in range(2 + len(potsig))]
        line[0] = "call"
        line[1] = word[0]
        for p in sig:
            line[p+3] = sig[p]
        sigl[tuple(line)] = 0
    return sigl

def getLL(cu, i, seq_mode = "levels", meth_prob = "MEMM", var_prob = 3, var_voc = "pot", fill = "max", num_guess = 20):
    data_path = "../Data/Revised"
    vocab_name = "vocab_" + seq_mode + ".txt"
    counts_name = "counts_" + seq_mode + ".txt"
    memm_name = "memm_" + seq_mode + ".txt"
    vocab_file = open(os.path.join(data_path, vocab_name), 'rb')
    vocab_data = pickle.load(vocab_file)
    meth_sigs, meth_vocab_list, pot_var_vocab_list, act_var_vocab_list = vocab_data
    print "Read vocab data"
    vocab_file.close()
    if var_voc == "act":
        var_vocab_list = act_var_vocab_list
        pot_var_vocab_list = None
    else:
        var_vocab_list = pot_var_vocab_list
        act_var_vocab_list = None
    count_file = open(os.path.join(data_path, counts_name), 'rb')
    count_data = pickle.load(count_file)
    meth_count, pot_count, act_count = count_data
    print "Read count data"
    count_file.close()
    if var_voc == "act":
        var_count = act_count
        pot_count = None
    else:
        var_count = pot_count
        act_count = None
    if type(meth_prob) == int:
        meth_dat = [meth_prob, meth_vocab_list]
        meth_dat.extend(meth_count)
        prob_mode = "ngram"
    else:
        meth_count = None
        memm_file = open(os.path.join(data_path, memm_name), 'rb')
        meth_dat = pickle.load(memm_file)
        meth_dat = [meth_dat,  meth_vocab_list]
        print "Read MEMM"
        prob_mode = "MEMM"
        memm_file.close()
    imp, fi, sents = seq.getSents(cu, i, seq_mode)
    word_ll = {}
    for word in meth_vocab_list:
        #print word
        if type(word) is not str:
            ll = 0
            ctr = 0
            for sent, vl in sents:
                newsent = []
                for stat, ctx in sent:
                    if stat == "UNK":
                        newsent.append((word, ctx))
                    else:
                        f = stat[1]
                        n = len(stat) - 2
                        newsent.append(((f, n), ctx))
                newsent = seq.getFeatures([newsent])[0]
                newsent.insert(0, "<S1>")
                newsent.insert(0, "<S2>")
                newsent.append("<END>")
                if type(meth_prob) == int:
                    ctr += len(newsent) - 2
                else:
                    ctr += len(newsent) - 3
                ll += seqProb(newsent, meth_dat, prob_mode)
            ll /= ctr
            word_ll[word] = ll
    word_ll = sorted(word_ll.items(), key=operator.itemgetter(1), reverse = True)
    top_guess = {}
    i = 0
    while i < len(word_ll) and len(top_guess) < 20:
        if fill == "max":
            w = word_ll[i][0]
        else:
            w = random.choice(word_ll)[0]
        i += 1
        var_guess = var_guesses(w, cu, meth_sigs, num_guess)
        if len(var_guess) > 0:
            var_dat = [var_prob, var_vocab_list]
            var_dat.extend(var_count)
            for call in var_guess:
                ll = 0
                ctr = 0
                vsents = []
                for sent, vl in sents:
                    newsent = []
                    for stat, ctx in sent:
                        if stat == "UNK":
                            newsent.append((call, ctx))
                        else:
                            newsent.append((stat, ctx))
                    vsents.append([newsent, vl])
                vsents = seq.getVarSents2(vsents)
                for sen in vsents:
                    sen.insert(0, "<S1>")
                    sen.insert(0, "<S2>")
                    sen.append("<END>")
                    ctr += len(sen) - 2
                    #print sen
                    ll += varSeqProb(sen, var_dat)
                top_guess[call] = ll / ctr
    top_guess  = sorted(top_guess.items(), key=operator.itemgetter(1), reverse = True)
    return top_guess
