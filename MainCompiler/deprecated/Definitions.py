# -*- coding: utf-8 -*-
reserved = {'if' : 'IF', 'then' : 'THEN', 'else' : 'ELSE', 'while' : 'WHILE', 'break': 'BREAK', 'continue': 'CONTINUE', 'for': 'FOR', 'double': 'DOUBLE', 'do': 'DO',
    'string':'STRING','int':'INT','float':'FLOAT', 'long':'LONG', 'short':'SHORT', 'bool':'BOOL', 'switch':'SWITCH', 'case':'CASE', 'return':'RETURN', 'void':'VOID',
    'unsigned':'UNSIGNED', 'enum':'ENUM','register':'REGISTER', 'typedef':'TYPEDEF', 'char':'CHAR','extern':'EXTERN', 'union':'UNION','function':'FUNCTION',
    'const':'CONST', 'signed':'SIGNED', 'default':'DEFAULT', 'goto':'GOTO', 'sizeof':'SIZEOF', 'volatile':'VOLATILE', 'static':'STATIC', 'auto':'AUTO', 'struct':'STRUCT'
    , 'number':'NUMBER'
            }#保留字
type=[
    'seperator', 'operator', 'identifier', 'string', 'char', 'int', 'float'
]#类别
regexs=[
    '\{|\}|\[|\]|\(|\)|,|;|\.|\?|\:'#界符
    ,'\+|-|\*|%|/|>|<|==|!=|='#操作符
    ,'[a-zA-Z_][a-zA-Z_0-9]*'#标识符
    ,'\".+?\"'#字符串
    ,'\'.{1}\''#字符
    ,'\d+'#整数
    ,'-?\d+\.\d+?'#浮点数
]#匹配使用的正则表达式
# ,'\+\+|\+|>>=|<<=|>>|<<|--|-|\+=|-=|\*|\*=|%|%=|->|\||\|\||\|=|/|/=|>|<|>=|<=|==|!=|^=|=|!|~|&&|&|&='#操作符