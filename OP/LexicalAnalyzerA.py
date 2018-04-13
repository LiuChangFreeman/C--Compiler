# -*- coding: utf-8 -*-
KeyWordList = ['if', 'else', 'while', 'break', 'continue', 'for', 'double', 'int', 'float', 'long', 'short', 'bool','switch', 'case', 'return', 'void','unsigned']
SeparatorList = ['{', '}', '[', ']', '(', ')', '~', ',', ';', '.', '?', ':', ' ']
OperatorList = ['+', '++', '-', '--', '+=', '-=', '*', '*=', '%', '%=', '->', '|', '||', '|=','/', '/=', '>', '<', '>=', '<=', '=', '==', '!=', '!', '&']
CategoryDict = {
    # keyword
    "far": 257,
    "near": 258,
    "pascal": 259,

    "asm": 261,
    "cdecl": 262,
    "huge": 263,
    "auto": 264,
    "double": 265,
    "int": 266,
    "struct": 267,
    "break": 268,
    "else": 269,
    "long": 270,
    "switch": 271,
    "case": 272,
    "enum": 273,
    "register": 274,
    "typedef": 275,

    "extern": 277,
    "return": 278,
    "union": 279,
    "const": 280,
    "float": 281,
    "short": 282,
    "unsigned": 283,
    "continue": 284,
    "for": 285,
    "signed": 286,
    "void": 287,
    "default": 288,
    "goto": 289,

    "volatile": 291,
    "do": 292,
    "if": 293,
    "while": 294,
    "static": 295,
    "interrupt": 296,
    "sizeof": 297,
    "NULL": 298,
    # separator
    "{": 299,
    "}": 300,
    "[": 301,
    "]": 302,
    "(": 303,
    ")": 304,
    "~": 305,
    ",": 306,
    ";": 307,
    ".": 308,
    "#": 309,
    "?": 310,
    ":": 311,
    # operator
    "<<": 312,
    ">>": 313,
    "<": 314,
    "<=": 315,
    ">": 316,
    ">=": 317,
    "=": 318,
    "==": 319,
    "|": 320,
    "||": 321,
    "|=": 322,
    "^": 323,
    "^=": 324,
    "&": 325,
    "&&": 326,
    "&=": 327,
    "%": 328,
    "%=": 329,
    "+": 330,
    "++": 331,
    "+=": 332,
    "-": 333,
    "--": 334,
    "-=": 335,
    "->": 336,
    "/": 337,
    "/=": 338,
    "*": 339,
    "*=": 340,
    "!": 341,
    "!=": 342,

    "<<=": 344,
    ">>=": 345,
    "inum": 346,
    "int16": 347,
    "int8": 348,
    "char": 350,
    "string": 351,
    "bool": 352,
    "fnum": 353,
    "IDN": 354
}
current_row = -1
current_line = 0
out_line = 1
def getchar(input_str):
    global current_row
    global current_line
    current_row += 1
    if current_row == len(input_str[current_line]):
        current_line += 1
        current_row = 0
    #读到行末换行
    if current_line == len(input_str) - 1:
        return 'EOF'
    #读到文件末尾
    return input_str[current_line][current_row]#返回一个字符
def ungetchar(input_str):
    global current_row
    global current_line
    current_row = current_row - 1
    if current_row < 0:
        current_line = current_line - 1
        current_row = len(input_str[current_row]) - 1
    #退行
    return input_str[current_line][current_row]#返回一个字符
def error(msg, line=None, row=None):
    global out_line
    if line is None:
        line = current_line + 1
    if row is None:
        row = current_row + 1
    print(str(line) + ':' + str(row) + '  Error:  ' + msg)
    out_line = out_line + 1
