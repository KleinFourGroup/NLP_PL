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
                                else:
                                    sig.append("UNK")
                            else:
                                sig.append(stat[i])
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

def splitLit(s):
    ret = []
    inStr = False
    inChar = False
    prevChar = None
    curpart = ""
    for ch in s:
        if ch == ' ':
            if inChar or inStr:
                curpart += ch
            else:
                if len(curpart) > 0:
                    ret.append(curpart)
                    curpart = ""
        elif ch == '\\':
            curpart += ch
            ch = "DONT END STR"
        elif ch == '"':
            curpart += ch
            if not (prevChar == '\\' or inChar):
                inStr = not inStr
        elif ch == '\'':
            curpart += ch
            if not (prevChar == '\\' or inStr):
                inChar = not inChar
        elif ch in '\r\n\t':
            if len(curpart) > 0:
                ret.append(curpart)
                curpart = ""
        else:
            curpart += ch
        prevChar = ch
    if len(curpart) > 0:
        ret.append(curpart)
    return ret

def powerset(seq):
    if len(seq) <= 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]]+item
            yield item
            
