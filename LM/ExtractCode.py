#!/usr/bin/env python2

import sys
import plyj.parser
import plyj.model as m
import copy

unr = []

def nstr(l):
    try:
        s = ' '.join(map(str, l))
    except:
        s = str(l)
    return s

def get_hnum(stat):
    hnum = 0
    try:
        for v in stat:
            if type(v) is str and v[0] == '@':
                hnum = max(hnum, int(v[1:]))
    except:
        pass
    return hnum + 1

def getTypeName(ty):
    if type(ty) is str:
        type_name = ty
    elif type(ty.name) is str:
        type_name = ty.name
    elif hasattr(ty.name, "value"):
        type_name = ty.name.value
    else:
        type_name = ty.name.name.value
    return type_name

def parse(stat):
    seq = []
    hnum = get_hnum(stat)
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
        if len(stat.body) > 0:
            seq.append(getCU("InstanceCreation", [], "", stat.body))
        line = ["new"]
        line.append(getTypeName(stat.type))
        line.append("@0")
        line.extend(stat.arguments)
        seq.append(line)
    elif type(stat) == m.Unary:
        if stat.sign == 'x++':
            line = ["add", stat.expression, stat.expression, '1']
        elif stat.sign == 'x--':
            line = ["sub", stat.expression, stat.expression, '1']
        else:
            line = stat
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
                if type(it.target) is str:
                    nstat.append(it.target + '.' + it.name)
                else:
                    nstat.append('@' + str(hnum) + '.' + it.name)
                    seq.append(('alloc', '@' + str(hnum), it.target))
                    hnum += 1
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
            if type(it.target) is str:
                nstat.append(it.target + '.' + it.name)
            else:
                nstat.append('@' + str(hnum) + '.' + it.name)
                seq.append(('alloc', '@' + str(hnum), it.target))
                hnum += 1
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
            if len(ex.body) > 0:
                seq.append(getCU("InstanceCreatione", [], "", ex.body))
            line = ["new"]
            line.append(getTypeName(ex.type))
            line.append(stat[1])
            line.extend(ex.arguments)
            seq.append(line)
        elif type(ex) == m.Unary:
            if ex.sign == '-':
                line = ["mul", stat[1], ex.expression, '-1']
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.ArrayAccess:
            line = ["arr", stat[1], ex.target, ex.index]
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
        elif type(ex) == m.Or:
            line = ["or", stat[1], ex.lhs, ex.rhs]
            seq.append(line)
        elif type(ex) == m.And:
            line = ["and", stat[1], ex.lhs, ex.rhs]
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
            if type(ex.target) is str:
                line = [stat[0], stat[1], ex.target + '.' + ex.name]
            else:
                line = [stat[0], stat[1], '@' + str(hnum) + '.' + ex.name]
                seq.append(('alloc', '@' + str(hnum), ex.target))
                hnum += 1
            seq.append(line)
        elif type(ex) == m.ArrayCreation:
            line = ["newarr", getTypeName(ex.type), stat[1], ex.dimensions[0]]
            seq.append(line)
        else:
            seq.append(stat)
            if type(ex) is not str:
                unr.append(stat)
    else:
        if type(stat) == type(CodeUnit()):
            stat.unpack()
        seq.append(stat)
        if not type(stat) == type(CodeUnit()):
            unr.append(stat)
    return seq

class CodeUnit:
    def __init__(self, name = "default"):
        self.v_list = []
        self.body = []
        self.name = name
        self.unpacked = False
    def addStat(self, stat):
        self.body.append(stat)
    def addVar(self, var):
        self.v_list.append(var)
    def unpack(self):
        if not self.unpacked:
            seq = None
            while not seq == self.body:
                seq = self.body
                self.body = []
                for stat in seq:
                    exp = parse(stat)
                    self.body.extend(exp)
            self.unpacked = True
    def matchPackages(self, imports):
        for v_dec in self.v_list:
            for im in imports:
                end = im.split('.')[-1]
                if v_dec[1] == end:
                    v_dec[1] = im
        for stat in self.body:
            try:
                if stat[0] == "new":
                    for im in imports:
                        end = im.split('.')[-1]
                        if stat[1] == end:
                            stat[1] = im
            except:
                pass
    def getStr(self, pre = ""):
        s = pre + self.name + "\n"
        for var in self.v_list:
            s += pre + "\t" + nstr(var) + "\n"
        s += pre + "\t-----\n"
        for stat in self.body:
            if type(stat) == type(self):
                s += stat.getStr(pre + "\t")
            else:
                s += pre + "\t" + nstr(stat) + "\n"
        return s