def scanner(input_str):
    global current_line
    global current_row
    current_char = getchar(input_str)
    if current_char == 'EOF':
        return ('EOF', '', '')
    #读到文件末尾返回
    if current_char.strip() == '':
        return
    if current_char.isdigit():
        int_value = 0
        while current_char.isdigit():
            int_value = int_value * 10 + int(current_char)
            current_char = getchar(input_str)
        #十进制常数计算值大小
        if current_char not in OperatorList and current_char not in SeparatorList and current_char != 'e':
            line = current_line + 1
            row = current_row + 1
            # ungetchar(input_str)
            error('illigal identifier', line, row)
            #既不是界符也不是操作符，也不是科学记数法，异常退出
            # return ('EOF', '', '')
            return ('', '', '')
        if current_char != '.' and current_char != 'e':
            ungetchar(input_str)
            #不是小数也不是科学记数法，返回整数
            return ('INUM', int_value, CategoryDict['inum'])
        if current_char == 'e':
            power_value = str(int_value) + 'e'
            current_char = getchar(input_str)
            if current_char == '+' or current_char == '-':
                power_value += current_char
                current_char = getchar(input_str)
            while current_char.isdigit():
                power_value += current_char
                current_char = getchar(input_str)
            if current_char not in OperatorList and current_char not in SeparatorList:
                line = current_line + 1
                row = current_row + 1
                # ungetchar(input_str)
                error('illigal const int value in power', line, row)
                # return ('EOF', '', '')
                return ('', '', '')
            ungetchar(input_str)
            #返回科学记数法的值
            return ('INUM', power_value, CategoryDict['inum'])
        if current_char == '.':
            float_value = str(int_value) + '.'
            current_char = getchar(input_str)
            while current_char.isdigit():
                float_value += current_char
                current_char = getchar(input_str)
            if current_char not in OperatorList and current_char not in SeparatorList or current_char == '.':
                line = current_line + 1
                row = current_row + 1
                # ungetchar(input_str)
                error('illigal const float value', line, row)
                # return ('EOF', '', '')
                return ('', '', '')
            ungetchar(input_str)
            #返回浮点数的值
            return ('FNUM', float_value, CategoryDict['fnum'])
    if current_char.isalpha() or current_char == '_':
        string = ''
        while current_char.isalpha() or current_char.isdigit() or current_char == '_' and current_char != ' ':
            string += current_char
            current_char = getchar(input_str)
            if current_char == 'EOF':
                break
        ungetchar(input_str)
        if string in KeyWordList:
            #是保留字
            return (string, '', CategoryDict[string])
        else:
            #是标识符
            return ('IDN', string, CategoryDict['IDN'])

    if current_char == '\"':
        str_literal = ''
        line = current_line + 1
        row = current_row + 1
        current_char = getchar(input_str)
        while current_char != '\"':
            str_literal += current_char
            current_char = getchar(input_str)
            if current_char == 'EOF':
                error('missing terminating \"', line, row)
                #缺失右引号错误
                current_line = line
                current_row = row
                return ('EOF', '', '')
        #是字符串
        return ('STRING_LITERAL', str_literal, CategoryDict['string'])

    if current_char == '/':
        next_char = getchar(input_str)
        line = int(current_line) + 1
        row = int(current_row) + 1
        if next_char == '*':
            comment = ''
            next_char = getchar(input_str)
            while True:
                if next_char == 'EOF':
                    error('unteminated /* comment', line, row)
                    #注释符缺失错误
                    return ('EOF', '', '')
                if next_char == '*':
                    end_char = getchar(input_str)
                    if end_char == '/':
                        return None
                    if end_char == 'EOF':
                        error('unteminated /* comment', line, row)
                        # 注释符缺失错误
                        return ('EOF', '', '')
                comment += next_char
                next_char = getchar(input_str)
        else:
            ungetchar(input_str)
            op = current_char
            current_char = getchar(input_str)
            if current_char in OperatorList:
                op += current_char
            else:
                ungetchar(input_str)
            #是操作符
            return ('OP', op, CategoryDict[op])

    if current_char in SeparatorList:
        #是界符
        return ('SEP', current_char, CategoryDict[current_char])

    if current_char in OperatorList:
        op = current_char
        current_char = getchar(input_str)
        if current_char in OperatorList:
            op += current_char
        else:
            ungetchar(input_str)
        # 是操作符
        return ('OP', op, CategoryDict[op])
    else:
        error('unknown character: ' + current_char)
def lexer_analysis(input_str):
    global current_row
    global current_line
    global out_line
    current_row = -1
    current_line = 0
    analysis_result = []

    while True:
        r = scanner(input_str)
        if r is not None:
            if r[0] == 'EOF':
                break
            analysis_result.append(str(r[0]) + "\t\t" + str(r[1]) + "\t\t" + str(r[2]))
    return analysis_result
def main():
    global analysis
    input_str = []
    input_raw = open("test.c","r").read()
    input_str = input_raw.split("\n")
    lexer_analysis(input_str)
    out_line = 1
    result = lexer_analysis(input_str)
    for each in result:
       print(str(out_line) + '.end'+'    '+each)
       out_line = out_line + 1
if __name__ == '__main__':
    main()
