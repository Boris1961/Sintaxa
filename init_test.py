# coding=utf-8

from functools import reduce
from itertools import zip_longest
import re

SyntaxDict = dict(Operation=dict(_attrs_=dict(pseudo='<Opr>'),
                                   OperInfix=dict(_attrs_=dict(pseudo='<Infix>'),
                                                  Degree=dict(_attrs_=dict(syntax_modus=r'\*{2}', pseudo='**', prior=3)),
                                                  Div=dict(_attrs_=dict(syntax_modus=r'\/', pseudo='/', prior=2)),
                                                  Mult=dict(_attrs_=dict(syntax_modus=r'\*(?!\*)', pseudo='*', prior=2)),
                                                  Sub=dict(_attrs_=dict(syntax_modus=r'\-', pseudo='-', prior=1)),
                                                  Add=dict(_attrs_=dict(syntax_modus=r'\+', pseudo='+', prior=1))
                                                  )
                                   ),
                    QuoteRight=dict(_attrs_=dict(syntax_modus=r'\)', pseudo=')')
                                    ),
                    QuoteLeft=dict(_attrs_=dict(syntax_modus=r'\(', pseudo='(' )
                                   ),
                    Expression=dict(_attrs_=dict(pseudo='<Exp>'),
                                    Variable=dict(_attrs_=dict(syntax_modus=r'[a-zA-Z]+(?:\d|\w)*', pseudo='<Var>')
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
        self.syntax_list = []
        Syn.recurse(self,syntax_dict,SyntaxClass)
        self.lexis_moduses = []
        self.lex_reg = reduce(lambda a, b: '{}|{}'.format(a, b),
                 [(r'(?P<{}>{})'.format(x.__name__, re.sub(r'[^0-9a-zA-Z]', lambda m: '\{}'.format(m.group()), x.pseudo) )) for x in self.syntax_list])
        self.syn_reg = reduce(lambda a,b: '{}|{}'.format(a,b), [(r'(?P<{}>{})'.format(x.__name__,x.syntax_modus)) for x in self.syntax_list if hasattr(x,'syntax_modus')])
        for (mkey,mval) in lexis_moduses.items():
            lkey = []
            lval = []
            re.sub(self.lex_reg, lambda m: m.lastgroup if lkey.append(getattr(self,m.lastgroup)) else m.lastgroup, mkey)
            re.sub(self.lex_reg, lambda m: m.lastgroup if lval.append(getattr(self,m.lastgroup)) else m.lastgroup, mval)
            self.lexis_moduses.append((tuple(lkey),lval[0]))

        pass # debug

    @staticmethod
    def recurse(obj,sdict,sclass):
        for (key,value) in sdict.items():
            attrs = value.pop('_attrs_', {})
            # if attrs.get('syntax_modus'):
            #    obj.syntax_moduses.append((key,attrs['syntax_modus'],attrs['pseudo']))
            setattr(obj, key, type(key, (sclass,), attrs))
            obj.syntax_list.append(getattr(obj,key))
            if value:
                Syn.recurse(obj, value, getattr(obj,key))

    def exec_state(self,statement):
        state_list = []
        def repl(m):
            for cl in self.syntax_list:
                if cl.__name__ == m.lastgroup:
                    state_list.append(cl(m.group()))
                    return ''
        if re.sub(self.syn_reg, repl, statement):
            raise "Syntax error"

        def exec_modus(lexis, depth=0):
            while len(lexis) > 1:  # проход по всем лексемам
                second_break = False
                modus_found = False
                for modus in self.lexis_moduses:  # проход по всенм модусам
                    if len(lexis) < len(modus[0]):  # модус явно не годится
                        continue  # давай следующий
                    try:
                        ipos = [isinstance(*t) for t in
                                zip_longest(lexis[:len(modus[0])], modus[0], fillvalue=object)].index(False)
                    except ValueError:  # модус совпал полностью
                        modus_target = modus[1](modus[1].__name__)
                        modus_target.childs = lexis[:len(modus[0])]
                        lexis = [modus_target] + lexis[len(modus[0]):]
                        modus_found = True
                        if depth:
                            return lexis
                        else:
                            break
                    for i in range(ipos, 0, -1):
                        lst = exec_modus(lexis[i:], depth=depth + 1)
                        if lst.__class__.__name__ == 'list':
                            lexis = lexis[:i] + lst
                            if len(lexis) == 1:  # lexis отсканирован весь
                                return lexis
                            modus_found = True
                            second_break = True
                            break
                    if second_break:
                        break
                if not modus_found:
                    # return None
                    return (lexis, modus)
            return lexis

        lexis_result = exec_modus(state_list)

        pass # debug



s = Syn(SyntaxDict,LexisModus)
exp_str = '((A-X)*12)**(B/(C-7))'
e = s.exec_state(exp_str)

# print(s.__dict__)
print([cl for cl in dir(s) if getattr(getattr(s,cl),'pseudo','')=='Int'])
# print(dir(s.Mult('*')))
pass

