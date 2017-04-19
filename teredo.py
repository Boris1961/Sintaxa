import os
class Tree_OS(object):
    def __init__(self, root_script):
        self._root = os.path.abspath(root_script)

    def _str(self):
        return self.path

    def _childs(self, parent=None):
        try:
            # childs = os.listdir(parent.path) if parent else []
            list_of_childs = [os.path.join(parent.path, element) for element in
                              os.listdir(parent.path)] if parent else [self._root]
        except:
            list_of_childs = []
        return [{'name': os.path.basename(name),
                 'isnode': os.path.isdir(name),
                 'path': os.path.abspath(name)}
                for name in list_of_childs]

class Tree_HTML(object):
    def __init__(self, root_script):
        from bs4 import BeautifulSoup
        import requests

        try:
            root_script = requests.get(root_script).content
        except:
            raise RuntimeError("Something bad happened")

        self._root = BeautifulSoup(root_script, 'html.parser')

    def _str(self):
        return self.tag

    def _childs(self, parent=None):
        list_of_childs = list(parent.tag) if parent else [self._root]
        return [{'name': element.name if element.name else '<Text>',
                 'isnode': element.name is not None ,
                 'tag': element}
                for element in list_of_childs]

class Tree_EXPRESSION(object):
    pass

class Tree_WEB(object):
    pass

'''
    Ниже - классы абстрактного Teredo-дерева
    Классовая зависимость:  TeredoTree -> TeredoElement -> Teredo
'''

class TeredoTree(object):
    """
    Класс:
        TeredoTree: абстрактное дерево:
    Атрибуты:
        .root : type=TeredoElement: корневой элемент дерева
        .elements: type=list: список всех элементов (объектов класса TeredoElement) дерева
        .handler: type=type: класс-контейнер user-дерева (например, встроенные Tree_HTML или Tree_OS)


    """

    def __init__(self, root_script, class_handler):
        def walk(parent):
            # рекурсивно проходим по дереву и генерим все его элементы
            for child_dict in class_handler._childs(self,parent):
                child = TeredoElement(parent, child_dict)
                child.id = len(self.elements)
                child.root = self.root
                self.elements.append(child)
                parent.childs.append(child)
                if child.isnode:
                    walk(child)
        class_handler.__init__(self,root_script)
        root = TeredoElement(None, class_handler._childs(self)[0]) # генерим корневой элемент дерева
        self.handler = class_handler
        self.root = root.root = root
        self.elements = [root]
        root.id = 0
        root.tree = self
        walk(root)

    def __str__(self):
        return object.__str__(self.root.tree.handler._str(self))

    __repr__ = __str__

    # итератор дерева
    @staticmethod
    def iterate_tree(root, touch=False):
        if not touch:
            yield root
        for element in root.childs:
            yield element
            if element.isnode:
                for child in TeredoTree.iterate_tree(element, True):
                    yield child

    def get_pattern(self, dist=list(), wrapper_element=lambda x:x.name, wrapper_open=lambda x:'(',  wrapper_between=lambda x:',', wrapper_close=lambda x:')', filterer=lambda x:x.isnode):
        """
        Метод:
            get_pattern(self, dist=list(), wrapper_element=lambda x:x.name, wrapper_open=lambda x:'(',  wrapper_between=lambda x:',', wrapper_close=lambda x:')', filterer=lambda x:x.isnode):
        Аргументы:
            dist: type=list или dict: get_pattern генерит и возвращает либо строку-патерн элемента self, либо словарь патернов всех узлов поддерева self {element:pattern}
            wrapper_element, wrapper_open, wrapper_between, wrapper_close: функции форматирования вывода соответственно - самого узла, начала ветки, промежутка между узлами, конца ветки
            filterer: функция-фильтр поддерева self
        """

        def iterate_tree(element, dist):
            list_childs = list(filter(filterer,element.childs))
            str_tree = wrapper_element(element) + wrapper_open(element)
            for child in list_childs:
                str_tree += iterate_tree(child,dist)
                if list_childs[-1] != child:
                    str_tree += wrapper_between(child)
            str_tree += wrapper_close(element)
            if dist.__class__.__name__ == 'dict' :
                dist[element] = str_tree
            return str_tree
        str_tree = iterate_tree(self, dist)
        if dist.__class__.__name__ == 'list':
            return str_tree
        else:
            return dist

    def get_postfix(self, wrapper_element=lambda x:x.name):
        post_list = []
        for element in TeredoTree.iterate_tree(self):
            post_list = (['func(%i)<%s>' % (len(element.childs), wrapper_element(element))] if element.isnode else ['arg<%s>' % wrapper_element(element)]) + post_list
        return post_list


    def ShowPostfix(self):
        pass

    def Select(self, selector):
        pass

