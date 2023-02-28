from pathlib import Path
from shutil import rmtree
from .Node import *

def create(rootModule: Module, path: str = './'):
    p = Path(path)

    # Clean target
    if not p.exists():
        p.mkdir()
    elif not p.is_dir():
        raise ValueError(f'Path "{p.absolute()}" exists but is not a directory')
    for x in p.iterdir():
        rmtree(x)

    if isinstance(rootModule, Module):
        createModule(p, rootModule)

def line(data: str = '', indent: int = 0):
    indentChars = ' ' * indent * 4
    return f'{indentChars}{data}\n'

def code(data: list, indent: int = 0):
    for row in data:
        if type(row) is str:
            yield line(row, indent)
        elif type(row) is list:
            yield from code(row, indent + 1)


def createModule(path: Path, module: Module):
    name = module.name
    modules = module.modules()
    if len(modules) == 0:
        path = path / f'{name}.py'
        with open(path, 'a+') as f:
            f.writelines(['from __future__ import annotations\n']);
            for classObj in module.classes():
                classData = getClass(classObj)
                f.writelines(code(classData))

            for builtin in module.builtins():
                builtInData = getFunction(builtin)
                f.writelines(code(builtInData))

    else:
        path = path / name
        path.mkdir()
        for submodule in modules:
            createModule(path, submodule)
        
        with open(path / '__init__.py', 'a+') as f:
            for submodule in modules:
                f.writelines(code([
                    f'import {submodule.name}'
                ]))
                

def getFunction(funcObj: Function) -> list:
    args = ''
    for arg in funcObj.args:
        args += f'{arg.name}'
        if arg.type is not None:
            args += f': {arg.type}'
        if isinstance(arg, OptionalArgument):
            args += f'={arg.value}'
        args += ','
    
    args = args.rstrip(',')

    data = [
        '',
        f'def {funcObj.name}({args}) -> {funcObj.type}:',
        [
            *getDocString(funcObj),
            'pass'
        ]
    ]
    return data

def getClass(classObj: Class):
    valuesData = []
    for value in classObj.values():
        if value.docs is not None:
            valuesData += [
                f'{value.name} = type(\'Any\', (), {{\'__doc__\': \'{value.docs}\'}})()',
                *getDocString(value),
                ''
            ]
        else:
            valuesData += [
                f'{value.name} = type(\'Any\', ())()',
                ''
            ]

    propertiesData = []
    for property in classObj.properties():
        propertiesData += [
            f'@property',
            f'def {property.name}(self):',
            [
                *getDocString(property),
                'pass'
            ],
            f'@{property.name}.setter',
            f'def {property.name}(self,value):',
            ['pass'],
            ''
        ]
    
    methodsData = []
    for method in classObj.methods():
        methodsData += getFunction(method)

    subClassesData = []
    for subClass in classObj.subclasses():
        subClassesData += getClass(subClass)

    data = [
        '',
        f'class {classObj.name}:',
        [
            *getDocString(classObj),
            *valuesData,
            *propertiesData,
            *methodsData,
            *subClassesData,
            'pass'
        ]
    ]

    return data

def getDocString(node: Node):
    if node.docs is not None:
        docString = [
            '"""',
            f'{node.docs}',
            '"""'
            ''
        ]
    else:
        docString = [None]
    return docString
