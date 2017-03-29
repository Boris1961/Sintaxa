# coding=utf-8


from functools import reduce
from itertools import zip_longest
import re


class Class_EOL(object):
    pass

class SintaxObject(object):
    def __init__(self, value):
        self.name = self.__class__.__name__
        self.value = value

class Expression(SintaxObject):
    pass

class Variable(Expression):
    pass

class Number(Expression):
    pass

class IntNumber(Number):
    pass

class FloatNumber(Number):
    pass

class String(Number):
    pass

class QuoteLeft(SintaxObject):
    pass

class QuoteRight(SintaxObject):
    pass

class Operation(SintaxObject):
    pass

class OperInfix(Operation):
    pass

class Degree(OperInfix):
    pass

class Div(OperInfix):
    pass

class Mult(OperInfix):
    pass

class Sub(OperInfix):
    pass

class Add(OperInfix):
    pass

class Lexema(object):
    def __init__(self, match):
        # self.match = match
        self.name = match.lastgroup
        self.value = match.string[match.regs[0][0]: match.regs[0][1]]
    def __repr__(self):
        return '<{}:"{}">'.format(self.name,self.value)


def symbol_class(sym):
    pass

def modus_match(modus,lexis):
    if len(lexis) < len(modus[0]):
        return None
    else:
        lst = [isinstance(*t) for t in zip_longest(lexis, modus[0])]
        if lst.count(False) == 0:
            return len(lst)-1
        else:
            return lst.index(False)

def multiply(m):
    lexis_list.append(eval('{}("{}")'.format(m.lastgroup,m.group())))
    for x in syntax_modus:
        if x[0].__name__ == m.lastgroup:
            sret = x[2] if len(x) == 3 else '<%s>' % m.lastgroup
    return sret

def get_lexis_modus(lst):
    ml = [m for m in lexis_modus if len(m[0]) <= len(lst)]
    mlist = [ (m, [isinstance(*n) for n in zip_longest(lst, m[0])] ) for m in ml ]
    print(mlist)
    return mlist

lexis_modus = [((QuoteLeft,Expression,QuoteRight), Expression),
                ((Expression, OperInfix, Expression), Expression)]
syntax_modus = [
    (String, r'(?:".*")|(?:\'.*\')'),
    (IntNumber, r'\d+(?![\.])'),
    (FloatNumber, r'\d+\.\d*'),
    (Variable, r'\w+(?:\d|\w)*'),
    (QuoteLeft, r'\(', '('),
    (QuoteRight, r'\)', ')'),
    (Degree, r'\*{2}', '^'),
    (Mult, r'\*', '*'),
    (Div, r'\/', '/'),
    (Sub, r'\-', '/'),
    (Add, r'\+', '+' )
]

def modus_match(modus,lexis):
    if len(lexis) < len(modus[0]):
        return 0
    else:
        lst = [isinstance(*t) for t in zip_longest(lexis[:len(modus[0])], modus[0], fillvalue = object)]
        if lst.count(False) == 0:
            return -1
        else:
            return lst.index(False)

def exec_modus(lexis, depth=0):
    print("\nВход: \n", lexis)
    while len(lexis) > 1: # проход по всем лексемам
        second_break = False
        modus_found = False
        for modus in lexis_modus: # проход по всенм модусам
            ipos = modus_match(modus,lexis)
            if ipos == 0:   # модус явно не годится
                continue    # давай следующий
            if ipos == -1:  # модус совпал полностью
                modus_target = modus[1]('Expression')
                modus_target.childs = lexis[:len(modus[0])]
                lexis = [modus_target] + lexis[len(modus[0]):]
                modus_found = True
                if depth:
                    return lexis
                else:
                    break
                return lexis
            for i in range(ipos,0,-1):
                lst = exec_modus(lexis[i:], depth=depth+1)
                if lst:
                    lexis = lexis[:i] + lst
                    if len(lexis) == 1:  # lexis отсканирован весь
                        return lexis
                    modus_found = True
                    second_break = True
                    break
            if second_break:
                break
        if not modus_found:
            return None
    return lexis

lexis_list = []

# exp_str = '(23+19)*dsds/asss1**8-8.9**8'
# exp_str = 'A*(B+C)'
# exp_str = '(A-X)*(B+C)'
# exp_str = 'A*(B+C)'

exp_str = '((A-X)*12)**(B/(C-7))'

reg = reduce(lambda a,b: a+'|'+b, [(r'(?P<%s>%s)' % (x[0].__name__,x[1])) for x in syntax_modus ])
result = re.sub(reg, multiply, exp_str)
print([(m.name,m.value) for m in lexis_list])

lexis_result = exec_modus(lexis_list)
# if not parse_syntax(0): print('Syntax error')
print('\n{}\n{}'.format(exp_str,''.join([m.value for m in lexis_result])))
