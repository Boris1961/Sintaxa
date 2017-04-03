# coding=utf-8

from syntaxa import *
from teredo import *

lang = Syntaxa()
exp_str = '((A-X)*12)**(B/(C-7))+(Q*12+19+C)'
synt_root = lang.exec_state(exp_str)

print([cl for cl in dir(s) if getattr(getattr(s,cl),'pseudo','')=='Int'])

class Synt_Tree(object):
    def __init__(self, root_script):
        self._root = root_script
    def _str(self):
        return self.name
    def _childs(self, parent=None):
        if parent is None:
            list_of_childs = self._root
        else:
            list_of_childs = getattr(parent.obj,'childs',[])
        return [{'name': child.name,
                 'obj': child,
                 'isnode': hasattr(child, 'childs')}
                for child in list_of_childs]

t = Teredo(synt_root, Synt_Tree)
print(t.get_pattern(wrapper_element=lambda x: '\t'*x.floor + x.obj.value + '\n',
                                    wrapper_open=lambda x: '',
                                    wrapper_between=lambda x: '',
                                    wrapper_close=lambda x: '',
                                    filterer=lambda x:True))

print(t.get_pattern(wrapper_element=lambda x: x.obj.value,
                    wrapper_open=lambda x: '(' if x.isnode else '',
                    wrapper_between=lambda x: '',
                    wrapper_close=lambda x: ')' if x.isnode else  '',
                    filterer=lambda x:True))

# Expression(Expression((Expression(Expression((Expression(A-X)))*12)))**Expression((Expression(B/Expression((Expression(C-7)))))))
# <SIn>(<Exp>((<SIn>(<Exp>((<SIn>(<Var>-<Var>)))*<Int>)))**<Exp>((<SIn>(<Var>/<Exp>((<SIn>(<Var>-<Int>))))))+<Exp>((<SIn>(<Var>*<Int>+<Int>+<Var>))))