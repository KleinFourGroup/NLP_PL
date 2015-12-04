
import os
import plyj.parser
import ExtractCode as e


def main():
    par = plyj.parser.Parser()
    file_path = "../Java/Corpus/"
    unr = []
    for subdir, dirs, files in os.walk(file_path):
        for f in files:
            if f.endswith(".java"):
                p = os.path.join(subdir, f)
                cus = e.ExtractCode(par, p)
                for i, cu in cus:
                    unr.extend(cu.getUNR())
                    cu.renameVars()
                    print cu.getStr()
                    for v in cu.dumpVars():
                        print e.nstr(v)
                    break
            break
    for s in unr:
        print e.nstr(s)
        
if __name__ == "__main__":
    main()
