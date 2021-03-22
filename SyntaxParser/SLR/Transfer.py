from __future__ import print_function
import re
data=open("grammer.txt.txt","r")
lines=data.read()
# lines=lines.replace("direct_abstract_declarator","abstract_declarator")
# print lines
data={
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
}
data={v:k for k, v in data.items()}
print(data.keys())
for key in data.keys():
    lines=lines.replace(key,'\''+data[key]+'\'')
print(lines)