class TeredoElement(TeredoTree):
    """
    Класс:
        TeredoElement(TeredoTree) = элемент (узел) Teredo-дерева.
    Атрибуты:
        .root : корневой элемент дерева (класс TeredoElement)
        .next : соседний по ветке элемент справа (fault:None)
        .previous : соседний по ветке элемент слева (fault:None)
        .down : первый элемент в дочернем списке (fault:None)
        .up : родительский элемент(fault:None)
        .showfunc : функциональная (префиксная) форма поддерева (строка)
        .showtree : схематическая (древесная) форма поддерева (строка)
        .showpostfix : постфиксная) форма поддерева (строка)
        .showpath : путь к элементу от корня (список)
    """

    def __init__(self, parent, kwargs):
        if parent:
            self.floor = parent.floor + 1
            self.parent = parent
        else:
            self.floor = 0
            self.id = 0
            self.parent = None
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        self.childs = []

    def __getattr__(self, item):
        if not self.isnode:
            return None

        nodes = [child for child in self.parent.childs if child.isnode] if self.parent else [self]

        if item.lower() == 'next':
            try:
                # return nodes[nodes.index(self):][1]
                return nodes[nodes.index(self)+1]
            except:
                return None

        if item.lower() == 'previous':
            try:
                return nodes[nodes.index(self)-1]
            except:
                return None

        if item.lower() == 'down':
            try:
                return [child for child in self.childs if child.isnode][0]
            except:
                return None

        if item.lower() == 'up':
            try:
                return self.parent
            except:
                return None

        if item.lower() == 'showfunc':
            return self.get_pattern()

        if item.lower() == 'showtree':
            return self.get_pattern(wrapper_element=lambda x: '\t' * x.floor + x.name + '\n',
                                    wrapper_open=lambda x: '',
                                    wrapper_between=lambda x: '',
                                    wrapper_close=lambda x: '')

        if item.lower() == 'showpostfix':
            return self.get_postfix(wrapper_element=lambda x:x.name)

        if item.lower() == 'showpath':
            element = self
            path = []
            while element.parent:
                path = [element.name] + path
                element = element.parent
            return path

        return getattr(self.root, item)

    def LikeIt(self, elem_pattern=lambda x: x.name, elem_filter=lambda x: x.isnode):
        return [element for element in TeredoTree.iterate_tree(self.root) if elem_filter(element) and elem_pattern(element) == elem_pattern(self)]

class Teredo(TeredoElement):
    """
    Класс:
        Teredo(TeredoElement) = Teredo-дерево.
    Атрибут:
        .root = корневой элемент дерева (класс TeredoElement)
    Метод __init__:
        Аргументы:
            descriptor: type=str: дескриптор корневого элемента дерева(например: "C:/TOOLS" при forester="os", или "https:/pythonworld.ru/" при forester="html")
            forester: type=str или type: передает класс дерева (лес) - строку-дескриптор встроенного дерева ("html", "os") или класс-обработчик <class_handler> пользовательского дерева
                Протокол класса <class_handler>:
                    class <class_handler>(object):
                        def __init__(self, root_script):
                            self._root = <normalized_root_name> (root_script)

                        def _str(self):
                            return <formatted_name> (self)

                        def _childs(self, parent=None): # parent=None означает, что self - корневой узел
                            ...script generated <list_of_childs>...
                            return [{'<attr1>': <get_attr1>(name), ..., '<attrN>': <get_attrN>(name)} for name in <list_of_childs>]
                    Имена по протоколу : _root , _str, _childs

    """
    def __init__(self,descriptor,forester="html"):

        if forester.__class__.__name__ == 'type':
            self.tree = TeredoTree(descriptor, forester)
        elif forester.lower() == 'html':
            self.tree = TeredoTree(descriptor, Tree_HTML)
        elif forester.lower() == 'os':
            self.tree = TeredoTree(descriptor, Tree_OS)

        self.root = self.tree.root
        self.root.ancestor = self

    def __getattr__(self, item):
        return getattr(self.root, item)
