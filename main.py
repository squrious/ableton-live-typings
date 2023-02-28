from lib.XmlParser import XmlParser
import lib.ModuleGenerator as ModuleGenerator
import pickle


def getRootModule(xmlPath: str):
    with open('root.pickle', 'a+b') as cached:
        cached.seek(0)
        try:
            rootModule = pickle.load(cached)
        except EOFError:
            cached.seek(0)
            parser = XmlParser()
            rootModule = parser.parseFile(xmlPath)
            pickle.dump(rootModule, cached)
    return rootModule        

rootModule = getRootModule('./Live10.1.19.xml')

ModuleGenerator.create(rootModule['Live'], './typings')

