#coding:utf-8
from __future__ import print_function
import re
import os
import io
import copy
import json

reserved = {
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'for': 'FOR',
    'int':'INT',
    'return':'RETURN',
    'void':'VOID',
    'function':'FUNCTION',
    'goto':'GOTO' ,
    'number':'NUMBER'
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

SOURCE_PATH= ''
NAME_SOURCE_CODE="test.c--"
NAME_GRAMMER_JSON="grammer.json"
NAME_GRAMMER_PLAIN="grammer.txt"
NAME_LR1= "lr1.table"
NAME_ANALYSIS= "analysis.table"
NAME_INTERMEDIATE_CODE="result.middle"
NAME_ASM="result.asm"

CURRENT_LINE=1
CURRENT_LABLE=0
CURRENT_TEMP=0
CURRENT_FUNCTION=0
CURRENT_STEP=0
CURRENT_OFFSET=0
CURRENT_PRODUCTION=None
CURRENT_FUNCTION_SYMBOL=None

PRODUCTION_GROUP=[]
PRODUCTION_GROUP_DOTED=[]
TERMINAL_SYMBOL_GROUP=[]
NONE_TERMINAL_SYMBOL_GROUP=[]

STATE_INDEX_TABLE={}
TERMINAL_INDEX_TABLE={}
NONE_TERMINAL_INDEX_TABLE={}

ACTION=[]
GOTO=[]
REDUCE={}
SHIFT={}
FIRST={}
FOLLOW={}

OP_STACK = []
STATE_STACK = []
SEMANTIC_STACK=[]

SYMBOL_TABLE=[]
FUNCTION_TABLE=[]
REGISTER_TABLE={'$' + str(x): '' for x in range(7, 26)}

RECORD_TABLE=None
START_PRODUCTION=None
TEMP_VALUE_STATUS={}
TOKENS=[]
MIPS_CODE=[]
INTERMEDIATE_CODE=[]
STACK_OFFSET=8000
DATA_SEGMENT=10010000


class Node():
    def __init__(self):
        self.place=None#语句块入口的中间变量
        self.code=[]#传递而来的或者生成的中间代码
        self.stack = []#翻译闭包表达式所用的临时栈
        self.name=None#语句块的标识符
        self.type = None#结点的数据类型
        self.data = None#结点携带的数据
        self.begin=None#循环入口
        self.end=None#循环出口
        self.true=None#为真时的跳转位置
        self.false=None#为假时的跳转位置

class Symbol:
    def __init__(self):
        self.name=None#符号的标识符
        self.type=None#类型
        self.size=None#占用字节数
        self.offset=None#内存偏移量
        self.place=None#对应的中间变量
        self.function=None#所在函数

class FunctionSymbol:
    def __init__(self):
        self.name = None#函数的标识符
        self.type = None#返回值类型
        self.lable = None#入口处的标签
        self.params = []#形参列表
        self.temp=[]#局部变量列表

class Production():
    def __init__(self, left, right, position=0, terminals=None):
        self.left=left
        self.right=right
        self.position=position
        self.terminals=terminals

    def next_doted_production(self):
        return Production(self.left,
                          self.right,
                          self.position + 1,
                          self.terminals)

    def to_string(self):
        result=self.left+'->'
        position=1
        for data in self.right:
            if position==self.position:
                result += '@'
            result += data['type']+' '
            position += 1
        if position == self.position:
            result += '@'
        result += ',['
        if self.terminals!=None:
            if len(self.terminals)>0:
                for item in sorted(self.terminals):
                    result += '\''+item+'\''+','
                result= result[:-1]
        result += ']'
        return result

    def to_string_compact(self):
        result=self.left+'->'
        for data in self.right:
            result += data['type']+' '
        return result

class State():
    def __init__(self,name):
        self.name=name
        self.productions=[]
        self.string=[]

    def to_string(self):
        for production in self.productions:
            if production.to_string() not in self.string:
                self.string.append(production.to_string())
        return "\n".join(sorted(self.string))

    def get_item(self):
        result=[]
        for production in self.productions:
            expressions = production.right
            position = production.position
            if position < len(expressions) + 1:
                node = expressions[position - 1]
                if node not in result:
                    result.append(node)
        return result

class DFA():
    def __init__(self):
        self.state=[]
        self.edge=[]

    def add_state(self, Ix):
        self.state.append(Ix)

    def add_edge(self, Ia, t, Ib):
        self.edge.append((Ia,t,Ib))

def remove_comments(text):#去除注释
    comments = re.findall('//.*?\n', text, flags=re.DOTALL)
    if(len(comments)>0):
        text=text.replace(comments[0], "")
    comments = re.findall('/\*.*?\*/', text, flags=re.DOTALL)
    if(len(comments)>0):
        text=text.replace(comments[0], "")
    return text

def scan(line):#经行一次扫描，返回得到的token以及剩余的字符串
    max=''
    target_regex=regexs[0]
    index_sub=0
    match=False
    for regex in regexs:
        result=re.findall(regex,line,flags=re.DOTALL)
        if(len(result)>0):
            result=result[0]
            index=line.find(result)
            if(index!=0):
                continue
            else:
                if(len(result)>len(max)):
                    match=True
                    max=result
                    target_regex=regex
    if(match==False):#出错处理
        print(u"非法字符："+line[0])
        return {"data":line[0],"regex":None,"remain":line[1:]}
    else:
        return {"data":max,"regex":target_regex,"remain":line[index_sub+len(max):]}

def scan_line(line):#对一行进行重复扫描，获得一组token
    tokens=[]
    result = line.strip().strip('\t')
    origin=result
    while True:
        if result == "":
            break
        before=result
        result = scan(result)
        if result['regex']:
            token = {}
            token['class'] = "T"
            token['row'] = CURRENT_LINE
            token['colum'] = origin.find(before)+1
            token['name'] = type[regexs.index(result['regex'])].upper()
            token['data'] = result['data']
            token['type'] = token['name']
            if result['data'] in reserved:#保留字，对应文法中->不加引号，认定为终结符
                token['name'] = reserved[result['data']].lower()
                token['type'] = token['name']
            if token['name']=="operator".upper() or token['name']=="seperator".upper():
                #操作符或者界符，对应文法中->加引号，认定为终结符
                token['type'] = token['data']
            if token['name'] == "int" and token['type'] != "int":
                token['data'] = int(token['data'])
            if token['name'] == "float" and token['type'] != "float":
                token['data'] = float(token['data'])
            if token['name'] == "INT" or token['name'] == "FLOAT":
                #整数与浮点数统一
                token['type'] ='number'
            tokens.append(token)
        result = result['remain'].strip().strip('\t')
        if (result == ""):
            return tokens
    return tokens

def generate_tokens(path):
    fd=open(path,'r')
    lines=remove_comments(fd.read()).split('\n')
    with open(path,'wb')as f:
        for line in lines:
            f.write(line.strip().strip('\t')+'\n')
    tokens=[]
    for line in lines:
        tokens_temp=scan_line(line)
        tokens+=tokens_temp
        global CURRENT_LINE
        CURRENT_LINE+=1
    return tokens

def find_symbol(name, function):#根据所在函数及标识符，找到符号表中的符号
    for item in SYMBOL_TABLE:
        if item.name==name and item.function == function:
            return item
    return None

def update_symbol_table(symbol):#更新或者插入符号表
    global SYMBOL_TABLE
    for item in SYMBOL_TABLE:
        if item.name == symbol.name and item.function == symbol.function:
            SYMBOL_TABLE.remove(item)
            break
    SYMBOL_TABLE.append(symbol)

def find_function_by_name(name):#根据函数名找到函数表中的函数
    for item in FUNCTION_TABLE:
        if item.name==name:
            return item
    return None

def update_function_table(symbol):#更新或者插入函数表
    global FUNCTION_TABLE
    for item in FUNCTION_TABLE:
        if item.name == symbol.name:
            FUNCTION_TABLE.remove(item)
            break
    FUNCTION_TABLE.append(symbol)

def read_grammer_from_plain(path):#从txt读取LR(1)文法，已废弃
    global PRODUCTION_GROUP
    global TERMINAL_SYMBOL_GROUP
    global NONE_TERMINAL_SYMBOL_GROUP
    global START_PRODUCTION
    type = [
        'seperator', 'operator', 'identifier', 'STRING', 'CHAR', 'INT', 'FLOAT'
    ]
    regexs = [
        '{|}|[|]|(|)|,|;|.|?|:'  # 界符
        , '++|+|>>=|<<=|>>|<<|--|-|+=|-=|*|*=|%|%=|->|||||||=|/|/=|>|<|>=|<=|==|!=|^=|=|!|~|&&|&|&='  # 操作符
    ]
    NONE_TERMINAL_SYMBOL_GROUP.append('S')
    TERMINAL_SYMBOL_GROUP.append({'class': 'T', 'type': '#'})
    START_PRODUCTION = Production('S', [{'class': 'NT', 'type': 'start'}], 1, terminals=['#'])
    PRODUCTION_GROUP.append(START_PRODUCTION)
    blocks=open(path).read().split('\n\n')
    NONE_TERMINAL_SYMBOL_GROUP=[x.split('\n')[0] for x in blocks]
    for block in blocks:
        lines=block.split('\n')
        left=lines[0]
        expressions=[x.strip(' ')[1:] for x in lines[1:-1]]
        for expression in expressions:
            right=[]
            items=expression.strip(' ').split(' ')
            for item in items:
                data={}
                match=re.match("\'(.+?)\'",item)
                if match:#界符或者操作符
                    for i in range(2):
                        if match.groups()[0] in regexs[i]:
                            data={'class':'T','name':type[i],'type':match.groups()[0]}
                            break
                    if data=={}:
                        data = {'class': 'T', 'type': '$'}
                elif item in type and item !='operator':#基本类型
                    data ={'class':'T','name': item, 'type': item.upper()}
                elif item in reserved.keys():#保留字
                    data ={'class':'T','name': item, 'type': item}
                else:#非终结符
                     data ={'class':'NT','type':item}
                right.append(data)
                if not data in TERMINAL_SYMBOL_GROUP and data['class']!= 'NT':
                    TERMINAL_SYMBOL_GROUP.append(data)
            production_temp=Production(left, right, terminals=['#'])
            PRODUCTION_GROUP.append(production_temp)
    return

def read_grammer_from_json(path):#从json读取LR(1)文法产生式
    global PRODUCTION_GROUP
    global TERMINAL_SYMBOL_GROUP
    global NONE_TERMINAL_SYMBOL_GROUP
    global START_PRODUCTION
    TERMINAL_SYMBOL_GROUP.append({'class': 'T', 'type': '#'})
    START_PRODUCTION = Production('S', [{'class': 'NT', 'type': 'start'}], 1, terminals=['#'])
    PRODUCTION_GROUP.append(START_PRODUCTION)
    fd=io.open(path,"r", encoding="utf-8")
    data=fd.read()
    grammer=json.loads(data)
    for none_terminal in grammer:
        if none_terminal not in NONE_TERMINAL_SYMBOL_GROUP:
            NONE_TERMINAL_SYMBOL_GROUP.append(none_terminal)
        group=grammer[none_terminal]
        for expressions in group:
            production_temp=Production(none_terminal,expressions, terminals=['#'])
            PRODUCTION_GROUP.append(production_temp)
            for item in expressions:
                if item['class'] != 'NT':
                    if not item in TERMINAL_SYMBOL_GROUP:
                        TERMINAL_SYMBOL_GROUP.append(item)


def print_grammer(PRODUCTION_GROUP):#打印读取的文法
    for production in PRODUCTION_GROUP:
        print(production.to_string_compact())

def add_dot_to_productions(production):#对产生式加点
    result=[]
    if len(production.right)==1 and production.right[0]['type']== '$':
        result.append(Production(production.left, production.right, 1))
    else:
        productions_temp=[Production(production.left, production.right, i + 1)
              for i in range(len(production.right) + 1)]
        for item in productions_temp:
            result.append(item)
    return result

def generate_doted_productions():#获得所有加点的产生式
    global PRODUCTION_GROUP_DOTED
    for production in PRODUCTION_GROUP:
        for item in add_dot_to_productions(production):
            PRODUCTION_GROUP_DOTED.append(item)

def find_production(none_terminal):#在所有加点的产生式中，找到其中左侧非终结符为NT的
    result=[]
    for production in PRODUCTION_GROUP_DOTED:
        if production.left==none_terminal:
            result.append(production)
    return result

def get_closure(productions):#求一个项目集的CLOSURE
    def expand_production(production):
        data=[]
        right = production.right
        position = production.position
        terminals = production.terminals
        def get_first_set_final(node):
            if node['class'] == 'NT':
                return FIRST[next['type']]
            else:
                return get_first_set(next['type'])
        if position < len(right) + 1 and right[position - 1]['class'] == 'NT':
            first=[]
            flag=True
            for i in range(position, len(right)):
                next=right[i]
                first_set=copy.deepcopy(get_first_set_final(next))
                terminal_end={'class':'T','type':'$'}
                if terminal_end in first_set:
                    first_set.remove(terminal_end)
                    for item in first_set:
                        if not item in first:
                            first.append(item)
                else:
                    for item in first_set:
                        if not item in first:
                            first.append(item)
                    flag =False
                    break
            if flag:
                for item in terminals:
                    if not item in first:
                        first.append({'class':'T','type':item})
            productions = find_production(right[position - 1]['type'])
            for item in productions:
                if item.position == 1:
                    temp = copy.deepcopy(item)
                    temp.terminals =[item['type'] for item in first]
                    data.append(temp)
        return data
    productions_string_group=set(production.to_string() for production in productions)
    result=[production for production in productions]
    procession=[production for production in productions]
    while len(procession)>0:
        production=procession.pop()
        data=expand_production(production)
        for item in data:
            if item.to_string() not in productions_string_group:
                result.append(item)
                productions_string_group.add(item.to_string())
                procession.append(item)
    return result

def get_go(State, item):#求一个项目集对于item的GO
    params=[]
    for production in State.productions:
        expressions=production.right
        position=production.position
        if position<len(expressions)+1:
            node=expressions[position-1]
            if node['type']=='$' and len(expressions)==1:
                continue
            if node==item and production.next_doted_production() not in params:
                params.append(production.next_doted_production())
    return get_closure(params)

def get_first_set(symbol):#初步获取First集
    global FIRST
    result=[]
    productions=[production for production in PRODUCTION_GROUP if production.left == symbol]
    if len(productions)==0:
        return [{'class':'T','type':symbol}]
    terminal_end={'class':'T','type':'$'}
    for production in productions:
        expressions=production.right
        if expressions==[terminal_end] and terminal_end not in result:
            result.append(terminal_end)
        else:
            count = len(expressions)
            if expressions[0]['class']=='T' and expressions[0] not in result:
                result.append(expressions[0])
                continue
            else:
                if expressions[0]['type']!=symbol:
                    temp_first=expressions[0]
                    if temp_first not in result:
                        result.append(temp_first)
            if count>1:
                previous=expressions[0]
                for i in range(1,count):
                    if previous['type']!=symbol:
                        if not terminal_end in get_first_set(previous['type']):
                            break
                        else:
                            if expressions[i]['type']!=symbol:
                                temp_first = get_first_set(expressions[i]['type'])
                                if temp_first not in result:
                                    result.append(temp_first[0])
                                previous=expressions[i]
    FIRST[symbol]=result
    return result

def make_up_first():#补全Fisrt集
    def is_first_set_complete(key):
        first = FIRST[key]
        for item in first:
            if item['class'] == 'NT':
                return False
        return True
    global FIRST
    procession =FIRST.keys()
    while len(procession)>0:
        for key in procession:
            first = FIRST[key]
            for item in first:
                if item['class'] == 'NT':
                    if is_first_set_complete(item['type']):
                        for value in FIRST[item['type']]:
                            if value not in first:
                                first.append(value)
                        first.remove(item)
            if is_first_set_complete(key):
                procession.remove(key)
    return

def generate_first():#产生First集
    for none_terminal in NONE_TERMINAL_SYMBOL_GROUP:
        get_first_set(none_terminal)
    make_up_first()
    return

def generate_dfa():#构造LR(1)项目集规范族的DFA
    global DFA
    def merge(productions):
        result=[]
        table={}
        reversed={}
        for production in productions:
            production_temp=Production(production.left,production.right,production.position)
            teiminals = production.terminals
            if not production_temp.to_string() in table:
                table[production_temp.to_string()]=teiminals
                reversed[production_temp.to_string()]=production_temp
            else:
                for teiminal in teiminals:
                    table[production_temp.to_string()].append(teiminal)
        for key in table:
            production_temp=reversed[key]
            production_temp.terminals=table[key]
            result.append(production_temp)
        return result
    state_table={}
    tranfer=[]
    current_state=0
    states=[]
    procession=[]
    state_top=State('I'+str(current_state))
    state_top.productions=get_closure([START_PRODUCTION])
    state_table[state_top.name]=state_top.to_string()
    procession.append(state_top)
    DFA.add_state(state_top)
    states.append(state_top)
    current_state+=1
    while len(procession)>0:
        state_top=procession.pop(0)
        items=state_top.get_item()
        for item in items:
            state_temp=State('I'+str(current_state))
            state_temp.productions = merge(get_go(state_top, item))
            state_string=state_temp.to_string()
            if state_string=='':
                continue
            if state_string not in state_table.values():
                states.append(state_temp)
                state_table[state_temp.name] = state_string
                DFA.add_state(state_temp)
                DFA.add_edge(state_top, item, state_temp)
                tranfer.append((state_top.name,item['type'],state_temp.name))
                procession.append(state_temp)
                current_state += 1
            else:
                for state in states:
                    if state_table[state.name] == state_string:
                        DFA.add_edge(state_top, item, state)
                        tranfer.append((state_top.name, item['type'], state.name))
                        break
    return

def search_go_to_state(state, target):#查找GO(I,X)所到达的项目集
    for tuple in DFA.edge:
        state_from, item, state_to = tuple
        if (state_from,item)==(state, target):
            return state_to
    return

def generate_table():#生成LR(1)分析表
    global ACTION
    global GOTO
    global STATE_INDEX_TABLE
    global TERMINAL_INDEX_TABLE
    global NONE_TERMINAL_INDEX_TABLE
    global REDUCE
    global SHIFT
    states=DFA.state
    edges=DFA.edge
    production_string_group =copy.deepcopy(PRODUCTION_GROUP)
    production_string_group[0].position=0
    production_string_group=[production.to_string() for production in production_string_group]
    STATE_INDEX_TABLE = {states[i].name:i for i in range(len(states))}
    TERMINAL_INDEX_TABLE = {TERMINAL_SYMBOL_GROUP[i]["type"]:i for i in range(len(TERMINAL_SYMBOL_GROUP))}
    NONE_TERMINAL_INDEX_TABLE = {NONE_TERMINAL_SYMBOL_GROUP[i]:i for i in range(len(NONE_TERMINAL_SYMBOL_GROUP))}
    ACTION=[[" " for x in range(len(TERMINAL_SYMBOL_GROUP))] for y in range(len(states))]
    GOTO=[[" " for x in range(len(NONE_TERMINAL_SYMBOL_GROUP))] for y in range(len(states))]
    for state in states:
        x = STATE_INDEX_TABLE[state.name]
        production_end = copy.deepcopy(START_PRODUCTION)
        production_end.position += 1
        lable_group=[production.to_string() for production in state.productions]
        if production_end.to_string() in lable_group:
            y = TERMINAL_INDEX_TABLE["#"]
            ACTION[x][y] = 'acc'
            continue
        for production in state.productions:
            expressions = production.right
            position = production.position
            if position < len(expressions) + 1:
                node = expressions[position - 1]
                if node['class'] == 'T':
                    y = TERMINAL_INDEX_TABLE[node["type"]]
                    state_to = search_go_to_state(state, node)
                    if node['type'] != '$':
                        table_item_name='s'+state_to.name[1:]
                        if ACTION[x][y] != "" and ACTION[x][y] != table_item_name:
                            pass
                        ACTION[x][y] = table_item_name
                        production_temp = copy.deepcopy(production)
                        production_temp.position = 0
                        production_temp.terminals = ('#')
                        SHIFT[table_item_name] = production_temp
                    else:
                        for i in range(len(production.terminals)):
                            y = TERMINAL_INDEX_TABLE[production.terminals[i]]
                            production_temp = copy.deepcopy(production)
                            production_temp.position = 0
                            production_temp.terminals = ('#')
                            table_item_name = 'r' + str(production_string_group.index(production_temp.to_string()))
                            if ACTION[x][y] != "" and ACTION[x][y] != table_item_name:
                                pass
                            ACTION[x][y] = table_item_name
                            REDUCE[table_item_name] = production_temp
            elif position == len(expressions) + 1:
                for i in range(len(production.terminals)):
                    y = TERMINAL_INDEX_TABLE[production.terminals[i]]
                    production_temp=copy.deepcopy(production)
                    production_temp.position=0
                    production_temp.terminals=('#')
                    table_item_name= 'r'+str(production_string_group.index(production_temp.to_string()))
                    if ACTION[x][y]!="" and ACTION[x][y]!=table_item_name:
                        pass
                    ACTION[x][y] =table_item_name
                    REDUCE[table_item_name] = production_temp
    for tuple in edges:
        state_from,item,state_to=tuple
        if item['class']=='NT':
            x= STATE_INDEX_TABLE[state_from.name]
            y= NONE_TERMINAL_INDEX_TABLE[item['type']]
            if GOTO[x][y] != "" and GOTO[x][y] != state_to.name:
                pass
            GOTO[x][y]=state_to.name
    return

def write_to_table():#将LR(1)分析表写入文件
    title=[""]
    for i in range(len(TERMINAL_SYMBOL_GROUP)):
        title.append(TERMINAL_SYMBOL_GROUP[i]['type'])
    for i in range(len(NONE_TERMINAL_SYMBOL_GROUP)):
        title.append(NONE_TERMINAL_SYMBOL_GROUP[i])
    x = [title]
    for i in range(len(DFA.state)):
        row=[DFA.state[i].name]
        for j in range(len(TERMINAL_SYMBOL_GROUP)):
            row.append(ACTION[i][j])
        for j in range(len(NONE_TERMINAL_SYMBOL_GROUP)):
            row.append(GOTO[i][j])
        x.append(row)
    with open(os.path.join(SOURCE_PATH, NAME_LR1), 'w') as fd:
        for row in x:
            for colum in row:
                fd.write(colum+'\t')
            fd.write('\n')
    return

def add_table_colum(operation, action, state):
    global RECORD_TABLE
    global CURRENT_STEP
    CURRENT_STEP += 1
    op_stack_column = ""
    tokens_column = ""
    if len([x['type'] for x in OP_STACK]) > 5:
        op_stack_column = "...... "
    op_stack_column += " ".join([x['type'] for x in OP_STACK][-5:])
    tokens_column += " ".join([x['type'] for x in TOKENS][:5])
    if len([x['type'] for x in TOKENS]) > 5:
        tokens_column += " ......"
    state_stack_column = " ".join([x.name for x in STATE_STACK])
    row = [str(CURRENT_STEP), op_stack_column, tokens_column, operation, state_stack_column, action, state]
    RECORD_TABLE.append(row)
    return

def start_analyse():#进行语法分析
    global OP_STACK
    global STATE_STACK
    global CURRENT_PRODUCTION
    global RECORD_TABLE
    global TOKENS
    title=["步骤","当前栈","输入串","动作","状态栈","ACTION","GOTO"]
    RECORD_TABLE = [title]
    def find_state_by_name(name):
        for state in DFA.state:
            if state.name==name:
                return state
    terminal_end={'class': 'T', 'type': '#'}
    OP_STACK=[terminal_end]
    STATE_STACK=[DFA.state[0]]
    while True:
        current_state=STATE_STACK[-1]
        if len(TOKENS)==0:
            token = terminal_end
        else:
            token = TOKENS[0]
        x = STATE_INDEX_TABLE[current_state.name]
        y = TERMINAL_INDEX_TABLE[token['type']]
        action=ACTION[x][y]
        if action==' ':
            exit(1)
        if action=='acc':
            operation = "accept"
            add_table_colum(operation, action, "")
            with open(os.path.join(SOURCE_PATH , NAME_ANALYSIS), 'w') as fd:
                for row in RECORD_TABLE:
                    for colum in row:
                        fd.write(colum + '\t')
                    fd.write('\n')
            break
        elif action[0]=='s':
            next_state=find_state_by_name('I'+action[1:])
            STATE_STACK.append(next_state)
            token_temp =TOKENS.pop(0)
            OP_STACK.append(token_temp)
            operation = "shift"
            add_table_colum(operation, action, "")
        elif action[0]=='r':
            CURRENT_PRODUCTION=REDUCE[action]
            semantic_analysis()
            count=len(CURRENT_PRODUCTION.right)
            if count==1 and CURRENT_PRODUCTION.right[0]['type'] == '$':
                symbol_destination = {'class': 'NT', 'type': CURRENT_PRODUCTION.left}
                current_state = STATE_STACK[-1]
                temp_state=search_go_to_state(current_state, symbol_destination)
                STATE_STACK.append(search_go_to_state(current_state, symbol_destination))
                OP_STACK.append(symbol_destination)
                production_temp = copy.deepcopy(CURRENT_PRODUCTION)
                production_temp.position = 0
                operation = "reduce({})".format(production_temp.to_string())
                add_table_colum(operation, action, temp_state.name)
                continue
            for i in range(count):
                item=CURRENT_PRODUCTION.right[count - i - 1]
                back = OP_STACK[-1]
                if item['class'] != back['class'] and item['type'] != back['type']:
                    print("error in parser place row:{},colum{}".format(token['row'],token['colum']))
                    exit(-1)
                else:
                    OP_STACK.pop(-1)
                    STATE_STACK.pop(-1)
            current_state = STATE_STACK[-1]
            none_terminal=CURRENT_PRODUCTION.left
            x = STATE_INDEX_TABLE[current_state.name]
            y = NONE_TERMINAL_INDEX_TABLE[none_terminal]
            next_state=find_state_by_name(GOTO[x][y])
            STATE_STACK.append(next_state)
            OP_STACK.append({'class': 'NT', 'type': none_terminal})
            production_temp = copy.deepcopy(CURRENT_PRODUCTION)
            production_temp.position = 0
            operation = "reduce({})".format(production_temp.to_string())
            add_table_colum(operation, action, next_state.name)
    return

def draw_graph():
    class Graph():
        def __init__(self):
            self.edges = []

        def add_edge(self, edge):
            self.edges.append(edge)

        def to_string(self):
            result = "digraph  {\n"
            for edge in self.edges:
                result += "\t{} -> {}\t".format(edge[0], edge[1])
                result += "[constraint = True,\n\t\tlabel = \"{}\",\n\t\tlabelfloat = True];\n".format(edge[2])
            result += "}"
            return result

    graph_view = Graph()
    for tuple in DFA.state:
        state_from,item,state_to=tuple
        graph_view.add_edge((state_from.name,state_to.name,item['type']))
    with open("test.dot","w") as f:
        f.write(graph_view.to_string())
    os.system("dot -Tpng test.dot -o test.png")
    return

def get_new_label():#生成一个新的lable
    global CURRENT_LABLE
    CURRENT_LABLE+=1
    return "l"+str(CURRENT_LABLE)

def get_new_function_lable():#生成一个新的函数lable
    global CURRENT_FUNCTION
    CURRENT_FUNCTION+=1
    return "f"+str(CURRENT_FUNCTION)

def get_new_temp():#生成一个新的中间变量lable
    global CURRENT_TEMP
    CURRENT_TEMP+=1
    return "t"+str(CURRENT_TEMP)

def semantic_analysis():#语义分析子程序
    global CURRENT_OFFSET
    global CURRENT_FUNCTION_SYMBOL
    none_terminal=CURRENT_PRODUCTION.left
    expressions=CURRENT_PRODUCTION.right
    if none_terminal=='operator':
        node_new=Node()
        node_new.name= 'operator'
        node_new.type=''
        for i in range(len(expressions)):
            token = OP_STACK[-(len(expressions) - i)]
            node_new.type += token['type']
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='assignment_operator':
        node_new=Node()
        node_new.name= 'assignment_operator'
        node_new.type=[]
        for i in range(len(expressions)):
            node_new.type.append(expressions[i]['type'])
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='type_specifier':
        node_new=Node()
        node_new.name= 'type_specifier'
        node_new.type=expressions[0]['type']
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='primary_expression':
        node_new=Node()
        if expressions[0]['type']=='IDENTIFIER':
            node_new.data=OP_STACK[-1]['data']
            node_temp=find_symbol(node_new.data, CURRENT_FUNCTION_SYMBOL.lable)
            node_new.place=node_temp.place
            node_new.type=node_temp.type
        elif expressions[0]['type']=='number':
            node_new.data = OP_STACK[-1]['data']
            node_new.type=OP_STACK[-1]['name'].lower()
        elif expressions[1]['type']=='expression':
            node_new=copy.deepcopy(SEMANTIC_STACK.pop(-1))
        node_new.name= 'primary_expression'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='arithmetic_expression':
        node_new=Node()
        node_new.name= 'arithmetic_expression'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=copy.deepcopy(SEMANTIC_STACK.pop(-1))
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='constant_expression':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        node_new.name= 'constant_expression'
        if len(node_new.stack)==1:
            node_new=copy.deepcopy(node_new.stack[0])
        else:
            node_left=node_new.stack.pop(0)
            while len(node_new.stack)>0:
                node_op=node_new.stack.pop(0)
                node_right=node_new.stack.pop(0)
                if node_left.place==None:
                    arg1=node_left.data
                else:
                    arg1 =node_left.place
                if node_right.place==None:
                    arg2=node_right.data
                else:
                    arg2 =node_right.place
                if len(node_left.code)>0:
                    for code in node_left.code:
                        node_new.code.append(code)
                if len(node_right.code)>0:
                    for code in node_right.code:
                        node_new.code.append(code)
                node_result = Node()
                node_result.name = 'primary_expression'
                node_result.place = get_new_temp()
                node_result.type = node_right.type
                code=(node_op.type,arg1,arg2,node_result.place)
                node_new.code.append(code)
                node_left=node_result
                node_new.type=node_right.type
            node_new.place=node_new.code[-1][3]
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='declaration_assign':
        node_new = Node()
        if len(expressions)==2:
            id=OP_STACK[-3]['data']
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.id=id
        else:
            id = OP_STACK[-1]['data']
            node_new.id = id
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='declaration_init':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'declaration_init'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='declaration_init_list':
        node_new = Node()
        node_new.name = 'declaration_init_list'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='declaration':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        node_new.name= 'declaration'
        type=SEMANTIC_STACK.pop(-1).type
        for node in node_new.stack:
            symbol = find_symbol(node.id, CURRENT_FUNCTION_SYMBOL.lable)
            if symbol!=None and symbol.function==CURRENT_FUNCTION_SYMBOL.lable:
                token = TOKENS[0]
                print("multiple defination of {} in row{}".format(node.id,token['row']))
            else:
                symbol=Symbol()
            if node.place==None:
                symbol.name=node.id
                symbol.place=get_new_temp()
                symbol.type=type
                symbol.function=CURRENT_FUNCTION_SYMBOL.lable
                symbol.size = 4
                symbol.offset = CURRENT_OFFSET
                CURRENT_OFFSET += symbol.size
                update_symbol_table(symbol)
                if node.data!=None:
                    if(node.type!=type):
                        token = TOKENS[0]
                        print("type error in row{}".format(token['row']))
                    code=(':=',node.data,'_',symbol.place)
                    node_new.code.append(code)
            else:
                symbol.name=node.id
                symbol.place=node.place
                symbol.type=type
                symbol.function = CURRENT_FUNCTION_SYMBOL.lable
                symbol.size = 4
                symbol.offset = CURRENT_OFFSET
                CURRENT_OFFSET += symbol.size
                update_symbol_table(symbol)
                for code in node.code:
                    node_new.code.append(code)
        node_new.stack=[]
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='assignment_expression':
        node_new = SEMANTIC_STACK.pop(-1)
        node_op=SEMANTIC_STACK.pop(-1)
        id=OP_STACK[-3]['data']
        symbol = find_symbol(id, CURRENT_FUNCTION_SYMBOL.lable)
        if symbol == None:
            token = TOKENS[0]
            print("none defination of {} in row{}".format(id, token['row']))
            symbol = Symbol()
            symbol.place=get_new_temp()
            symbol.name=id
            symbol.type=node_new.type
            symbol.function = CURRENT_FUNCTION_SYMBOL.lable
            symbol.size=4
            symbol.offset=CURRENT_OFFSET
            CURRENT_OFFSET+=symbol.size
            update_symbol_table(symbol)
        if node_new.place==None:
            arg=node_new.data
        else:
            arg = node_new.place
        if len(node_op.type)==1:
            code=(':=',arg,'_',symbol.place)
            node_new.code.append(code)
        else:
            code=(node_op.type[0],symbol.place,arg,symbol.place)
            node_new.code.append(code)
        node_new.name = 'assignment_expression'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='assignment_expression_profix':
        node_new = Node()
        node_new.name = 'assignment_expression_profix'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='assignment_expression_list':
        node_new = Node()
        node_new.name = 'assignment_expression_list'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
            for node in node_new.stack:
                for code in reversed(node.code):
                    node_new.code.insert(0,code)
            node_new.stack=[]
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='expression':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'expression'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='expression_profix':
        node_new = Node()
        node_new.name = 'expression_profix'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='expression_list':
        node_new = Node()
        node_new.name = 'expression_list'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
            for node in reversed(node_new.stack):
                for code in node.code:
                    node_new.code.insert(0,code)
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='expression_statement':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'expression_statement'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='statement':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'statement'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='statement_list':
        node_new = Node()
        node_new.name = 'statement_list'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
            for node in node_new.stack:
                for code in reversed(node.code):
                    node_new.code.insert(0,code)
            node_new.stack=[]
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='compound_statement':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'compound_statement'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='jump_statement':
        node_new = Node()
        node_new.name = 'jump_statement'
        node_new.type=expressions[0]['type']
        if len(expressions)==3:
            node_temp=SEMANTIC_STACK.pop(-1)
            if node_temp.place!=None:
                node_result=node_temp.place
            else:
                node_result = node_temp.data
            node_new.code.append((':=', node_result, '_', 'v0'))
        node_new.code.append((node_new.type, '_', '_', '_'))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='selection_statement':
        node_new = Node()
        node_new.name = 'selection_statement'
        Node.true=get_new_label()
        Node.false=get_new_label()
        Node.end = get_new_label()
        FalseStmt=SEMANTIC_STACK.pop(-1)
        TrueStmt = SEMANTIC_STACK.pop(-1)
        expression=SEMANTIC_STACK.pop(-1)
        for code in  expression.code:
            node_new.code.append(code)
        node_new.code.append(('j>',expression.place,'0',Node.true))
        node_new.code.append(('j','_','_',Node.false))
        node_new.code.append((Node.true,':','_','_'))
        for code in TrueStmt.code:
            node_new.code.append(code)
        node_new.code.append(('j', '_', '_', Node.end))
        node_new.code.append((Node.false,':','_','_'))
        for code in FalseStmt.code:
            node_new.code.append(code)
        node_new.code.append((Node.end,':','_','_'))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='iteration_statement':
        node_new = Node()#生成新节点
        node_new.name = 'iteration_statement'
        node_new.true = get_new_label()#四个分支的入口
        node_new.false = get_new_label()
        node_new.begin = get_new_label()
        node_new.end = get_new_label()
        if expressions[0]['type']=='while':
            statement = SEMANTIC_STACK.pop(-1)#获得expression结点和statement结点
            expression=SEMANTIC_STACK.pop(-1)
            node_new.code.append((node_new.begin,':','_','_'))#begin入口
            for code in expression.code:#传递expression的中间代码
                node_new.code.append(code)
            node_new.code.append(('j>',expression.place,'0',node_new.true))#当expression的计算结果大于0时，跳转到true
            node_new.code.append(('j','_','_',node_new.false))#否则，跳转到false
            node_new.code.append((node_new.true,':','_','_'))#true入口
            for code in statement.code:#传递statement的中间代码
                if code[0]=='break':#当中间代码为break时，添加跳转到false的中间代码
                    node_new.code.append(('j','_','_',node_new.false))
                elif code[0]=='continue':#当中间代码为continue时，添加跳转到begin的中间代码
                    node_new.code.append(('j','_','_',node_new.begin))
                else:
                    node_new.code.append(code)
            node_new.code.append(('j', '_', '_', node_new.begin))#跳转回begin
            node_new.code.append((node_new.false,':','_','_'))#false入口
        elif expressions[0]['type']=='for':
            statement= SEMANTIC_STACK.pop(-1)
            assign= SEMANTIC_STACK.pop(-1)
            expression=SEMANTIC_STACK.pop(-1)
            Declaration=SEMANTIC_STACK.pop(-1)
            for code in  Declaration.code:
                node_new.code.append(code)
            node_new.code.append((node_new.begin,':','_','_'))
            for code in  expression.code:
                node_new.code.append(code)
            node_new.code.append(('j>',expression.place,'0',node_new.true))
            node_new.code.append(('j','_','_',node_new.false))
            node_new.code.append((node_new.true,':','_','_'))
            is_continue_existed=False
            for code in statement.code:
                if code[0]=='break':
                    node_new.code.append(('j','_','_',node_new.false))
                elif code[0]=='continue':
                    node_new.code.append(('j','_','_',node_new.end))
                    is_continue_existed=True
                else:
                    node_new.code.append(code)
            if is_continue_existed:
                node_new.code.append((node_new.end,':','_','_'))
            for code in assign.code:
                node_new.code.append(code)
            node_new.code.append(('j', '_', '_', node_new.begin))
            node_new.code.append((node_new.false,':','_','_'))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='function_declaration':
        node_new = Node()
        node_new.name = 'function_declaration'
        id = OP_STACK[-1]['data']
        node_new.id = id
        node_new.type=SEMANTIC_STACK.pop(-1).type
        node_new.place=get_new_temp()
        SEMANTIC_STACK.append(node_new)
    elif none_terminal=='function_declaration_suffix':
        node_new = Node()
        node_new.name = 'function_declaration_suffix'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal == 'function_declaration_list':
        node_new = Node()
        node_new.name = 'function_declaration_list'
        if len(expressions) == 1:
            node_new.stack = []
        else:
            node_new = SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal == 'function_definition':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'function_definition'
        function=FunctionSymbol()
        node_type=SEMANTIC_STACK.pop(-1)
        function.type=node_type.type
        function.name=OP_STACK[-4]['data']
        if function.name=='main':
            function.lable ='main'
        else:
            function.lable=get_new_function_lable()
        for arg in node_new.stack:
            symbol=Symbol()
            symbol.name=arg.id
            symbol.type=arg.type
            symbol.place=arg.place
            symbol.function = function.lable
            symbol.size=4
            symbol.offset=CURRENT_OFFSET
            CURRENT_OFFSET+=symbol.size
            update_symbol_table(symbol)
            function.params.append((arg.id,arg.type,arg.place))
        node_new.data=function.lable
        update_function_table(function)
        CURRENT_FUNCTION_SYMBOL=function
        SEMANTIC_STACK.append(node_new)
    elif none_terminal == 'function_implement':
        node_new = SEMANTIC_STACK.pop(-1)
        node_definition=SEMANTIC_STACK.pop(-1)
        node_new.name = 'function_implement'
        code_temp=[]
        code_temp.append((node_definition.data,':','_','_'))
        for node in node_definition.stack:
            code_temp.append(('pop','_',4*node_definition.stack.index(node),node.place))
        if len(node_definition.stack)>0:
            code_temp.append(('-', 'fp', 4*len(node_definition.stack), 'fp'))
        for code in reversed(code_temp):
            node_new.code.insert(0,code)
        code_end=node_new.code[-1]
        if code_end[0][0]=='l':
            lable=code_end[0]
            node_new.code.remove(code_end)
            for code in node_new.code:
                if code[3]==lable:
                    node_new.code.remove(code)
        SEMANTIC_STACK.append(node_new)
    elif none_terminal == 'function_expression':
        function = find_function_by_name(OP_STACK[-4]['data'])
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'function_expression'
        code_temp=[]
        symbol_temp_list = copy.deepcopy(CURRENT_FUNCTION_SYMBOL.params)
        code_temp.append(('-', 'sp', 4 * len(symbol_temp_list)+4, 'sp'))
        code_temp.append(('store', '_', 4 * len(symbol_temp_list), 'ra'))
        for symbol in symbol_temp_list:
            code_temp.append(('store','_',4 * symbol_temp_list.index(symbol),symbol[2]))
        for code in reversed(code_temp):
            node_new.code.insert(0,code)

        if len(function.params)>0:
            node_new.code.append(('+', 'fp', 4*len(function.params), 'fp'))
        for node in node_new.stack:
            if node.place!=None:
                node_result=node.place
            else:
                node_result = node.data
            node_new.code.append(('push','_',4*node_new.stack.index(node),node_result))
        node_new.code.append(('call', '_', '_', function.lable))

        symbol_temp_list.reverse()
        for symbol in symbol_temp_list:
            node_new.code.append(('load', '_', 4 * symbol_temp_list.index(symbol), symbol[2]))
        node_new.code.append(('load', '_', 4 * len(symbol_temp_list), 'ra'))
        node_new.code.append(('+', 'sp', 4 * len(CURRENT_FUNCTION_SYMBOL.params) + 4, 'sp'))

        node_new.place=get_new_temp()
        node_new.code.append((':=', 'v0', '_', node_new.place))
        SEMANTIC_STACK.append(node_new)
    elif none_terminal =='external_declaration':
        node_new = SEMANTIC_STACK.pop(-1)
        node_new.name = 'external_declaration'
        SEMANTIC_STACK.append(node_new)
    elif none_terminal =='start':
        node_new = Node()
        node_new.name = 'start'
        if len(expressions)==1:
            node_new.stack=[]
        else:
            node_new=SEMANTIC_STACK.pop(-1)
            node_new.stack.insert(0, SEMANTIC_STACK.pop(-1))
            for node in node_new.stack:
                for code in reversed(node.code):
                    node_new.code.insert(0,code)
            node_new.stack=[]
        SEMANTIC_STACK.append(node_new)
    return

def write_intermediate_code():#将中间代码写入文件
    fd=open(os.path.join(SOURCE_PATH,NAME_INTERMEDIATE_CODE), 'w')
    for code in INTERMEDIATE_CODE:
        if code[0]==':=':
            fd.write('{}={}'.format(code[3],code[1]))
        elif code[1]==':':
            if code[0][0]=='f' or code[0]=='main':
                fd.write('\n')
            fd.write('{}:'.format(code[0]))
        elif code[0]=='call' or code[0]=='push' or code[0]=='pop'or code[0]=='store' or code[0]=='load' or code[0]=='j':
            fd.write('{}  {}'.format(code[0], code[3]))
        elif code[0]=='j>':
            fd.write('j>0 {} {}'.format(code[1], code[3]))
        elif code[0]=='return':
            fd.write('return')
        else:
            fd.write('{}={}{}{}'.format(code[3], code[1], code[0], code[2]))
        fd.write('\n')
    fd.close()

def get_register(identifier,codes):#为中间变量申请一个寄存器
    global MIPS_CODE
    global REGISTER_TABLE
    if str(identifier)[0]!= 't':
        return identifier
    if identifier in TEMP_VALUE_STATUS:
        if TEMP_VALUE_STATUS[identifier]== 'reg':
            for key in REGISTER_TABLE:
                if REGISTER_TABLE[key]==identifier:
                    return key
    while True:
        for key in REGISTER_TABLE:
            if REGISTER_TABLE[key]== '':
                REGISTER_TABLE[key] =identifier
                TEMP_VALUE_STATUS[identifier]= 'reg'
                return key
        free_register(codes)

def free_register(codes):#释放寄存器占用
    global REGISTER_TABLE
    registers_used=REGISTER_TABLE.values()
    if '' in registers_used:
        registers_used.remove('')
    data={}
    for code in codes:
        for item in code:
            temp=str(item)
            if temp[0]=='t':
                if temp in registers_used:
                    if temp in data.keys():
                        data[temp]+=1
                    else:
                        data[temp] =1
    flag=False
    for item in registers_used:
        if item not in data:
            for key in REGISTER_TABLE.keys():
                if REGISTER_TABLE[key]==item:
                    REGISTER_TABLE[key]= ''
                    TEMP_VALUE_STATUS[item] = 'memory'
                    flag=True
    if flag:
        return
    sorted(data.items(),key=lambda x:x[1])
    freed=data.keys()[0]
    for key in REGISTER_TABLE:
        if REGISTER_TABLE[key]==freed:
            for item in SYMBOL_TABLE:
                if item.place==freed:
                    MIPS_CODE.append('addi $at,$zero,0x{}'.format(DATA_SEGMENT))
                    MIPS_CODE.append('sw {},{}($at)'.format(key, item.offset))
                    REGISTER_TABLE[key] = ''
                    TEMP_VALUE_STATUS[freed]= 'memory'
                    return

def generate_mips():#翻译中间代码为MIPS
    global TEMP_VALUE_STATUS
    code_remain=copy.deepcopy(INTERMEDIATE_CODE)
    TEMP_VALUE_STATUS={x.place: 'memory' for x in SYMBOL_TABLE}
    MIPS_CODE.append("addiu $sp,$zero,0x{}".format(DATA_SEGMENT + STACK_OFFSET))
    MIPS_CODE.append("or $fp,$sp,$zero")
    while len(code_remain)>0:
        intermediate_code=code_remain.pop(0)
        code=[]
        for item in intermediate_code:
            if item=='v0':
                code.append('$v0')
            else:
                code.append(item)
        if code[0] == ':=':
            arg1=get_register(code[3], code_remain)
            arg3=get_register(code[1], code_remain)
            MIPS_CODE.append('add {},$zero,{}'.format(arg1, arg3))
        elif code[1] == ':':
            if code[0][0]=='f':
                MIPS_CODE.append('')
            MIPS_CODE.append('{}:'.format(code[0]))
        elif code[0] == 'call':
            MIPS_CODE.append('jal  {}'.format(code[3]))
        elif code[0] == 'push':
            if code[3]=='ra':
                MIPS_CODE.append('sw $ra,{}($fp)'.format(code[2]))
            else:
                register=get_register(code[3], code_remain)
                if str(register)[0] != '$':
                    MIPS_CODE.append("add $a0,$zero,{}".format(register))
                    register = '$a0'
                MIPS_CODE.append('sw {},{}($fp)'.format(register, code[2]))
        elif code[0] == 'pop':
            if code[3]=='ra':
                MIPS_CODE.append('lw $ra,{}($fp)'.format(code[2]))
            else:
                register = get_register(code[3], code_remain)
                MIPS_CODE.append('lw {},{}($fp)'.format(register, code[2]))
        elif code[0] == 'store':
            if code[3]=='ra':
                MIPS_CODE.append('sw $ra,{}($sp)'.format(code[2]))
            else:
                register=get_register(code[3], code_remain)
                if str(register)[0] != '$':
                    MIPS_CODE.append("add $a0,$zero,{}".format(register))
                    register = '$a0'
                MIPS_CODE.append('sw {},{}($sp)'.format(register, code[2]))
        elif code[0] == 'load':
            if code[3]=='ra':
                MIPS_CODE.append('lw $ra,{}($sp)'.format(code[2]))
            else:
                register = get_register(code[3], code_remain)
                MIPS_CODE.append('lw {},{}($sp)'.format(register, code[2]))
        elif code[0] == 'j':
            MIPS_CODE.append('j {}'.format(code[3]))
        elif code[0] == 'j>':
            arg1=get_register(code[1], code_remain)
            MIPS_CODE.append('bgt {},$zero,{}'.format(arg1, code[3]))
        elif code[0] == 'return':
            MIPS_CODE.append('jr $ra')
        else:
            if code[0]=='+':
                if code[1]=='fp':
                    MIPS_CODE.append("add $fp,$fp,{}".format(code[2]))
                elif code[1]=='sp':
                    MIPS_CODE.append("add $sp,$sp,{}".format(code[2]))
                else:
                    arg1= get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0]!='$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    MIPS_CODE.append("add {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='-':
                if code[1]=='fp':
                    MIPS_CODE.append("sub $fp,$fp,{}".format(code[2]))
                elif code[1]=='sp':
                    MIPS_CODE.append("sub $sp,$sp,{}".format(code[2]))
                else:
                    arg1= get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0]!='$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("sub {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='*':
                    arg1= get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0]!='$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("mul {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='/':
                    arg1= get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0]!='$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("div {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='%':
                    arg1= get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0]!='$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("div {},{},{}".format(arg3, arg1, arg2))
                    MIPS_CODE.append("mfhi {}".format(arg3))
            elif code[0]=='<':
                    arg1= get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0]!='$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("slt {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='>':
                    arg1= get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0]!='$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("sgt {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='!=':
                    arg1 = get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0] != '$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("sne {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='==':
                    arg1 = get_register(code[1], code_remain)
                    arg2 = get_register(code[2], code_remain)
                    arg3 = get_register(code[3], code_remain)
                    if str(arg1)[0] != '$':
                        MIPS_CODE.append("add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        MIPS_CODE.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    MIPS_CODE.append("seq {},{},{}".format(arg3, arg1, arg2))
    return

if __name__=="__main__":
    read_grammer_from_json(os.path.join(SOURCE_PATH,NAME_GRAMMER_JSON))
    # read_grammer_from_plain(os.path.join(SOURCE_PATH,NAME_GRAMMER_PLAIN))
    generate_doted_productions()
    generate_first()
    DFA = DFA()
    generate_dfa()
    generate_table()
    write_to_table()
    TOKENS = generate_tokens(os.path.join(SOURCE_PATH, NAME_SOURCE_CODE))
    start_analyse()
    INTERMEDIATE_CODE = SEMANTIC_STACK[0].code
    INTERMEDIATE_CODE.insert(0, ('call', '_', '_', 'end'))
    INTERMEDIATE_CODE.insert(0, ('call', '_', '_', 'main'))
    write_intermediate_code()
    generate_mips()
    with open(os.path.join(SOURCE_PATH,NAME_ASM), 'w') as f:
        for code in MIPS_CODE:
            if code == 'main:':
                f.write('\n')
            f.write(code + '\n')
        f.write('end:')