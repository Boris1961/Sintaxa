# coding=utf-8

from functools import reduce
from itertools import zip_longest
import re

SyntaxDict = dict(Operation=dict(_attrs_=dict(pseudo='<Opr>'),
                                   OperInfix=dict(_attrs_=dict(pseudo='<Infix>'),
                                                  Degree=dict(_attrs_=dict(syntax_modus=r'\*{2}', pseudo='**', prior=3)),
                                                  Div=dict(_attrs_=dict(syntax_modus=r'\/', pseudo='/', prior=2)),
                                                  Mult=dict(_attrs_=dict(syntax_modus=r'\*', pseudo='*', prior=2)),
                                                  Sub=dict(_attrs_=dict(syntax_modus=r'\-', pseudo='-', prior=1)),
                                                  Add=dict(_attrs_=dict(syntax_modus=r'\+', pseudo='+', prior=1))
                                                  )
                                   ),
                    QuoteRight=dict(_attrs_=dict(syntax_modus=r'\)', pseudo=')')
                                    ),
                    QuoteLeft=dict(_attrs_=dict(syntax_modus=r'\(', pseudo='(' )
                                   ),
                    Expression=dict(_attrs_=dict(pseudo='<Exp>'),
                                    Variable=dict(_attrs_=dict(syntax_modus=r'\w+(?:\d|\w)*', pseudo='Var')
                                                  ),
                                    Number=dict(_attrs_=dict(pseudo='<Num>'),
                                                IntNumber=dict(_attrs_=dict(syntax_modus=r'\d+(?![\.])', pseudo='Int')),
                                                FloatNumber=dict(_attrs_=dict(syntax_modus=r'\d+\.\d*', pseudo='Flo'))
                                                ),
                                    String=dict(_attrs_=dict(syntax_modus=r'(?:".*")|(?:\'.*\')', pseudo='Str'))
                                    )
                    )

# [((QuoteLeft, Expression, QuoteRight), Expression),
# ((Expression, OperInfix, Expression), Expression)]

LexisModus = {'(<Exp>)' : '<Exp>', '<Exp><Infix><Exp>' : '<Exp>'}

class Syn():
    def __init__(self, syntax_dict, lexis_moduses):
        class SyntaxClass(object):
            def __init__(self, value):
                self.name = self.__class__.__name__
                self.value = value
        setattr(self, 'SyntaxClass', SyntaxClass)
        self.syntax_moduses = []
        Syn.recurse(self,syntax_dict,SyntaxClass)
        self.lexis_moduses = []
        reg = reduce(lambda a, b: '{}|{}'.format(a, b),
                     [(r'(?P<{}>{})'.format(x[0],x[1])) for x in self.syntax_moduses])
        def multiply(m):
            src.append(m.group())
            for x in syntax_modus:
                if x[0].__name__ == m.lastgroup:
                    sret = x[2] if len(x) == 3 else m.lastgroup
            return sret
        for (mkey,mval) in lexis_moduses.items():
            src = []
            result = re.sub(reg, lambda m: src.append(m.group()), mkey)
            self.lexis_moduses.append([src,mval])
        pass

        """
        def multiply(m):
            self.lexis_modus.append(eval('{}("{}")'.format(m.lastgroup, m.group())))
            for x in syntax_modus:
                if x[0].__name__ == m.lastgroup:
                    sret = x[2] if len(x) == 3 else m.lastgroup
            return sret
        result = re.sub(reg, multiply, exp_str)
        """

    @staticmethod
    def recurse(obj,sdict,sclass):
        for (key,value) in sdict.items():
            try:
                attrs = value.pop('_attrs_')
                if 'syntax_modus' in attrs:
                    obj.syntax_moduses.append((key,attrs['syntax_modus'],attrs['pseudo']))
            except KeyError:
                attrs = {}
            setattr(obj, key, type(key, (sclass,), attrs))
            if value:
                Syn.recurse(obj, value, getattr(obj,key))
        return

s = Syn(SyntaxDict,LexisModus)
print(s)
m = s.Mult('*')
pass
