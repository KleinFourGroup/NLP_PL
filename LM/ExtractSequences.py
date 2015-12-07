import copy
import TypeUtils as t

def getSeqs(cu, mode = "levels", lvars = [], inf = []):
    v_list = copy.deepcopy(lvars)
    v_list.extend(copy.deepcopy(cu.v_list))
    inf = copy.deepcopy(inf)
    inf.append(cu.name)
    sent = []
    sents = []
    if mode == "levels":
        l = len(cu.body)
        for i in range(l):
            stat = cu.body[i]
            ctx = []
            if i == 0 or (type(cu.body[i-1]) == type(cu)):
                ctx.append("begin")
            if i == l-1 or (type(cu.body[i+1]) == type(cu)):
                ctx.append("end")
            ctx.extend(inf)
            if not type(stat) == type(cu):
                sent.append((stat, ctx))
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

def getCFS(cu, inf = []):
    inf = copy.deepcopy(inf)
    inf.append(cu.name)
    sents = [[]]
    dsents = []
    if cu.name == "IfThenElse" or cu.name == "Switch" or cu.name == "Catches":
        sents = []
        for c in cu.body:
            s, sd = getCFS(c, inf)
            sents.extend(s)
            dsents.extend(sd)
            #print pre + str(len(sents))# + ": " + '-'.join(map(str, map(len, sents)))
        if len(sents) == 0:
            sents = [[]]
    else:
        l = len(cu.body)
        for i in range(l):
            stat = cu.body[i]
            ctx = []
            if i == 0 or (type(cu.body[i-1]) == type(cu)):
                ctx.append("begin")
            if i == l-1 or (type(cu.body[i+1]) == type(cu)):
                ctx.append("end")
            ctx.extend(inf)
            if not type(stat) == type(cu):
                sents = prod(sents, [[(stat, ctx)]])
            else:
                s, sd = getCFS(stat, inf)
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
    #cu = copy.deepcopy(cu)
    if mode == "cfs":
        sents, dsents = getCFS(cu)
        sents.extend(dsents)
        for i in range(len(sents)):
            sents[i] = (copy.deepcopy(sents[i]), copy.deepcopy(cu.dumpVars()))
        return sents
    else:
        sents = getSeqs(cu, mode)
        return copy.deepcopy(sents)

def getSents(cu, i, mode):
        cu.stripToFunctions()
        cu.renameVars()
        importables = cu.matchPackages(i)
        cu.resolveFunctions(i)
        cu.stripToAPI()
        fields = cu.resolveFields(i)
        sents = getSentences(cu, mode)
        return importables, fields, sents

def getVarSents(sents):
    vsents = []
    for sent, v_list in sents:
        for var in v_list:
            sen = []
            for stat, ctx in sent:
                app = []
                for i in range(len(stat)):
                    if stat[i] == var[2]:
                        app.append(i - 3)
                if len(app) > 0:
                    s = t.getSig(stat, v_list)
                    s.append('|')
                    s.extend(app)
                    sen.append((s, ctx))
            vsents.append(sen)
    return vsents

def getVarSents2(sents):
    vsents = []
    for sent, v_list in sents:
        for var in v_list:
            sen = []
            for stat, ctx in sent:
                app = []
                for i in range(len(stat)):
                    if stat[i] == var[2]:
                        app.append(i - 3)
                if len(app) > 0:
                    s = t.getSig(stat, v_list)
                    f = s[0]
                    n = len(s) - 1
                    sen.append((f, n, tuple(app)))
            vsents.append(sen)
    return vsents

def getFeatures(meth_sents):
    sents = []
    for s in meth_sents:
        sent = []
        for i in range(len(s)):
            stat, inf = s[i]
            if i > 0:
                pre = sent[i-1]
            else:
                pre = None
            if type(stat) is str:
                sent.append((stat, [0 for i in range(8)]))
            else:
                feat = []
                if "begin" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                if "end" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                if "For" in inf or "While" in inf or "DoWhile" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                if "IfThenElse" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                if "Switch" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                if "TryBlock" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                if "Catches" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                if "Finally" in inf:
                    feat.append(1)
                else:
                    feat.append(0)
                sent.append((stat, feat))
        sents.append(sent)
    return sents
