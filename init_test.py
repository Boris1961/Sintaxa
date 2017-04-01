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
                                    Variable=dict(_attrs_=dict(syntax_modus=r'\w+(?:\d|\w)*', pseudo='<Var>')
                                                  ),
                                    Number=dict(_attrs_=dict(pseudo='<Num>'),
                                                IntNumber=dict(_attrs_=dict(syntax_modus=r'\d+(?![\.])', pseudo='<Int>')),
                                                FloatNumber=dict(_attrs_=dict(syntax_modus=r'\d+\.\d*', pseudo='<Flo>'))
                                                ),
                                    String=dict(_attrs_=dict(syntax_modus=r'(?:".*")|(?:\'.*\')', pseudo='<Str>'))
                                    )
                    )

# [((QuoteLeft, Expression, QuoteRight), Expression),
# ((Expression, OperInfix, Expression), Expression)]

LexisModus = {'(<Exp>)' : '<Exp>', '<Exp><Infix><Exp>' : '<Exp>'}

class Syn():
    def __init__(self, syntax_dict, lexis_moduses):
        class SyntaxClass(object):
            pseudo = 'SynCl'
            def __init__(self, value):
                self.name = self.__class__.__name__
                self.value = value
        setattr(self, 'SyntaxClass', SyntaxClass)
        self.syntax_moduses = []
        self.syntax_list = []
        Syn.recurse(self,syntax_dict,SyntaxClass)
        self.lexis_moduses = []
        reg = reduce(lambda a, b: '{}|{}'.format(a, b),
                 [(r'(?P<{}>{})'.format(x.__name__, re.sub(r'[^0-9a-zA-Z]', lambda m: '\{}'.format(m.group()), x.pseudo) )) for x in self.syntax_moduses])
        for (mkey,mval) in lexis_moduses.items():
            lkey = []
            lval = []
            re.sub(reg, lambda m: m.lastgroup if lkey.append(getattr(self,m.lastgroup)) else m.lastgroup, mkey)
            re.sub(reg, lambda m: m.lastgroup if lval.append(getattr(self,m.lastgroup)) else m.lastgroup, mval)
            self.lexis_moduses.append((tuple(lkey),lval[0]))
        pass # debug

    @staticmethod
    def recurse(obj,sdict,sclass):
        for (key,value) in sdict.items():
            attrs = value.pop('_attrs_', {})
            # if attrs.get('syntax_modus'):
            #    obj.syntax_moduses.append((key,attrs['syntax_modus'],attrs['pseudo']))
            setattr(obj, key, type(key, (sclass,), attrs))
            obj.syntax_moduses.append(getattr(obj,key))
            if value:
                Syn.recurse(obj, value, getattr(obj,key))

s = Syn(SyntaxDict,LexisModus)

# print(s.__dict__)
print([cl for cl in dir(s) if getattr(getattr(s,cl),'pseudo','')=='Int'])
# print(dir(s.Mult('*')))
pass
