# coding=utf-8

from syntaxa import *
from teredo import *


class Synt_Tree(object):
    def __init__(self, root_script):
        self._root = root_script

    def _str(self):
        return self.name

    def _childs(self, parent=None):
        if parent is None:
            list_of_childs = self._root
        else:
            list_of_childs = getattr(parent.obj, 'childs', [])
        return [{'name': child.name,
                 'obj': child,
                 'isnode': hasattr(child, 'childs')}
                for child in list_of_childs]

test_str = """
            frog(a(1,2),b(3))
            func(A-X)*12**17/puk(C-7)
            ((A-X)*12)**(17/(C-7))+(Q*12+(19*y)*8**9+C+foo(17**gaga(2+5*8)))
            1+B(17+C)+119
            1+B(17+5,7)
            B(17,7,16,500)+Foo(19,16)
            (a(1,2),b(3,4))+19**17/1445
            frog(a(1,2),b(3,4),7)+Cu(119)-19**17/1445
            177))+/fooling
            """

lang = Syntaxa()
for expression in test_str.split():

    try:
        synt_root = lang.compile_exp(expression)
    except:
        continue

    print(70*'_' + '\n' + expression)

    t = Teredo(synt_root, Synt_Tree)

    # functional screening
    print(t.get_pattern(wrapper_element=lambda x: x.obj.value,
                        wrapper_open=lambda x: '(' if x.isnode else '',
                        wrapper_between=lambda x: ',' if isinstance(x.parent.obj, lang.Sequance) else '' ,
                        wrapper_close=lambda x: ')' if x.isnode else  '',
                        filterer=lambda x:True))

    # tree screening
    print(t.get_pattern(wrapper_element=lambda x: '\t'*x.floor + x.obj.value + '\n',
                                        wrapper_open=lambda x: '',
                                        wrapper_between=lambda x: '',
                                        wrapper_close=lambda x: '',
                                        filterer=lambda x:True))
