from __future__ import annotations
import xml.etree.ElementTree as ET
from lib.Node import *
from lib.FunctionParser import Parser

class XmlParser:
    '''
        XML Doc parser for Ableton Live documentation
    '''
    TAG_MAP = {
        'Module': Module,
        'Class': Class,
        'Built-In': BuiltIn,
        'Property': Property,
        'Method': Method,
        'Sub-Class': SubClass,
        'Value': Value
    }

    def parseFile(self, path: str):
        root = ET.parse(path).getroot()
        rootModule = Module('root')
        previous: Node = None
        for elem in root:
            tag = elem.tag
            if 'Doc' == tag and previous is not None:
                textDoc = elem.text.strip()
                if isinstance(previous, Function):
                    self.__updateFunctionNode(previous, textDoc)
                else:
                    previous.docs = textDoc
                previous = None
                continue

            parts = elem.text.split('.')
            name = parts[-1]

            parent = rootModule.find(parts[:-1])

            if tag in self.TAG_MAP:
                node: Node = self.TAG_MAP[tag](name)
                parent[node.name] = node
            else:
                node = None

            previous = node
        return rootModule

    def __updateFunctionNode(self, node: Function, textDoc: str) -> None:
        parser = Parser()
        ast = parser.parse(textDoc)
        function = ast['function']
        if function['name'] != node.name:
            message = f'Parsed doc function name differs from this function node\'s name (parsed: "{function["name"]}", current: "{node.name}")'
            raise ValueError(message)

        for arg in function['args']:
            if 'value' in arg:
                argObj = OptionalArgument(arg['name'])
                argObj.value = arg['value']
            else:
                argObj = Argument(arg['name'])

            argObj.type = arg['type']

            node.args += [argObj]
        node.type = function['type']
        node.docs = ast['doc']

