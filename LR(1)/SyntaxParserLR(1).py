#coding:utf-8
from __future__ import print_function

import os
import re
import copy
from prettytable import *
from Definitions import *
from LexcialAnalyzer import *
regexs=[
    '{|}|[|]|(|)|,|;|.|?|:'#界符
    ,'++|+|>>=|<<=|>>|<<|--|-|+=|-=|*|*=|%|%=|->|||||||=|/|/=|>|<|>=|<=|==|!=|^=|=|!|~|&&|&|&='#操作符
]
class Production():
    def __init__(self, left, right, position=0, terminals=None):
        self.left=left
        self.right=right
        self.position=position
        self.terminals=terminals
    def Next(self):
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
            result += data['value']+' '
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
class State():
    def __init__(self,name):
        self.name=name
        self.productions=[]
        self.string=[]
    def to_string(self):
        for Production in self.productions:
            if Production.to_string() not in self.string:
                self.string.append(Production.to_string())
        return "\n".join(sorted(self.string))
    def get_item(self):
        result=[]
        for production in self.productions:
            expression = production.right
            position = production.position
            if position < len(expression) + 1:
                node = expression[position - 1]
                if node not in result:
                    result.append(node)
        return result
class DFA(object):
    def __init__(self):
        self.state=[]
        self.edge=[]
    def add_state(self, Ix):
        self.state.append(Ix)
    def add_edge(self, Ia, t, Ib):
        self.edge.append((Ia,t,Ib))
def ReadGrammer(file):
    global ProductionGroup
    global TerminalSymbolGroup
    global LeftGroup
    global StartProduction
    type = [
        'seperator', 'operator', 'id', 'STRING', 'CHAR', 'INT', 'FLOAT'
    ]
    LeftGroup.append('S')
    TerminalSymbolGroup.append({'class':'T', 'value': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'value': 'start'}],1, terminals=['#'])
    ProductionGroup.append(StartProduction)
    blocks=open(file).read().split('\n\n')
    LeftGroup=[x.split('\n')[0] for x in blocks]
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
                            data={'class':'T','type':type[i],'value':match.groups()[0]}
                            break
                    if data=={}:
                        data = {'class': 'T', 'value': '$'}
                elif item in type and item !='operator':#基本类型
                    data ={'class':'T','type': item, 'value': item.upper()}
                elif item in Reserved.keys():#保留字
                    data ={'class':'T','type': item, 'value': item}
                else:#非终结符
                     data ={'class':'NT','value':item}
                right.append(data)
                if not data in TerminalSymbolGroup and data['class']!='NT':
                    TerminalSymbolGroup.append(data)
            ProductionGroup.append(Production(left, right, terminals=['#']))
    return
def PrintGrammer(ProductionGroup):
    for Production in ProductionGroup:
        print(Production.to_string())
def AddDotToproductions(production):
    result=[]
    if len(production.right)==1 and production.right[0]['value']== '$':
        result.append(Production(production.left, production.right, 1))
    else:
        temp=[Production(production.left, production.right, i + 1)
              for i in range(len(production.right) + 1)]
        for item in temp:
            result.append(item)
    return result
def GenerateDotedproductions():
    global DotedProductionGroup
    for P in ProductionGroup:
        for item in AddDotToproductions(P):
            DotedProductionGroup.append(item)
def FindProduction(NT):
    result=[]
    for Production in DotedProductionGroup:
        if Production.left==NT:
            result.append(Production)
    return result
def CLOSURE(productions):
    def ExpandProduction(production):
        data=[]
        right = production.right
        position = production.position
        terminal = production.terminals
        def get_first_set(node):
            if node['class'] == 'NT':
                return FIRST[next['value']]
            else:
                return GetFirstSet(next['value'])
        if position < len(right) + 1 and right[position - 1]['class'] == 'NT':
            first=[]
            flag=True
            for i in range(position, len(right)):
                next=right[i]
                firstset=copy.deepcopy(get_first_set(next))
                eps={'class':'T','value':'$'}
                if eps in firstset:
                    firstset.remove(eps)
                    for item in firstset:
                        if not item in first:
                            first.append(item)
                else:
                    for item in firstset:
                        if not item in first:
                            first.append(item)
                    flag =False
                    break
            if flag:
                for item in terminal:
                    if not item in first:
                        first.append({'class':'T','value':item})
            productions = FindProduction(right[position - 1]['value'])
            for item in productions:
                if item.position == 1:
                    temp = copy.deepcopy(item)
                    temp.terminals =[item['value'] for item in first]
                    data.append(temp)
        return data
    cache=[p.to_string() for p in productions]
    result=[p for p in productions]
    procession=[p for p in productions]
    while len(procession)>0:
        production=procession.pop()
        data=ExpandProduction(production)
        for item in data:
            if item.to_string() not in cache:
                result.append(item)
                cache.append(item.to_string())
                procession.append(item)
    return result
