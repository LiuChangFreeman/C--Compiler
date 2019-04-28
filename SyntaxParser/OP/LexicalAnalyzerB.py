# -*- coding: utf-8 -*-
from __future__ import print_function
from ply import lex
reserved = {
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'break':'BREAK',
    'continue':'CONTINUE',
    'for':'FOR',
    'double':'DOUBLE',
    'int':'INT',
    'float':'FLOAT',
    'long':'LONG',
    'short':'SHORT',
    'bool':'BOOL',
    'switch':'SWITCH',
    'case':'CASE',
    'return':'RETURN',
    'void':'VOID',
    'unsigned':'UNSIGNED',
    'enum':'ENUM',
    'register':'REGISTER',
    'typedef':'TYPEDEF',
    'char':'CHAR',
    'extern':'EXTERN',
    'union':'UNION',
    'const':'CONST',
    'signed':'SIGNED',
    'default':'DEFAULT',
    'goto':'GOTO',
    'sizeof':'SIZEOF',
    'volatile':'VOLATILE',
    'static':'SATTIC',
    'auto':'AUTO',
    'struct':'STRUCT'
}
tokens=[
    'Identifier',
    'Inum',
    'Fnum',
    'Separator',
    'Operator',
    'String',
]+ list(reserved.values())
t_Separator = r'\{|\}|\[|\]|\(|\)|~|,|;|\.|\?|\:'
t_Operator= r'\+|\+\+|-|--|\+=|-=|\*|\*=|%|%=|->|\||\|\||\|=|/|/=|>|<|>=|<=|=|==|!=|!|&'
def t_Identifier(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.value = str(t.value)
    t.type = reserved.get(t.value, 'Identifier')
    return t
def t_String(t):
    r'\".+?\"'
    t.value = str(t.value)
    return t
def t_Inum(t):
    r'\d+'
    t.value = int(t.value)
    return t
def t_Fnum(t):
    r'(-?\d+)(\.\d+)?'
    t.value = float(t.value)
    return t
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
t_ignore  = ' \t'
def t_error(t):
    print ("illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
lexer = lex.lex()
data=open("test.c","r").read()
lexer.input(data)
while True:
    token = lexer.token()
    if not token: break
    print (token)