import os
import plyj.parser
import ExtractCode as e
import ExtractSequences as seq
import TypeUtils as t
import sys


def getSig(stat, v_list, no_const = True):
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
                            if no_const:
                                sig.append(var[1])
                            else:
                                sig.append("<type>" + var[1])
                            b = False
                    if b:
                        if ':' in stat[i]:
                            sig.append("FIELD")
                        else:
                            if no_const:
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
                                else:
                                    sig.append("UNK")
                            else:
                                sig.append(stat[i])
    except:
        pass
    return sig

def getVarSents(sent, v_list):
    sents = []
    for var in v_list:
        sen = []
        for stat in sent:
            app = []
            for i in range(len(stat)):
                if stat[i] == var[2]:
                    app.append(i - 3)
            if len(app) > 0:
                s = getSig(stat, v_list)
                s.append('|')
                s.extend(app)
                sen.append(s)
        if len(sen) > 0:
            sents.append(sen)
    return sents

def main():
    par = plyj.parser.Parser()
    modes = ["cfs", "levels"]
    mode = sys.argv[1]
    if mode not in modes:
        mode = "levels"
    corpus_path = "../Java/Corpus/"
    data_path = "../Data/Raw"
    ####
    meth_name = "method_sentences_" + mode + ".txt"
    var_name = "variable_sentences_" + mode + ".txt"
    vocab_name = "vocab_" + mode + ".txt"
    ####
    meth_file = open(os.path.join(data_path, meth_name), 'w')
    var_file = open(os.path.join(data_path, var_name), 'w')
    ####
    vocab = {}
    sf = []
    fields = []
    ctr = 1
    blacklist = ["5a8beeae20366b5094d0db8148e0563", "3cd87ee90872cfcb72b3cb3b773d8efa"]
    for subdir, dirs, files in os.walk(corpus_path):
        for f in files:
            clear = True
            for h in blacklist:
                if h in f: clear = False
            if f.endswith(".java") and clear:
                p = os.path.join(subdir, f)
                cus = e.ExtractCode(par, p)
                for i, cu in cus:
                    sf2, fi, sents = seq.getSents(cu, i, "levels")
                    sf.extend(sf2)
                    fields.extend(fi)
                    print str(ctr) + ": " + str(len(sents))
                    ctr += 1
                    for sent, vl in sents:
                        if len(sent) > 0:
                            for stat in sent:
                                meth_file.write(e.nstr(getSig(stat, vl, False)) + '\n')
                            meth_file.write('\n')
                            vsents = getVarSents(sent, vl)
                            for vsent in vsents:
                                if len(vsent) > 0:
                                    for stat in vsent:
                                        var_file.write(e.nstr(stat) + '\n')
                                    var_file.write('\n')
                            #    s = getSig(stat, vl)
                            #    if not s[0] in vocab:
                            #        vocab[s[0]] = []
                            #    vocab[s[0]].append(s[1:])
            #break
    meth_file.close()
    var_file.close()
#    for s in vocab:
#        print s
#        for sig in resolveSigs(vocab[s]):
#            print '\t' + e.nstr(sig)
#    print len(vocab)
#    print len(set(sf))
#    print len(set(fields))
#    print sentlens
        
if __name__ == "__main__":
    main()
