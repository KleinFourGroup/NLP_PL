imports = []
for im in tree.import_declarations:
    imports.append(im.name.value)
cs_list = []

def extractDefVars(pre, stat):
    print pre + str(stat)
    v_list = []
    if type(stat) == m.MethodDeclaration:
        for param in stat.parameters:
            if type(param.type) is str:
                type_name = param.type
            else:
                type_name = param.type.name.value
            v_list.append([type_name, param.variable.name])
    elif type(stat) == m.For and type(stat.init) == m.VariableDeclaration:
        for var_decl in stat.init.variable_declarators:
            if type(stat.init.type) is str:
                type_name = stat.init.type
            else:
                type_name = stat.init.type.name.value
            v_list.append([type_name, var_decl.variable.name])
    return v_list

def extractBody(stat):
    if type(stat) == m.While or type(stat) == m.DoWhile or type(stat) == m.For or type(stat) == m.MethodDeclaration or type(stat) == m.ClassDeclaration:
        return [stat.body]
    elif type(stat) == m.Block:
        return [stat.statements]
    elif type(stat) == m.IfThenElse:
        bods = []
        if stat.if_true is not None:
            bods.append([stat.if_true])
        if stat.if_false is not None:
            bods.append([stat.if_false])
        return bods
    elif type(stat) == m.Switch:
        bods = []
        for c in stat.switch_cases:
            bods.append(c.body)
        return bods
    else:
        return []

def getCS(v_list, pre, body):
    print pre + "getCS()"
    #print pre + str(type(v_list))
    cs = []
    for stat in body:
        print pre + str(type(stat))
        if type(stat) == m.FieldDeclaration or type(stat) == m.VariableDeclaration:
            for var_decl in stat.variable_declarators:
                if type(stat.type) is str:
                    type_name = stat.type
                else:
                    type_name = stat.type.name.value
                v_list.append([type_name, var_decl.variable.name])
        elif type(stat) == m.ExpressionStatement:
            cs.append(stat)
        elif type(stat) == m.Return and not type(stat.result) == m.Name and not type(stat.result) == m.Literal and stat.result is not None:
            cs.append(stat.result)
        else:
            if len(cs) > 0:
                cs_list.append([copy.deepcopy(v_list), copy.deepcopy(cs)])
                cs = []
            lvars = extractDefVars(pre + "//", stat)
            for newbod in extractBody(stat):
                vl = copy.deepcopy(v_list)
                vl.extend(lvars)
                getCS(vl, pre + '\t', newbod)
    if len(cs) > 0:
        cs_list.append([copy.deepcopy(v_list), copy.deepcopy(cs)])
        cs = []
