#!/usr/bin/env python2

import sys
import plyj.parser
import plyj.model as m
import copy

p = plyj.parser.Parser()
tree = p.parse_file("C:\\Users\\Matthew\\Desktop\\t.java")

imports = []
for im in tree.import_declarations:
    imports.append(im.name.value)
#cs_list = []
hnum = 1

def nstr(l):
    try:
        s = ' '.join(map(str, l))
    except:
        s = str(l)
    return s

def extractDefVars(pre, stat):
    print pre + str(stat)
    v_list = []
    if type(stat) == m.MethodDeclaration:
        for param in stat.parameters:
            if type(param.type) is str:
                type_name = param.type
            else:
                type_name = param.type.name.value
            v_list.append(["def", type_name, param.variable.name])
    elif type(stat) == m.For and type(stat.init) == m.VariableDeclaration:
        for var_decl in stat.init.variable_declarators:
            if type(stat.init.type) is str:
                type_name = stat.init.type
            else:
                type_name = stat.init.type.name.value
            v_list.append(["def", type_name, var_decl.variable.name])
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

def getCS(pre, body, top = "Top" = []):
    print pre + "getCS()"
    #print pre + str(type(v_list))
    cs_list = []
    cs = []
    for stat in body:
        print pre + str(stat)
        if type(stat) == m.FieldDeclaration or type(stat) == m.VariableDeclaration:
            print pre + str(stat)
            for var_decl in stat.variable_declarators:
                if type(stat.type) is str:
                    type_name = stat.type
                else:
                    type_name = stat.type.name.value
                v_list.append(["def", type_name, var_decl.variable.name])
                if var_decl.initializer is not None:
                    cs.append(var_decl)
                    print pre + "extending cs"
        elif type(stat) == m.ExpressionStatement:
            cs.append(stat)
            print pre + "extending cs"
        elif type(stat) == m.Return:
            cs.append(stat)
            print pre + "extending cs"
        else:
            if len(cs) > 0:
                cs_list.append([copy.deepcopy(v_list), copy.deepcopy(cs)])
                cs = []
            lvars = extractDefVars(pre + "//", stat)
            for newbod in extractBody(stat):
                getCS(pre + '\t', newbod, type(stat).__name__, lvars)
    if len(cs) > 0:
        cs_list.append([copy.deepcopy(v_list), copy.deepcopy(cs)])
        cs = []
    return (top, cs_list)

def parse(stat):
    seq = []
    global hnum
    if type(stat) == m.ExpressionStatement:
        seq.append(stat.expression)
    elif type(stat) == m.MethodInvocation:
        line = ["call"]
        line.append(stat.name)
        line.append("@0")
        if stat.target == None:
            line.append("this")
        else:
            line.append(stat.target)
        line.extend(stat.arguments)
        seq.append(line)
    elif type(stat) == m.Assignment:
        line = ["set", stat.lhs, stat.rhs]
        seq.append(line)
    elif type(stat) == m.VariableDeclarator:
        line = ["set", stat.variable.name, stat.initializer]
        seq.append(line)
    elif type(stat) == m.InstanceCreation:
        line = ["new"]
        line.append(stat.type.name.value)
        line.append("@0")
        line.extend(stat.arguments)
        seq.append(line)
    elif type(stat) == m.Return:
        line = ["ret"]
        if stat.result is not None:
            line.append(stat.result)
        seq.append(line)
    elif type(stat) == list and not stat[0] == "set":
        nstat = []
        for it in stat:
            if type(it) is str:
                nstat.append(it)
            elif type(it) == m.Name or type(it) == m.Literal:
                nstat.append(it.value)
            elif type(it) == m.Cast:
                nstat.append(it.expression)
            elif type(it) == m.FieldAccess:
                nstat.append(it.target + it.name)
            else:
                nstat.append('@' + str(hnum))
                seq.append(('alloc', '@' + str(hnum), it))
                hnum += 1
        seq.append(nstat)
    elif type(stat) == list and stat[0] == "set" and type(stat[1]) is not str:
        nstat = ["set"]
        it = stat[1]
        if type(it) is str:
            nstat.append(it)
        elif type(it) == m.Name or type(it) == m.Literal:
            nstat.append(it.value)
        elif type(it) == m.Cast:
            nstat.append(it.expression)
        elif type(it) == m.FieldAccess:
            nstat.append(it.target + it.name)
        else:
            nstat.append('@' + str(hnum))
            seq.append(('alloc', '@' + str(hnum), it))
            hnum += 1
        nstat.append(stat[2])
        seq.append(nstat)
    elif type(stat) == tuple or type(stat) == list and stat[0] == 'set' and type(stat[1]) is str:
        ex = stat[2]
        if type(ex) == m.MethodInvocation:
            line = ["call"]
            line.append(ex.name)
            line.append(stat[1])
            if ex.target is None:
                line.append("this")
            else:
                line.append(ex.target)
            line.extend(ex.arguments)
            seq.append(line)
        elif type(ex) == m.InstanceCreation:
            line = ["new"]
            line.append(ex.type.name.value)
            line.append(stat[1])
            line.extend(ex.arguments)
            seq.append(line)
        elif type(ex) == m.Unary:
            if ex.sign == '-':
                line = ["mul", stat[1], ex.expression, '-1']
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.Additive:
            if ex.operator == '+':
                line = ["add", stat[1], ex.lhs, ex.rhs]
            elif ex.operator == '-':
                line = ["sub", stat[1], ex.lhs, ex.rhs]
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.Multiplicative:
            if ex.operator == '*':
                line = ["mul", stat[1], ex.lhs, ex.rhs]
            elif ex.operator == '/':
                line = ["div", stat[1], ex.lhs, ex.rhs]
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.Conditional:
            line = ["cond", stat[1], ex.predicate, ex.if_true, ex.if_false]
            seq.append(line)
        elif type(ex) == m.Equality:
            line = ["eq", stat[1], ex.lhs, ex.rhs]
            seq.append(line)
        elif type(ex) == m.Relational:
            if ex.operator == '>':
                line = ["gr", stat[1], ex.lhs, ex.rhs]
            elif ex.operator == '>=':
                line = ["geq", stat[1], ex.lhs, ex.rhs]
            elif ex.operator == '<':
                line = ["less", stat[1], ex.lhs, ex.rhs]
            elif ex.operator == '<=':
                line = ["leq", stat[1], ex.lhs, ex.rhs]
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.Name or type(ex) == m.Literal:
            line = [stat[0], stat[1], ex.value]
            seq.append(line)
        elif type(ex) == m.Cast:
            line = [stat[0], stat[1], ex.expression]
            seq.append(line)
        elif type(ex) == m.FieldAccess:
            line = [stat[0], stat[1], ex.target + ex.name]
            seq.append(line)
        else:
            seq.append(stat)
    else:
        seq.append(stat)
    return seq

