# -*- coding: utf-8 -*-
Reserved = {'if' : 'IF','then' : 'THEN','else' : 'ELSE', 'while' : 'WHILE', 'break':'BREAK', 'continue':'CONTINUE', 'for':'FOR', 'double':'DOUBLE','do':'DO',
    'string':'STRING','int':'INT','float':'FLOAT', 'long':'LONG', 'short':'SHORT', 'bool':'BOOL', 'switch':'SWITCH', 'case':'CASE', 'return':'RETURN', 'void':'VOID',
    'unsigned':'UNSIGNED', 'enum':'ENUM','register':'REGISTER', 'typedef':'TYPEDEF', 'char':'CHAR','extern':'EXTERN', 'union':'UNION',
    'const':'CONST', 'signed':'SIGNED', 'default':'DEFAULT','goto':'GOTO', 'sizeof':'SIZEOF','volatile':'VOLATILE','static':'STATIC','auto':'AUTO','struct':'STRUCT'
}#保留字
type=[
    'seperator','operator','id','string','char','int','float'
]#类别
regexs=[
    '\{|\}|\[|\]|\(|\)|,|;|\.|\?|\:'#界符
    ,'\+\+|\+|>>=|<<=|>>|<<|--|-|\+=|-=|\*|\*=|%|%=|->|\||\|\||\|=|/|/=|>|<|>=|<=|==|!=|^=|=|!|~|&&|&|&='#操作符
    ,'[a-zA-Z_][a-zA-Z_0-9]*'#标识符
    ,'\".+?\"'#字符串
    ,'\'.{1}\''#字符
    ,'\d+'#整数
    ,'-?\d+\.\d+?'#浮点数
]#匹配使用的正则表达式
op_table={
    ">>=":"RIGHT_ASSIGN",
    "<<=":"LEFT_ASSIGN",
    "+=":"ADD_ASSIGN",
    "-=":"SUB_ASSIGN",
    "*=":"MUL_ASSIGN",
    "/=":"DIV_ASSIGN",
    "%=":"MOD_ASSIGN",
    "&=":"AND_ASSIGN",
    "^=":"XOR_ASSIGN",
    "|=":"OR_ASSIGN",
    ">>":"RIGHT_OP",
    "<<":"LEFT_OP",
    "++":"INC_OP",
    "--":"DEC_OP",
    "->":"PTR_OP",
    "&&":"AND_OP",
    "||":"OR_OP",
    "<=":"LE_OP",
    ">=":"GE_OP",
    "==":"EQ_OP",
    "!=":"NE_OP",
}#操作符类型表