def extractDefVars(pre, stat):
    print pre + str(stat)
    v_list = []
    if type(stat) == m.MethodDeclaration:
        for param in stat.parameters:
            v_list.append(["def", getTypeName(param.type), param.variable.name])
    elif type(stat) == m.Catch:
        v_list.append(["def", stat.types[0].name.value, stat.variable.name])
    elif type(stat) == m.For and type(stat.init) == m.VariableDeclaration:
        for var_decl in stat.init.variable_declarators:
            v_list.append(["def", getTypeName(stat.init.type), var_decl.variable.name])
    return v_list
def getCU(name, v_list, pre, body):
    print pre + "getCU()"
    cu = CodeUnit(name)
    for var in v_list:
        cu.addVar(var)
    for stat in body:
        print pre + str(stat)
        if type(stat) == m.FieldDeclaration or type(stat) == m.VariableDeclaration:
            for var_decl in stat.variable_declarators:
                cu.addVar(["def", getTypeName(stat.type), var_decl.variable.name])
                if var_decl.initializer is not None:
                    cu.addStat(var_decl)
        elif type(stat) == m.ExpressionStatement:
            cu.addStat(stat)
        elif type(stat) == m.Return:
            cu.addStat(stat)
        else:
            ncu = None
            lvars = extractDefVars(pre + "//", stat)
            if type(stat) == m.While or type(stat) == m.DoWhile or type(stat) == m.For or type(stat) == m.MethodDeclaration or type(stat) == m.ClassDeclaration:
                ncu = getCU(type(stat).__name__, lvars, pre + '\t', stat.body)
            elif type(stat) == m.Block:
                ncu = getCU(type(stat).__name__, lvars, pre + '\t', stat.statements)
            elif type(stat) == m.ConstructorDeclaration:
                ncu = getCU(type(stat).__name__, lvars, pre + '\t', stat.block)
            else:
                ncu = CodeUnit(type(stat).__name__)
                for var in lvars:
                    ncu.addVar(var)
                if type(stat) == m.IfThenElse:
                    if stat.if_true is not None:
                        ncu.addStat(getCU("IfTrue", [], pre + '\t', [stat.if_true]))
                    else:
                        ncu.addStat(CodeUnit("IfTrue"))
                    if stat.if_false is not None:
                        ncu.addStat(getCU("IfFalse", [], pre + '\t', [stat.if_false]))
                    else:
                        ncu.addStat(CodeUnit("IfFalse"))
                elif type(stat) == m.Switch:
                    for c in stat.switch_cases:
                        ncu.addStat(getCU("SwitchCase", [], pre + '\t', c.body))
                elif type(stat) == m.Try:
                    ncu.addStat(getCU("TryBlock", [], pre + '\t', stat.block))
                    ncu.addStat(getCU("Catches", [], pre + '\t', stat.catches))
                    if stat._finally is not None:
                        ncu.addStat(getCU("Finally", [], pre + '\t', stat._finally))
                else:
                    pass
            cu.addStat(ncu)
    return cu

def ExtractCode(filename):
    p = plyj.parser.Parser()
    tree = p.parse_file(filename)
    imports = []
    for im in tree.import_declarations:
        imports.append(im.name.value)
    print('declared types:')
    for type_decl in tree.type_declarations:
        print(type_decl.name)
        if type_decl.extends is not None:
            print(' -> extending ' + type_decl.extends.name.value)
        if len(type_decl.implements) is not 0:
            print(' -> implementing ' + ', '.join([t.name.value for t in type_decl.implements]))
        cu = getCU(type(type_decl).__name__, [], "", type_decl.body)
        cu.unpack()
        cu.matchPackages(imports)
        print cu.getStr()
        for s in unr:
            print nstr(s)

def main():
    file_path = "../Java/ParseTests/"
    file_name = "FloatingSearchView.java"
    ExtractCode(file_path + file_name)

if __name__ == "__main__":
    main()
