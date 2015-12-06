import os
import plyj.parser
import ExtractCode as e
import ExtractSequences as seq
import TypeUtils as t
import sys


def main():
    par = plyj.parser.Parser()
    modes = ["cfs", "levels"]
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "levels"
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
    vocab_file = open(os.path.join(data_path, vocab_name), 'w')
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
                    sf2, fi, sents = seq.getSents(cu, i, mode)
                    sf.extend(sf2)
                    fields.extend(fi)
                    print str(ctr) + ": " + str(len(sents))
                    ctr += 1
                    for sent, vl in sents:
                        meth_file.write("<S2>\n")
                        meth_file.write("<S1>\n")
                        for stat, ctx in sent:
                            meth_file.write(e.nstr(t.getSig(stat, vl, False)) + ' # ' + e.nstr(ctx) + '\n')
                            s = t.getSig(stat, vl)
                            if not s[0] in vocab:
                                vocab[s[0]] = []
                            vocab[s[0]].append(s[1:])
                        meth_file.write('<END>\n')
                    vsents = seq.getVarSents(sents)
                    for vsent in vsents:
                        var_file.write("<S2>\n")
                        var_file.write("<S1>\n")
                        for stat, ctx in vsent:
                            var_file.write(e.nstr(stat) + '\n')
                        var_file.write('<END>\n')
            #break
        for s in vocab:
            vocab_file.write(s + '\n')
            for sig in t.resolveSigs(vocab[s]):
                vocab_file.write('\t' + e.nstr(sig) + '\n')
    meth_file.close()
    var_file.close()
    vocab_file.close()
#    print len(vocab)
#    print len(set(sf))
#    print len(set(fields))
#    print sentlens
        
if __name__ == "__main__":
    main()
