from ply import lex, yacc


class Lexer(object):
    '''
        Lexer for function signatures
    '''

    states = (
        ('args', 'exclusive'),
        ('optargs', 'exclusive'),
        ('optargsvalue', 'exclusive'),
        ('argtype', 'exclusive'),
        ('ret', 'exclusive'),
        ('comment', 'exclusive'),
    )

    tokens = (
        'NAME',
        'TYPE',
        'VALUE',
        'COMMA',
        'LPAREN',
        'RPAREN',
        'LSBRACE',
        'RSBRACE',
        'EQ',
        'RET',
        'COMMENT',
    )

    t_args_optargs_NAME     = r'\w+'
    t_argtype_TYPE          = r'\w+'
    t_comment_COMMENT       = r'.+'
    t_args_optargs_COMMA    = r','
    t_ANY_ignore            = ' \t'
    t_comment_ignore        = ''

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_ANY_error(self,t):
         print("Illegal character '%s'" % t.value[0])
         t.lexer.skip(1)

    def t_NAME(self, t):
        r'\w+'
        t.value = str(t.value)
        return t
    
    def t_LPAREN(self, t):
        r'\('
        t.lexer.push_state('args')
        return t

    def t_args_RPAREN(self, t):
        r'\)'
        t.lexer.pop_state()
        return t
    
    def t_RET(self, t):
        r'(->)|(-&gt;)'
        t.lexer.push_state('ret')
        return t

    def t_ret_TYPE(self, t):
        r'\w+'
        t.lexer.pop_state()
        return t
    
    def t_args_optargs_LPAREN(self, t):
        r'\('
        t.lexer.push_state('argtype')
        return t

    def t_argtype_RPAREN(self, t):
        r'\)'
        t.lexer.pop_state()
        return t

    def t_args_optargs_LSBRACE(self, t):
        r'\['
        t.lexer.push_state('optargs')
        return t
    
    def t_optargs_EQ(self, t):
        r'='
        t.lexer.push_state('optargsvalue')
        return t
    def t_optargsvalue_VALUE(self, t):
        r'[\w\.\'"+-]+'
        t.lexer.pop_state()
        return t
    def t_optargs_RSBRACE(self, t):
        r'\]'
        t.lexer.pop_state()
        return t
    
    def t_begin_comment(self, t): 
        r':\s?'
        t.lexer.push_state('comment')

    def tokenize(self, data):
        self.lexer.input(data)
        while True:
            token = self.lexer.token()
            if not token:
                break
            yield token

class Parser:
    '''
        Parser for function signature
    '''
    tokens = Lexer.tokens

    def __init__(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        pass
    
    def __del__(self):
        pass
    
    def parse(self, data):
        lexer = Lexer()
        return self.parser.parse(data)

    # GRAMAR START
    def p_expression(self, p): 
        '''
            expression : func 
                       | func doc
        '''
        root = {
            'function': p[1]
        }
        if len(p) > 2:
            root['doc'] = p[2]
        p[0] = root

    def p_empty(self, p):
        '''
            empty :
        '''
        pass
    
    def p_func(self, p):
        '''
            func : NAME LPAREN funcargs RPAREN
                 | NAME LPAREN funcargs RPAREN funcret
        '''
        func = {
            'name': p[1],
            'args': p[3]
        }
        if len(p) > 4:
            func['type'] = p[5]
        p[0] = func

    def p_funcargs(self, p):
        '''
            funcargs : empty
                     | args
                     | args LSBRACE COMMA optargs RSBRACE
        '''
        if p[1] is None:
            args = []
        else:
            args = p[1]
        if len(p) > 2:
            args = args + p[4]
        p[0] = args

    def p_args(self, p):
        '''
            args : args COMMA arg
                 | arg
        '''
        
        if len(p) > 2:
            # multiple arguments
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_arg(self, p):
        '''
            arg : NAME
                | argtype NAME
        '''
        arg = {}
        if len(p) > 2:
            arg['type'] = p[1]
            arg['name'] = p[2]
        else:
            arg['type'] = 'Any'
            arg['name'] = p[1]
        p[0] = arg    

    def p_argtype(self, p): 
        '''
            argtype : LPAREN TYPE RPAREN
        '''
        p[0] = p[2]

    def p_optargs(self, p):
        '''
            optargs : optargs LSBRACE COMMA optargs RSBRACE
                    | optarg
        '''
        if len(p) > 2:
            # multiple arguments
            p[0] = p[1] + p[4]
        else:
            p[0] = [p[1]]

    def p_optarg(self, p):
        '''
            optarg : arg EQ VALUE
        '''
        p[1]['value'] = p[3]
        p[0] = p[1]

    def p_funcret(self, p):
        '''
            funcret : RET TYPE
        '''
        p[0] = p[2]

    def p_doc(self, p): 
        '''
            doc : COMMENT
        '''
        p[0] = p[1]

    def p_error(self, p): 
        message = f'Syntax error: Unexpected {p.type}: {p.value}'
        message += f'\nAt line {p.lineno}, position {p.lexpos} in:'
        message += f'\n{p.lexer.lexdata}'
        raise SyntaxError(message)
