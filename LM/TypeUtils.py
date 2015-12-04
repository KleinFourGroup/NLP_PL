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
