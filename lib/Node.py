from __future__ import annotations
from typing import Dict, List

class Node:
    @property
    def children(self) -> Dict[str, Node]:
        return self._children

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def docs(self) -> str:
        return self._docs
    
    @docs.setter
    def docs(self, docs: str) -> None:
        self._docs = docs

    def __init__(self, name: str) -> None:
        self._name = name
        self._children = dict()
        self._docs = None

    def find(self, path: List[str]) -> Node:
        node = self
        for part in path:
            if part in node:
                node = node[part]
        return node
    
    def __getitem__(self, key) -> Node:
        return self.children[key]
    
    def __setitem__(self, key, value: Node) -> None:
        self.children[key] = value

    def __delitem__(self, key) -> None:
        del self.children[key]

    def __contains__(self, key) -> bool: 
        return key in self.children
    
    def __len__(self) -> int:
        return len(self.children)

    def members(self) -> Dict[str, Node]:
        return self.children.values()

    def filterMembers(self, type: type)-> List[type]:
        filtered = []
        for member in self.members():
            if isinstance(member, type):
                filtered += [member]
        return filtered

    def __str__(self) -> str:
        children = str.join(',', [str(child)
                            for child in self.children.values()])
        return f'\'{self.name}\': {{ {children } }}'


class Module(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def modules(self) -> List[Module]:
        return self.filterMembers(Module)
    
    def classes(self) -> List[Class]:
        return self.filterMembers(Class)

    def builtins(self) -> List[BuiltIn]:
        return self.filterMembers(BuiltIn)
    


class Function(Node):
    @property
    def args(self) -> List[Argument]:
        return self._args

    @args.setter
    def args(self, args):
        self._args = args

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type: str):
        self._type = type

    def __init__(self, name: str) -> None:
        self._type = None
        self._args = []
        super().__init__(name.rstrip('()'))

class Class(Node):
    def properties(self) -> List[Property]:
        return self.filterMembers(Property)
    def values(self) -> List[Value]:
        return self.filterMembers(Value)
    def methods(self) -> List[Method]:
        return self.filterMembers(Method)
    def subclasses(self) -> List[SubClass]:
        return self.filterMembers(SubClass)
    pass


class SubClass(Class):
    pass


class Method(Function):
    pass


class BuiltIn(Function):
    pass


class Property(Node):
    @property
    def type(self) -> str:
        return self._type
    @type.setter
    def type(self, type: str): 
        self._type = type

    def __init__(self, name: str) -> None:
        self._type = None
        super().__init__(name)

class Value(Node):
    pass

class Argument:
    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, type: str): 
        self._type = type

    def __init__(self, name: str) -> None:
        self._type = None
        self._name = name
        

class OptionalArgument(Argument):
    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __init__(self, name: str) -> None:
        self._value = None
        super().__init__(name)


__all__ = [
    'Node',
    'Module',
    'Class',
    'SubClass',
    'Function',
    'BuiltIn',
    'Method',
    'Property',
    'Value',
    'Argument',
    'OptionalArgument',
]