def GO(I,item):
    params=[]
    for production in I.productions:
        expression=production.right
        position=production.position
        if position<len(expression)+1:
            node=expression[position-1]
            if node['value']=='$' and len(expression)==1:
                continue
            if node==item and production.Next() not in params:
                params.append(production.Next())
    return CLOSURE(params)
def GetFirstSet(symbol):
    global FIRST
    result=[]
    productions=[production for production in ProductionGroup if production.left == symbol]
    if len(productions)==0:
        return [{'class':'T','value':symbol}]
    end_symbol={'class':'T','value':'$'}
    for production in productions:
        right=production.right
        if right==[end_symbol] and end_symbol not in result:
            result.append(end_symbol)
        else:
            cnt = len(right)
            if right[0]['class']=='T' and right[0] not in result:
                result.append(right[0])
                continue
            else:
                if right[0]['value']!=symbol:
                    temp_first=right[0]
                    if temp_first not in result:
                        result.append(temp_first)
            if cnt>1:
                previous=right[0]
                for i in range(1,cnt):
                    if previous['value']!=symbol:
                        if not end_symbol in GetFirstSet(previous['value']):
                            break
                        else:
                            if right[i]['value']!=symbol:
                                temp_first = GetFirstSet(right[i]['value'])
                                if temp_first not in result:
                                    result.append(temp_first[0])
                                previous=right[i]
    FIRST[symbol]=result
    return result
def MakeUpFirst():
    def IsFirstSetComplete(key):
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
                    if IsFirstSetComplete(item['value']):
                        for value in FIRST[item['value']]:
                            if value not in first:
                                first.append(value)
                        first.remove(item)
            if IsFirstSetComplete(key):
                procession.remove(key)
    return
def GenerateFirst():
    for Nonterminal in LeftGroup:
        GetFirstSet(Nonterminal)
    MakeUpFirst()
    return
def GenerateDFA():
    global DFA
    def Merge(productions):
        result=[]
        table={}
        reversed={}
        for p in productions:
            temp=Production(p.left,p.right,p.position)
            teiminals = p.terminals
            if not temp.to_string() in table.keys():
                table[temp.to_string()]=teiminals
                reversed[temp.to_string()]=temp
            else:
                for t in teiminals:
                    table[temp.to_string()].append(t)
        for key in table.keys():
            temp=reversed[key]
            temp.terminals=table[key]
            result.append(temp)
        return result
    StateTable={}
    Tranfer=[]
    CurrentState=0
    States=[]
    Procession=[]
    I=State('I'+str(CurrentState))
    I.productions=CLOSURE([StartProduction])
    StateTable[I.name]=I.to_string()
    Procession.append(I)
    DFA.add_state(I)
    States.append(I)
    CurrentState+=1
    while len(Procession)>0:
        I=Procession.pop(0)
        items=I.get_item()
        for item in items:
            temp=State('I'+str(CurrentState))
            temp.productions = Merge(GO(I, item))
            string=temp.to_string()
            if string=='':
                continue
            if string not in StateTable.values():
                States.append(temp)
                StateTable[temp.name] = string
                DFA.add_state(temp)
                DFA.add_edge(I, item, temp)
                Tranfer.append((I.name,item['value'],temp.name))
                Procession.append(temp)
                CurrentState += 1
            else:
                for state in States:
                    if StateTable[state.name] == string:
                        DFA.add_edge(I, item, state)
                        Tranfer.append((I.name, item['value'], state.name))
                        break
    return
def SearchGoToState(I,target):
    for tuple in DFA.edge:
        From, item, To = tuple
        if (From,item)==(I,target):
            return To
    return
