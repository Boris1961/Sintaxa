# coding=utf-8

from functools import reduce
import re

# Operations:
dict_Degree = dict(_attrs_=dict(syntax_modus=r'\*{2}', pseudo='**', prior=3))
dict_Div = dict(_attrs_=dict(syntax_modus=r'\/', pseudo='/', prior=2))
dict_Mult = dict(_attrs_=dict(syntax_modus=r'\*(?!\*)', pseudo='*', prior=2))
dict_Sub = dict(_attrs_=dict(syntax_modus=r'\-', pseudo='-', prior=1))
dict_Add = dict(_attrs_=dict(syntax_modus=r'\+', pseudo='+', prior=1))

dict_Call = dict(_attrs_=dict(syntax_modus=r'\#', pseudo='#', prior=4))

# SpecSymbols:
dict_QuoteLeft = dict(_attrs_=dict(syntax_modus=r'\(', pseudo='(', prior=5))
dict_QuoteRight = dict(_attrs_=dict(syntax_modus=r'\)', pseudo=')', prior=0))

# Expressions:
dict_Variable = dict(_attrs_=dict(syntax_modus=r'[a-zA-Z]+(?:\d|\w)*', pseudo='<Var>'))
dict_IntNumber = dict(_attrs_=dict(syntax_modus=r'\d+(?![\.])', pseudo='<Int>'))
dict_FloatNumber = dict(_attrs_=dict(syntax_modus=r'\d+\.\d*', pseudo='<Flo>'))
dict_String = dict(_attrs_=dict(syntax_modus=r'(?:".*")|(?:\'.*\')', pseudo='<Str>'))

SyntaxDict = dict(Operation=dict(_attrs_=dict(pseudo='<Opr>'),
                                 OperInfix=dict(_attrs_=dict(pseudo='<Infix>'), Degree=dict_Degree, Div=dict_Div,
                                                Mult=dict_Mult, Sub=dict_Sub, Add=dict_Add, Call=dict_Call
                                                )
                                 ),
                  SpecSymbol=dict(_attrs_=dict(pseudo='<SPEC>'),
                                  QuoteRight=dict_QuoteRight,
                                  QuoteLeft=dict_QuoteLeft),
                  Value=dict(_attrs_=dict(pseudo='<Val>'),
                             Variable=dict_Variable,
                             String=dict_String,
                             Number=dict(_attrs_=dict(pseudo='<Num>'),
                                         IntNumber=dict_IntNumber,
                                         FloatNumber=dict_FloatNumber),
                             Capsule=dict(_attrs_=dict(pseudo='<Caps>')),
                             Sequance=dict(_attrs_=dict(pseudo='<SEQ>'))
                             )
                  )

LexisModus = [dict(prototype='<Val><Infix><Val>', sub='<Val>', prior=1),
              # тут prior = индекс приоритетного элемента в прототипе
              dict(prototype='(<Val>)', sub='<Val>', repl_only=True),
              dict(prototype='<Var>(', sub='<Var>#(')
              ]


class Modus():
    def __init__(self, obj, kwargs):
        for key in kwargs:
            if key in ('prototype', 'sub'):
                setattr(self, key, tuple([getattr(obj, m.lastgroup) for m in re.finditer(obj.lex_reg, kwargs[key])]))
            else:
                setattr(self, key, kwargs[key])
    def __getattr__(self, item):
        return None

class SyntaxaError(Exception):
    def __init__(self, lexis):
        self.lexis = lexis

