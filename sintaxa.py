# coding=utf-8


from functools import reduce
import re




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

def get_lexis_modus(lst):
    pass


def match(ipos):
    """
    Ищем в списке syntax_modus правило, соответсвующее syntax_list[position:ipos]
    """
    return

def multiply(m):
    lexis_list.append(eval('{}("{}")'.format(m.lastgroup,m.group())))
    for x in syntax_modus:
        if x[0].__name__ == m.lastgroup:
            sret = x[2] if len(x) == 3 else '<%s>' % m.lastgroup
    return sret

def exec_modus(lexis):
    position = 0
    while position < len(lexis)-1: # проход по всем лексемам
        flag_modus_found = False
        for modus in lexis_modus: # проход по всенм модусам
            if position >= len(modus[0]) or not isinstance(lexis[0], modus[0][0]): # если модус явно не годится
                continue
            ipos = 1
            ilexis = lexis
            while ipos < len(modus[0])-1: # проход по шаблону модуса
                if not isinstance(ilexis[position+ipos], modus[0][position+ipos]): # если лексема [position+ipos] не явл. инстантом соотв. класса модуса, те не годится
                    lexeme = exec_modus(ilexis[position+ipos:])
                    if not lexeme: break
                    flag_modus_found = True
                    ilexis = ilexis[:position+ipos] + [lexeme] + ilexis[position+len(lexeme.childs):]
                    ipos += 1
            if ipos == len(modus[0])-1:
                lexis = ilexis
                position += 1
                break
        if not flag_modus_found:
            obj = modus[1]('node')
            obj.childs = lexis[position: position + ipos]
            return obj


                # if reduce(lambda a,b: a&b, [isinstance(lexis_list[pos], modus[0][pos]) for pos in range(len(modus)-1)]):


def parse_syntax(position):
    for modus in lexis_modus:
        if len(lexis_list[position:]) < len(modus[0]) or not isinstance(lexis_list[position], modus[0][0]):
            continue
        last_pos = 1
        while last_pos < len(modus[0]):
            if not isinstance(lexis_list[position+last_pos], modus[0][last_pos]):
                if not parse_syntax(position+last_pos-1):
                    break
            last_pos += 1
        if last_pos == len(modus[0]):
            obj = modus[1]('node')
            obj.childs = lexis_list[position: position+last_pos]
            tail = [obj] + lexis_list[position+last_pos:]
            while len(lexis_list)>position: lexis_list.pop()
            lexis_list.extend(tail)
            # parse_syntax(position)
            return True
    return False

lexis_modus = [([QuoteLeft,Expression,QuoteRight],Expression),
                ([Expression, OperInfix, Expression],Expression)
              ]
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
lexis_list = []

# exp_str = '(23+19)*dsds/asss1**8-8.9**8'
exp_str = '(17*dsds)/(asss1**8-8.9**8)'

reg = reduce(lambda a,b: a+'|'+b, [(r'(?P<%s>%s)' % (x[0].__name__,x[1])) for x in syntax_modus ])
result = re.sub(reg, multiply, exp_str)
print([(m.name,m.value) for m in lexis_list])

if not parse_syntax(0): print('Syntax error')
print('\n{}\n{}'.format(exp_str,''.join([m.value for m in lexis_list])))