def GenerateTable():
    global ACTION
    global GOTO
    global StateIndexTable
    global TerminalIndexTable
    global NonterminalIndexTable
    global Reduce
    global Shift
    ProductionStringGroup =copy.deepcopy(ProductionGroup)
    ProductionStringGroup[0].position=0
    ProductionStringGroup=[p.to_string() for p in ProductionStringGroup]
    states=DFA.state
    edges=DFA.edge
    StateIndexTable = {states[i].name:i for i in range(len(states))}
    TerminalIndexTable = {TerminalSymbolGroup[i]["value"]:i for i in range(len(TerminalSymbolGroup))}
    NonterminalIndexTable = {LeftGroup[i]:i for i in range(len(LeftGroup))}
    ACTION=[["" for x in range(len(TerminalSymbolGroup))] for y in range(len(states))]
    GOTO=[["" for x in range(len(LeftGroup))] for y in range(len(states))]
    for state in states:
        x = StateIndexTable[state.name]
        EndProduction = copy.deepcopy(StartProduction)
        EndProduction.position += 1
        LableGroup=[p.to_string() for p in state.productions]
        if EndProduction.to_string() in LableGroup:
            y = TerminalIndexTable["#"]
            ACTION[x][y] = 'acc'
            continue
        for production in state.productions:
            expression = production.right
            position = production.position
            if position < len(expression) + 1:
                node = expression[position - 1]
                if node['class'] == 'T':
                    y = TerminalIndexTable[node["value"]]
                    To = SearchGoToState(state, node)
                    if node['value'] != '$':
                        index='s'+To.name[1:]
                        if ACTION[x][y] != "" and ACTION[x][y] != index:
                            print("{}包含shift-reduce冲突".format(state.name))
                            print(index, end='->')
                            print(ACTION[x][y])
                            print(state.to_string())
                            print('-------------')
                        ACTION[x][y] = index
                        temp = copy.deepcopy(production)
                        temp.position = 0
                        temp.terminals = ('#')
                        Shift[index] = temp
                    else:
                        for i in range(len(production.terminals)):
                            y = TerminalIndexTable[production.terminals[i]]
                            temp = copy.deepcopy(production)
                            temp.position = 0
                            temp.terminals = ('#')
                            index = 'r' + str(ProductionStringGroup.index(temp.to_string()))
                            if ACTION[x][y] != "" and ACTION[x][y] != index:
                                print("{}包含shift-reduce冲突".format(state.name))
                                print(index, end='->')
                                print(ACTION[x][y])
                                print(state.to_string())
                                print(temp.to_string())
                                print('-------------')
                            ACTION[x][y] = index
                            Reduce[index] = temp

            elif position == len(expression) + 1:
                for i in range(len(production.terminals)):
                    y = TerminalIndexTable[production.terminals[i]]
                    temp=copy.deepcopy(production)
                    temp.position=0
                    temp.terminals=('#')
                    index= 'r'+str(ProductionStringGroup.index(temp.to_string()))
                    if ACTION[x][y]!="" and ACTION[x][y]!=index:
                        print("{}包含shift-reduce冲突".format(state.name))
                        print(index,end='->')
                        print(ACTION[x][y])
                        print(state.to_string())
                        print(temp.to_string())
                        print('-------------')
                    ACTION[x][y] =index
                    Reduce[index] = temp
    for tuple in edges:
        From,item,To=tuple
        if item['class']=='NT':
            x= StateIndexTable[From.name]
            y= NonterminalIndexTable[item['value']]
            if GOTO[x][y] != "" and GOTO[x][y] != To.name:
                print(To.name,end='->')
                print(GOTO[x][y])
                print('-------------')
            GOTO[x][y]=To.name
    return
def PrintTable():
    title=[""]
    for i in range(len(TerminalSymbolGroup)):
        title.append(TerminalSymbolGroup[i]['value'])
    for i in range(len(LeftGroup)):
        title.append(LeftGroup[i])
    temp=title
    title.sort()
    x = PrettyTable(title)
    for i in range(len(DFA.state)):
        row=[DFA.state[i].name]
        for j in range(len(TerminalSymbolGroup)):
            row.append(ACTION[i][j])
        for j in range(len(LeftGroup)):
            row.append(GOTO[i][j])
        x.add_row(row)
    print(x)
    return