class Syntaxa():

    def __init__(self, syntax_dict=SyntaxDict, lexis_moduses=LexisModus):
        class SyntaxClass(object):
            pseudo = 'SynCl'

            def __init__(self, value):
                self.name = self.__class__.__name__
                self.value = value

        setattr(self, 'SyntaxClass', SyntaxClass)
        self.syntax_list = []
        self.syntax_tree = []
        Syntaxa.recurse(self, syntax_dict, SyntaxClass)
        self.lex_reg = reduce(lambda a, b: '{}|{}'.format(a, b),
                              [(r'(?P<{}>{})'.format(x.__name__, re.escape(x.pseudo))) for x in self.syntax_list])
        self.syn_reg = reduce(lambda a, b: '{}|{}'.format(a, b),
                              [(r'(?P<{}>{})'.format(x.__name__, x.syntax_modus)) for x in self.syntax_list if
                               hasattr(x, 'syntax_modus')])
        self.lexis_moduses = [Modus(self, modus) for modus in lexis_moduses]

    @staticmethod
    def recurse(obj, sdict, sclass):
        for (key, value) in sdict.items():
            attrs = value.pop('_attrs_', {})
            setattr(obj, key, type(key, (sclass,), attrs))
            obj.syntax_list.append(getattr(obj, key))
            if value:
                Syntaxa.recurse(obj, value, getattr(obj, key))

    def exec_state(self, expression):
        def repl(m):
            for cl in self.syntax_list:
                if cl.__name__ == m.lastgroup:
                    expression_list.append(cl(m.group()))
                    return ''

        def proc_prior(lexis, modus):
            ipos = len(modus.prototype)
            if not modus.prior or len(lexis) == ipos:
                return False
            lexis_prior = lexis[ipos].prior
            proto_prior = lexis[modus.prior].prior
            if lexis_prior and proto_prior and lexis_prior > proto_prior:
                return True
            else:
                return False

        def match_modus(modus, lexis):
            return ([isinstance(*t) for t in zip(lexis[:len(modus.prototype)], modus.prototype)] + [False]).index(False)

        def match_pattern(pattern, lexis):
            return reduce(lambda x, y: x & y, [type(t[0]) == t[1] for t in zip(lexis, pattern)])

        def parse_modus(obj, lexis, depth=0, pattern=None):

            while len(lexis) > 1:  # проход по всем лексемам

                # print(''.join(['<' + m.name + '>' for m in lexis]), ' : ', ''.join([m.value for m in lexis]), ' dep = ', depth)
                self.last_pos = len(''.join([m.value for m in lexis]))

                match = sorted([(modus, match_modus(modus, lexis)) for modus in obj.lexis_moduses],
                               key=lambda x: x[1], reverse=True)
                match_full = [item for item in match if item[0].prototype.__len__() == item[1]]

                if match_full.__len__() > 1:
                    raise SyntaxaError("Unexpect modus")  # найдены более одного совпавшего прототипа

                elif match_full.__len__() == 1:  # найден ровно один совпавший прототип
                    modus, ipos = match_full[0]
                    if proc_prior(lexis, modus):  # след.элемент более приоритетный?
                        lexis = lexis[:ipos - 1] + parse_modus(obj, lexis[ipos - 1:], depth=depth + 1,
                                                               pattern=modus.prototype[ipos - 1:])  # РЕКУРСИЯ: обработка более высокого приоритета
                    if modus.sub.__len__() > 1 or modus.repl_only:
                        src = lexis[:ipos]
                        dst = []
                        for item in list(modus.sub):
                            try:
                                s = src.pop(list(map(type, src)).index(item))
                            except ValueError:
                                s = item(item.pseudo)
                            dst.append(s)
                        lexis = dst + lexis[ipos:]
                        if depth and match_pattern(pattern, lexis):
                            return lexis
                        else:
                            continue

                    else:
                        sub = modus.sub[0]
                        target = sub(sub.__name__)
                        target.childs = lexis[:ipos]
                        target.childs = [item for item in lexis[:ipos] if not isinstance(item, obj.SpecSymbol)]
                        lexis = [target] + lexis[ipos:]

                    if depth and match_pattern(pattern, lexis):
                        return lexis
                    else:
                        continue

                else:  # найдено только частичное совпадение
                    match = [item for item in match if item[1] > 0]
                    if len(match) == 0:
                        return []
                    modus_found = False
                    for item in match:
                        modus, ipos = item
                        for i in range(ipos, 0, -1):
                            lst = parse_modus(obj, lexis[i:], depth=depth + 1, pattern=modus.prototype[i:])
                            if not lst:
                                continue
                            lexis = lexis[:i] + lst
                            if depth and match_pattern(pattern, lexis):
                                return lexis
                            else:
                                modus_found = True
                                break
                        if modus_found:
                            break
                    if not modus_found:
                        return []

            return lexis

        expression_list = []
        if re.sub(self.syn_reg, repl, expression):
            raise RuntimeError("Syntax error")
        self.syntax_tree = parse_modus(self, expression_list, pattern=(self.Value,))
        if not self.syntax_tree:
            print('Syntax error:\n', expression, '\n', ' '*(len(expression)-self.last_pos) + '^' + ' '*self.last_pos)
            exit()
        #    print(''.join([m.value for m in expression_list])) # debug
        return self.syntax_tree
