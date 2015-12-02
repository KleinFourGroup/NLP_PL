
import os
import zipfile
import hashlib
import shutil

import plyj.parser

zip_path = "../git_dl/"
out_path = "../Java/Corpus/"
def extract_files():
    proj = {}
    for subdir, dirs, files in os.walk(zip_path):
        for f in files:
            if f.endswith(".zip"):
                p = os.path.join(subdir, f)
                print p
                proj[p] = [[], []]
                z = zipfile.ZipFile(p, 'r')
                for name in z.namelist():
                    if name.endswith(".java"):
                        print '\t' + name
                        h = hashlib.md5(name).hexdigest()
                        ex_name = f[:-4] + '_' + name.split('/')[-1][:-5] + '_' + h + ".java"
                        print '\t' + ex_name
                        try:
                            jfile = z.open(name)
                            t = os.path.join(out_path, ex_name)
                            target = file(t, "wb")
                            with jfile, target:
                                shutil.copyfileobj(jfile, target)
                            proj[p][0].append(t)
                        except:
                            pass
    return proj

def check_files(proj):
    par = plyj.parser.Parser()
    ctr = 0
    for z in proj:
        bad_list = []
        noapi_list = []
        for p in proj[z][0]:
            print p
            tree = par.parse_file(p)
            if tree is None:
                bad_list.append(p)
            else:
                api = False
                for im in tree.import_declarations:
                    if im.name.value.split('.')[0] == "android":
                        api = True
                if not api:
                    noapi_list.append(p)
        for p in bad_list:
            os.remove(p)
        for p in noapi_list:
            os.remove(p)
        proj[z][1].append(len(proj[z][0]))
        proj[z][1].append(len(bad_list))
        proj[z][1].append(len(proj[z][0]) - len(bad_list) - len(noapi_list))
        ctr += len(proj[z][0]) - len(bad_list) - len(noapi_list)
    for z in proj:
        print '\t'.join(map(str, proj[z][1])) + "\t" + z
    print "Java files: " + str(ctr)

def main():
    p = extract_files()
    check_files(p)
    
if __name__ == "__main__":
    main()