def MakeSyntacticAnalyse(Tokens):
    title=["步骤","当前栈","输入串","动作","状态栈","ACTION","GOTO"]
    step=0
    table = PrettyTable(title)
    def FindStateByName(name):
        for state in DFA.state:
            if state.name==name:
                return state
    EndSymbol={'class': 'T', 'value': '#'}
    OpStack=[EndSymbol]
    StateStack=[DFA.state[0]]
    while True:
        CurrentState=StateStack[-1]
        if len(Tokens)==0:
            Token = EndSymbol
        else:
            Token = Tokens[0]
        Token={'class':Token['class'],'value':Token['value']}
        x = StateIndexTable[CurrentState.name]
        y = TerminalIndexTable[Token['value']]
        Action=ACTION[x][y]
        if Action=='':
            pass
        if Action=='acc':
            step+=1
            OpStackColumn=""
            TokensColumn=""
            if len([x['value'] for x in OpStack])>5:
                OpStackColumn="...... "
            OpStackColumn+=" ".join([x['value'] for x in OpStack][-5:])
            TokensColumn+=" ".join([x['value'] for x in Tokens][:5])
            if len([x['value'] for x in Tokens]) > 5:
                TokensColumn += " ......"
            Operation="accept"
            StateStackColumn=" ".join([x.name for x in StateStack])
            row=[str(step),OpStackColumn,TokensColumn,Operation,StateStackColumn,Action,""]
            table.add_row(row)
            print(table)
            break
        elif Action[0]=='s':
            NextState=FindStateByName('I'+Action[1:])
            StateStack.append(NextState)
            Temp =Tokens.pop(0)
            Temp= {'class': Temp['class'], 'value': Temp['value']}
            OpStack.append(Temp)
            step += 1
            OpStackColumn=""
            TokensColumn=""
            if len([x['value'] for x in OpStack])>5:
                OpStackColumn="...... "
            OpStackColumn+=" ".join([x['value'] for x in OpStack][-5:])
            TokensColumn+=" ".join([x['value'] for x in Tokens][:5])
            if len([x['value'] for x in Tokens]) > 5:
                TokensColumn += " ......"
            Operation="shift"
            StateStackColumn=" ".join([x.name for x in StateStack])
            row=[str(step),OpStackColumn,TokensColumn,Operation,StateStackColumn,Action,""]
            table.add_row(row)
        elif Action[0]=='r':
            production=Reduce[Action]
            cnt=len(production.right)
            if cnt==1 and production.right[0]['value'] == '$':
                des = {'class': 'NT', 'value': production.left}
                CurrentState = StateStack[-1]
                StateStack.append(SearchGoToState(CurrentState, des))
                OpStack.append(des)
                continue
            for i in range(cnt):
                    item=production.right[cnt-i-1]
                    back = OpStack[-1]
                    if item['class'] != back['class'] and item['value'] != back['value']:
                        print("error")
                    else:
                        OpStack.pop(-1)
                        StateStack.pop(-1)
            CurrentState = StateStack[-1]
            NT=production.left
            x = StateIndexTable[CurrentState.name]
            y = NonterminalIndexTable[NT]
            NextState=FindStateByName(GOTO[x][y])
            StateStack.append(NextState)
            OpStack.append({'class': 'NT', 'value': NT})
            step += 1
            OpStackColumn=""
            TokensColumn=""
            if len([x['value'] for x in OpStack])>5:
                OpStackColumn="...... "
            OpStackColumn+=" ".join([x['value'] for x in OpStack][-5:])
            TokensColumn+=" ".join([x['value'] for x in Tokens][:5])
            if len([x['value'] for x in Tokens]) > 5:
                TokensColumn += " ......"
            temp=copy.deepcopy(production)
            temp.position=0
            Operation="reduce({})".format(temp.to_string())
            StateStackColumn=" ".join([x.name for x in StateStack])
            row=[str(step),OpStackColumn,TokensColumn,Operation,StateStackColumn,Action,NextState.name]
            table.add_row(row)
    return
def DrawGraph():
    class Graph(object):
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
    GraphView = Graph()
    for tuple in DFA.state:
        From,item,To=tuple
        GraphView.add_edge((From.name,To.name,item['value']))
    with open("temp.dot","w") as f:
        f.write(GraphView.to_string())
    os.system("dot -Tpng temp.dot -o temp.png")
    return
ProductionGroup=[]
DotedProductionGroup=[]
TerminalSymbolGroup=[]
LeftGroup=[]
StateIndexTable={}
TerminalIndexTable={}
NonterminalIndexTable={}
ACTION=[]
GOTO=[]
StartProduction=None
DFA=DFA()
Reduce={}
Shift={}
FIRST={}
FOLLOW={}
if __name__=='__main__':
    ReadGrammer("grammer.txt")
    GenerateDotedproductions()
    #PrintGrammer(ProductionGroup)
    GenerateFirst()
    GenerateDFA()
    #DrawGraph()
    GenerateTable()
    PrintTable()
    tokens=main('source.cc')
    MakeSyntacticAnalyse(tokens)