def parseSeq(seq):
    oseq = None
    nseq = seq
    while not oseq == nseq:
        oseq = nseq
        nseq = []
        for stat in oseq:
            exp = parse(stat)
            nseq.extend(exp)
    global hnum
    hnum = 1
    return nseq

def matchPackages(v_list, seq):
    for v_dec in v_list:
        for im in imports:
            end = im.split('.')[-1]
            if v_dec[1] == end:
                v_dec[1] = im
    for stat in seq:
        try:
            if stat[0] == "new":
                for im in imports:
                    end = im.split('.')[-1]
                    if stat[1] == end:
                        stat[1] = im
        except:
            pass

print('declared types:')
for type_decl in tree.type_declarations:
    print(type_decl.name)
    if type_decl.extends is not None:
        print(' -> extending ' + type_decl.extends.name.value)
    if len(type_decl.implements) is not 0:
        print(' -> implementing ' + ', '.join([t.name.value for t in type_decl.implements]))
    getCS([], "", type_decl.body)

    for cs in cs_list:
        v_list = cs[0]
        cs[1] = parseSeq(cs[1])
        seq = cs[1]
        matchPackages(v_list, seq)
        print
        for var in v_list:
            print '\t' + nstr(var)
        print "\t-----"
        for stat in seq:
            print '\t' + nstr(stat)


##
##    print
##    print('fields:')
##    for field_decl in [decl for decl in type_decl.body if type(decl) is m.FieldDeclaration]:
##        for var_decl in field_decl.variable_declarators:
##            if type(field_decl.type) is str:
##                type_name = field_decl.type
##            else:
##                type_name = field_decl.type.name.value
##            print('    ' + type_name + ' ' + var_decl.variable.name)
##
##    print
##    print('methods:')
##    for method_decl in [decl for decl in type_decl.body if type(decl) is m.MethodDeclaration]:
##        param_strings = []
##        for param in method_decl.parameters:
##            if type(param.type) is str:
##                param_strings.append(param.type + ' ' + param.variable.name)
##            else:
##                param_strings.append(param.type.name.value + ' ' + param.variable.name)
##        print('    ' + method_decl.name + '(' + ', '.join(param_strings) + ')')
##
##        if method_decl.body is not None:
##            for statement in method_decl.body:
##                print('        ' + str(type(statement)))
##                # note that this misses variables in inner blocks such as for loops
##                # see symbols_visitor.py for a better way of handling this
##                if type(statement) is m.VariableDeclaration:
##                    for var_decl in statement.variable_declarators:
##                        if type(statement.type) is str:
##                            type_name = statement.type
##                        else:
##                            type_name = statement.type.name.value
##                        print('        ' + type_name + ' ' + var_decl.variable.name)
