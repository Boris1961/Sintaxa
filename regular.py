# coding=utf-8
from functools import reduce
import re


exp_str = '(23+19)*dsds/asss1**8-8.9**8'

lexis_list = []

sintax_modus = [
    ('str', r'(?:".*")|(?:\'.*\')'),
    ('int', r'\d+(?![\.])'),
    ('flt', r'\d+\.\d*'),
    ('var', r'\w+(?:\d|\w)*'),
    ('qul', r'\(', '('),
    ('qur', r'\)', ')'),
    ('dgr', r'\*{2}', '^'),
    ('mul', r'\*', '*'),
    ('div', r'\/', '/'),
    ('sub', r'\-', '/'),
    ('add', r'\+', '+' )
]

reg = reduce(lambda a,b: a+'|'+b, [(r'(?P<%s>%s)' % (x[0],x[1])) for x in sintax_modus ])

# exp_str = '(23+19)*dsds**8-89'

class Lexema(object):
    def __init__(self, match):
        # self.match = match
        self.lclass = m.lastgroup
        self.lvalue = m.string[m.regs[0][0]: m.regs[0][1]]
        lexis_list.append(self)

def multiply(m):
    # образец = m.string[m.regs[0][0]: m.regs[0][1]]
    lexis_list.append(Lexema(m))
    for x in sintax_modus:
        if x[0] == m.lastgroup:
            sret = x[2] if len(x) == 3 else '<%s>' % m.lastgroup
    return sret
    # return '<%s>' % m.lastgroup

print(reg)


result = re.sub(reg, multiply, exp_str)
print(result)
print(lexis_list)
