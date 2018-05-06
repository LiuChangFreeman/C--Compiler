# -*- coding: utf-8 -*-
Reserved = {'if': 'IF', 'else' : 'ELSE', 'while' : 'WHILE', 'do': 'DO',
            'break':'BREAK', 'continue':'CONTINUE','for':'FOR',
            'int':'INT','float':'FLOAT', 'bool':'BOOL','string':'STRING',
            'switch':'SWITCH', 'case':'CASE','return':'RETURN',
            'void':'VOID','char':'CHAR', 'default':'DEFAULT','goto':'GOTO',
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