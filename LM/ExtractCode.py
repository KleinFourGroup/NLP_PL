#!/usr/bin/env python2

import sys
import plyj.parser
import plyj.model as m
import copy

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
            seq.append(getCU("InstanceDeclaration", [], "", stat.body))
        line = ["new"]
        line.append(getTypeName(stat.type))
        line.append("@0")
        line.extend(stat.arguments)
        seq.append(line)
    elif type(stat) == m.Unary:
        if stat.sign == 'x++':
            line = ["inc", stat.expression]
        elif stat.sign == 'x--':
            line = ["dec", stat.expression]
        elif stat.sign == '++x':
            line = ["add", stat.expression, stat.expression, 1]
        elif stat.sign == '--x':
            line = ["sub", stat.expression, stat.expression, 1]
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
            if type(it) is str or it is None:
                nstat.append(it)
            elif type(it) == int:
                nstat.append(str(int))
            elif type(it) == m.Name or type(it) == m.Literal:
                nstat.append(it.value)
            elif type(it) == m.ClassLiteral:
                nstat.append(getTypeName(it.type))
            elif type(it) == m.Type:
                nstat.append(getTypeName(it))
            elif type(it) == m.Cast:
                nstat.append(it.expression)
            elif type(it) == m.Unary and it.sign == '+':
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
        if type(it) is str or it is None:
            nstat.append(it)
        elif type(it) == int:
            nstat.append(str(int))
        elif type(it) == m.Name or type(it) == m.Literal:
            nstat.append(it.value)
        elif type(it) == m.ClassLiteral:
            nstat.append(getTypeName(it.type))
        elif type(it) == m.Type:
            nstat.append(getTypeName(it))
        elif type(it) == m.Cast:
            nstat.append(it.expression)
        elif type(it) == m.Unary and it.sign == '+':
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
                seq.append(getCU("InstanceDeclaration", [], "", ex.body))
            line = ["new"]
            line.append(getTypeName(ex.type))
            line.append(stat[1])
            line.extend(ex.arguments)
            seq.append(line)
        elif type(ex) == m.Unary:
            if ex.sign == '-':
                line = ["mul", stat[1], ex.expression, '-1']
            elif ex.sign == '!':
                line = ["neg", stat[1], ex.expression]
            elif ex.sign == '~':
                line = ["bitflip", stat[1], ex.expression]
            elif ex.sign == 'x++':
                line = ["inc", stat[1], ex.expression]
            elif ex.sign == 'x--':
                line = ["dec", stat[1], ex.expression]
            elif ex.sign == '++x':
                line = ["pinc", stat[1], ex.expression]
            elif ex.sign == '--x':
                line = ["pdec", stat[1], ex.expression]
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.Xor:
            line = ["xor", stat[1], ex.lhs, ex.rhs]
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
            elif ex.operator == '%':
                line = ["mod", stat[1], ex.lhs, ex.rhs]
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.Assignment:
            if ex.operator == '=':
                line = ["rset", stat[1], ex.lhs, ex.rhs]
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
        elif type(ex) == m.Shift:
            if ex.operator == '>>':
                line = ["arshr", stat[1], ex.lhs, ex.rhs]
            elif ex.operator == '>>>':
                line = ["logshr", stat[1], ex.lhs, ex.rhs]
            elif ex.operator == '<<':
                line = ["arshl", stat[1], ex.lhs, ex.rhs]
            else:
                line = stat
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
        elif type(ex) == m.ConditionalOr:
            if ex.operator == '||':
                line = ["cndor", stat[1], ex.lhs, ex.rhs]
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.ConditionalAnd:
            if ex.operator == '&&':
                line = ["cndand", stat[1], ex.lhs, ex.rhs]
            else:
                line = stat
            seq.append(line)
        elif type(ex) == m.Name or type(ex) == m.Literal:
            line = [stat[0], stat[1], ex.value]
            seq.append(line)
        elif type(ex) == m.ClassLiteral:
            line = [stat[0], stat[1], getTypeName(ex.type)]
            seq.append(line)
        elif type(ex) == m.Type:
            line = [stat[0], stat[1], getTypeName(ex)]
            seq.append(line)
        elif type(ex) == m.Cast:
            line = [stat[0], stat[1], ex.expression]
            seq.append(line)
        elif type(ex) == m.InstanceOf:
            line = ["instanceof", stat[1], ex.lhs, ex.rhs]
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
            line = ["newarr", getTypeName(ex.type), stat[1]]
            for dim in ex.dimensions:
                if dim is not None:
                    line.append(dim)
            seq.append(line)
        elif type(ex) == m.ArrayInitializer:
            line = ["newarr", stat[1]]
            line.extend(ex.elements)
            seq.append(line)
        else:
            seq.append(stat)
    else:
        if type(stat) == type(CodeUnit()):
            stat.unpack()
        seq.append(stat)
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
    def stripToFunctions(self):
        bod = []
        for stat in self.body:
            if type(stat) == type(self):
                stat.stripToFunctions()
                bod.append(stat)
            else:
                try:
                    if stat[0] == "call":
                        bod.append(stat)
                except:
                    pass
        self.body = bod
    def getUNR(self):
        unr = []
        for stat in self.body:
            if type(stat) == type(self):
                unr.extend(stat.getUNR())
            elif type(stat) == list or type(stat) == tuple:
                for t in stat:
                    if type(t) is not str:# and t is not None:
                        unr.append(stat)
                        break
            else:
                unr.append(stat)
        return unr
    def renameVars(self, pre = "", lvars = []):
        v_list = copy.deepcopy(lvars)
        for v in self.v_list:
            v[2] = v[2] + pre
        v_list.extend(copy.deepcopy(self.v_list))
        branch = 1
        for stat in self.body:
            if type(stat) == type(self):
                stat.renameVars(pre + '-' + str(branch), v_list)
                branch += 1
            elif type(stat) == list or type(stat) == tuple:
                for i in range(len(stat)):
                    if not (i == 1 and (stat[0] == "call" or stat[0] == "new")):
                        for v in v_list:
                            vl = v[2].split('-')[0]
                            sl = stat[i].split('.')
                            if vl == sl[0]:
                                if len(sl) > 1:
                                    stat[i] = v[2] + '.' + '.'.join(sl[1:])
                                else:
                                    stat[i] = v[2]
    def dumpVars(self):
        vl = copy.deepcopy(self.v_list)
        for stat in self.body:
            if type(stat) == type(self):
                vl.extend(stat.dumpVars())
        return vl
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
    #print pre + str(type(stat).__class__)
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
    #print pre + "getCU()"
    cu = CodeUnit(name)
    if v_list is not None:
        for var in v_list:
            cu.addVar(var)
    if body is not None:
        for stat in body:
            #print pre + str(stat)
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
                    if type(stat.body) == list:
                        ncu = getCU(type(stat).__name__, lvars, pre + '\t', stat.body)
                    elif stat.body is not None:
                        ncu = getCU(type(stat).__name__, lvars, pre + '\t', [stat.body])
                    else:
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
                        ncu.addStat(getCU("Finally", [], pre + '\t', stat._finally))
                    else:
                        pass
                cu.addStat(ncu)
    return cu

def ExtractCode(p, filename):
    tree = p.parse_file(filename)
    imports = []
    cus = []
    for im in tree.import_declarations:
        imports.append(im.name.value)
    print(filename)
    for type_decl in tree.type_declarations:
        if not type(type_decl) == m.EmptyDeclaration:
            print '\t' + str(type_decl.name)
            cu = getCU(type(type_decl).__name__, [], "", type_decl.body)
            cu.unpack()
            cus.append((imports, cu))
            #print cu.getStr()
    return cus
            
