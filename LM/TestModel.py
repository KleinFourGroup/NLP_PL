import os
import copy
import plyj.parser
import ExtractCode as e
import ExtractSequences as seq
import TypeUtils as t
import LM
import sys


def main():
    par = plyj.parser.Parser()
    corpus_path = "../Java/Test/"
    blacklist = ["5a8beeae20366b5094d0db8148e0563", "3cd87ee90872cfcb72b3cb3b773d8efa"]
    sm = [["levels", 3], ["levels", 2], ["levels", 1], ["levels", "MEMM"], ["cfs", 3], ["cfs", 2], ["cfs", 1]]
    vp = [3, 2, 1]
    fill = ["max", "random"]
    fout = open("results.csv", 'w')
    for subdir, dirs, files in os.walk(corpus_path):
        for f in files:
            clear = True
            for h in blacklist:
                if h in f: clear = False
            if clear:
                p = os.path.join(subdir, f)
                cus = e.ExtractCode(par, p)
                for smod, mp in sm:
                    for v in vp:
                        for fi in fill:
                            for i, cu in cus:
                                cu = copy.deepcopy(cu)
                                ans = LM.getLL(cu, i, smod, mp, v, "pot", fi)
                                print smod, mp, v, "pot", fi
                                for call, ll in ans[:20]:
                                    print str(ll) + ': ' + e.nstr(call)
                                if f.endswith(".java"):
                                    unk = True
                                else:
                                    unk = False
                                fout.write(f[:-5] + ';' + smod + ';' + str(mp) + ';' + str(v) + ';' + fi + ';' + str(unk) + ';' + str(ll) + '\n')
    fout.close()
#    print len(vocab)
#    print len(set(sf))
#    print len(set(fields))
#    print sentlens

if __name__ == "__main__":
    main()
