# coding=utf-8

from functools import reduce
from itertools import zip_longest
import re

dict_Degree=dict(_attrs_=dict(syntax_modus=r'\*{2}', pseudo='**', prior=3))
dict_Div=dict(_attrs_=dict(syntax_modus=r'\/', pseudo='/', prior=2))
dict_Mult=dict(_attrs_=dict(syntax_modus=r'\*(?!\*)', pseudo='*', prior=2))
dict_Sub=dict(_attrs_=dict(syntax_modus=r'\-', pseudo='-', prior=1))
dict_Add=dict(_attrs_=dict(syntax_modus=r'\+', pseudo='+', prior=1))
dict_QuoteRight=dict(_attrs_=dict(syntax_modus=r'\)', pseudo=')'))
dict_QuoteLeft=dict(_attrs_=dict(syntax_modus=r'\(', pseudo='(' ))
dict_Variable=dict(_attrs_=dict(syntax_modus=r'[a-zA-Z]+(?:\d|\w)*', pseudo='<Var>'))
dict_IntNumber=dict(_attrs_=dict(syntax_modus=r'\d+(?![\.])', pseudo='<Int>'))
dict_FloatNumber=dict(_attrs_=dict(syntax_modus=r'\d+\.\d*', pseudo='<Flo>'))
dict_String=dict(_attrs_=dict(syntax_modus=r'(?:".*")|(?:\'.*\')', pseudo='<Str>'))

SyntaxDict = dict(Operation=dict(_attrs_=dict(pseudo='<Opr>'),
                                   OperInfix=dict(_attrs_=dict(pseudo='<Infix>'), Degree=dict_Degree, Div=dict_Div, Mult=dict_Mult, Sub=dict_Sub, Add=dict_Add)
                                 ),
                  QuoteRight=dict_QuoteRight,
                  QuoteLeft=dict_QuoteLeft,
                  SequanceInfix=dict(_attrs_=dict(pseudo='<SIn>')),
                  Expression=dict(_attrs_=dict(pseudo='<Exp>'),
                                  Variable=dict_Variable,
                                  String=dict_String,
                                  Number=dict(_attrs_=dict(pseudo='<Num>'),
                                              IntNumber=dict_IntNumber,
                                              FloatNumber=dict_FloatNumber),
                                  )
                  )


# [((QuoteLeft, Expression, QuoteRight), Expression),
# ((Expression, OperInfix, Expression), Expression)]


"""
LexisModus = {'(<Exp>)' : '<Exp>',
              '<Exp><Infix><Exp>' : '<Exp>'}

"""

LexisModus = {'(<SIn>)' : '<Exp>',
              '<Exp><Infix><Exp>' : '<SIn>',
              '<SIn><Infix><Exp>' : '<SIn>'}

class Syntaxa():
    def __init__(self, syntax_dict=SyntaxDict, lexis_moduses=LexisModus):
        class SyntaxClass(object):
            pseudo = 'SynCl'
            def __init__(self, value):
                self.name = self.__class__.__name__
                self.value = value
        setattr(self, 'SyntaxClass', SyntaxClass)
        self.syntax_list = []
        Syntaxa.recurse(self, syntax_dict, SyntaxClass)
        self.lexis_moduses = []
        self.lex_reg = reduce(lambda a, b: '{}|{}'.format(a, b),
                 [(r'(?P<{}>{})'.format(x.__name__, re.escape(x.pseudo) )) for x in self.syntax_list])
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
            setattr(obj, key, type(key, (sclass,), attrs))
            obj.syntax_list.append(getattr(obj,key))
            if value:
                Syntaxa.recurse(obj, value, getattr(obj, key))

    def exec_state(self,statement):
        state_list = []
        def repl(m):
            for cl in self.syntax_list:
                if cl.__name__ == m.lastgroup:
                    state_list.append(cl(m.group()))
                    return ''
        if re.sub(self.syn_reg, repl, statement):
            raise RuntimeError("Syntax error")

        def hand_lexis(modus,lexis):
            modus_target = modus[1](modus[1].__name__)
            if ''.join([cl.pseudo for cl in modus[0]]) != '<SIn><Infix><Exp>':
                modus_target.childs = lexis[:len(modus[0])]
            else:
                modus_target.childs = lexis[0].childs + [lexis[1], lexis[2]]
            lexis = [modus_target] + lexis[len(modus[0]):]
            return lexis

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
                        # modus_target = modus[1](modus[1].__name__)
                        # modus_target.childs = lexis[:len(modus[0])]
                        # lexis = [modus_target] + lexis[len(modus[0]):]
                        lexis = hand_lexis(modus,lexis)
                        modus_found = True
                        if depth:
                            return lexis
                        else:
                            break
                    for i in range(ipos, 0, -1):
                        lst = exec_modus(lexis[i:], depth=depth + 1) # РЕКУРСИЯ
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
        self.syntax_tree = exec_modus(state_list)
        return self.syntax_tree
