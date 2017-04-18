# coding=utf-8

from functools import reduce
from itertools import takewhile
import re
import inspect

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
dict_Comma = dict(_attrs_=dict(syntax_modus=r'\,', pseudo=',', prior=0))

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
                                  QuoteLeft=dict_QuoteLeft,
                                  Comma=dict_Comma),
                  Value=dict(_attrs_=dict(pseudo='<Val>'),
                             Variable=dict_Variable,
                             String=dict_String,
                             Number=dict(_attrs_=dict(pseudo='<Num>'),
                                         IntNumber=dict_IntNumber,
                                         FloatNumber=dict_FloatNumber),
                             Capsule=dict(_attrs_=dict(pseudo='<Cap>')),
                             Sequance=dict(_attrs_=dict(pseudo='<Seq>')),
                             Tuple=dict(_attrs_=dict(pseudo='<Tup>'))
                             )
                  )

LexisModus1 = [dict(prototype='<Val><Infix><Val>', sub='<Val>', prior=1),
              dict(prototype='(<Val>)', sub='<Val>', repl_only=True),
              dict(prototype='<Var>(', sub='<Var>#(')
              ]

# тут prior = индекс приоритетного элемента в прототипе
LexisModus = [dict(prototype='<Val><Infix><Val>', sub='<Val>', prior=1),
              dict(prototype='(<Val>)', sub='<Val>', repl_only=True),
              dict(prototype='<Var>(', sub='<Var>#('),
              # dict(prototype='<Var>(<Val>)', sub='<Var>#<Val>'),
              # dict(prototype='(<Seq>)', sub='<Tup>'),
              # dict(prototype='<Var><Tup>', sub='<Var>#<Tup>'),
              dict(prototype='<Val>,<Val>', sub='<Seq>'),
              dict(prototype='<Seq>,<Val>', sub='<Seq>', repl_only=True)
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
        def recurse(sdict, sclass):
            for (key, value) in sdict.items():
                attrs = value.pop('_attrs_', {})
                setattr(self, key, type(key, (sclass,), attrs))
                self.syntax_list.append(getattr(self, key))
                if value:
                    recurse(value, getattr(self, key))

        setattr(self, 'SyntaxClass', SyntaxClass)
        self.syntax_list = []
        self.syntax_tree = []
        syntax_dict['SpecSymbol']['EOL'] = dict(_attrs_=dict(pseudo='<EOL>', prior=-1))
        lexis_moduses.append(dict(prototype='<Val><EOL>', sub='<Val>'))
        recurse(syntax_dict, SyntaxClass)
        self.lex_reg = reduce(lambda a,b: '{}|{}'.format(a,b),
                              [(r'(?P<{}>{})'.format(x.__name__, re.escape(x.pseudo))) for x in self.syntax_list])
        self.syn_reg = reduce(lambda a, b: '{}|{}'.format(a,b),
                              [(r'(?P<{}>{})'.format(x.__name__, x.syntax_modus)) for x in self.syntax_list if
                               hasattr(x, 'syntax_modus')])
        self.lexis_moduses = list(map(lambda x: Modus(self,x), lexis_moduses))

    def compile_exp(self, expression):

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
            # функция сравнивает прототип модуса с lexis, и возвращает длину совпавшего интервала (от начала списка)
            return len(list(takewhile(lambda x: isinstance(*x), zip(lexis, modus.prototype))))


        def match_pattern(pattern, lexis):
            return reduce(lambda x, y: x & y, map(lambda x: type(x[0]) == x[1], zip(lexis, pattern)))

        def get_depth():
            """ Возвращает глубину рекурсии парсинга
            """
            return list(filter(lambda x: x[3] == 'parse_modus', inspect.stack())).__len__() - 1

        def DECOR_DEBUG(f):
            def WRAP(*args, **kwargs):
                depth = get_depth()+1
                print('{tab} ({depth}) S: {new_lexis} P:{pattern}'.format(tab='\t'*depth, depth=depth,
                                                                          new_lexis=''.join([m.value for m in args[0]]),
                                                                          pattern=[m.__name__ for m in kwargs['pattern']]))
                ret = f(*args, **kwargs)
                print('{tab} ({depth}) F: {ret}'.format(tab='\t' * depth, depth=depth, ret=''.join([m.value for m in ret])))
                return ret
            return WRAP

        @DECOR_DEBUG
        def parse_modus(lexis, pattern=None):
            """
            Парсинг списка лексем lexis на предмет соответствия к-либо правилу из списка правил,
            преобразование lexis по найденному правилу и возврат результата
            :param lexis: список лексем-экземляров класса SyntaxClass, который будем парсить
            :param pattern: искомый список классов для lexis : isinstance(lexis(i),pattern(i)==True)

            :return: преобразованный список lexis по подходящему правилу modus
            """

            depth = get_depth()

            while len(lexis) > 1:  # проход по списку лексем

                self.last_pos = len(''.join([m.value for m in lexis])) # отрицательный индекс в исходной строке expression первого символа lexis (для обработки ошибки)
                match = list(zip(self.lexis_moduses, map(lambda x: match_modus(x, lexis), self.lexis_moduses)))
                match = sorted(list(filter(lambda x: x[1] > 0, match)),
                               key=lambda x: x[1], reverse=True) # список ненулевых совпадений с прототипом
                if not match:
                    return []

                match_full = list(filter(lambda x: x[0].prototype.__len__() == x[1], match))  # список match полностью совпавших протопитов

                #if match_full.__len__() > 1:
                #    raise SyntaxaError("Unexpected modus")  # найдены более одного совпавшего прототипа
                #elif match_full.__len__() == 1:  # найден ровно один совпавший прототип

                if match_full.__len__() == 1:  # найден ровно один совпавший прототип
                    modus, ipos = match_full[0]

                    if proc_prior(lexis, modus):  # след.элемент более приоритетный?
                        # рекурсия-обработка более высокого приоритета
                        lst = parse_modus(lexis[ipos - 1:], pattern=modus.prototype[ipos - 1:])
                        if not lst:
                            print('НОЛЬ!!!')
                        lexis = lexis[:ipos-1] + lst
                                # parse_modus(lexis[ipos-1:], pattern=modus.prototype[ipos-1:])

                    if modus.sub.__len__() > 1 or modus.repl_only:
                        # ТОЛЬКО замена прототипа по модусу без создания новых лексем
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
                        # создание новой лексемы-заместителя прототипа
                        sub = modus.sub[0]
                        target = sub(sub.__name__)
                        target.childs = list(filter(lambda x: not isinstance(x,self.SpecSymbol), lexis[:ipos]))
                        lexis = [target] + lexis[ipos:]

                    if depth and match_pattern(pattern, lexis):
                        return lexis
                    else:
                        continue

                else:  # найдено только частичное совпадение
                    modus_found = False
                    for item in match: # поиск вложенных прототипов
                        modus, ipos = item
                        for pos in range(ipos, 0, -1):
                            lst = parse_modus(lexis[pos:], pattern=modus.prototype[pos:])
                            if not lst:
                                continue
                            lexis = lexis[:pos] + lst
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
        expression_list.append(self.EOL('EOL'))
        self.syntax_tree = parse_modus(expression_list, pattern=(self.Value,))
        if not self.syntax_tree: # если парсер вернул ошибку
            print('Syntax error:\n', expression, '\n', ' '*(len(expression)-self.last_pos) + '^' + ' '*self.last_pos)
            exit()
        #    print(''.join([m.value for m in expression_list])) # debug
        return self.syntax_tree
