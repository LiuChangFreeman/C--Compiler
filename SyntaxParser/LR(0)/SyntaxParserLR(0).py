#coding:utf-8
from __future__ import print_function

import os
import re
import copy
from prettytable import *
from Definitions import *
regexs=[
    '{|}|[|]|(|)|,|;|.|?|:'#界符
    ,'++|+|>>=|<<=|>>|<<|--|-|+=|-=|*|*=|%|%=|->|||||||=|/|/=|>|<|>=|<=|==|!=|^=|=|!|~|&&|&|&='#操作符
]
class Production():
    def __init__(self,NonterminalSymbol,RightExpression,DotPosition=0):
        self.NonterminalSymbol=NonterminalSymbol
        self.RightExpression=RightExpression
        self.DotPosition=DotPosition
    def Next(self):
        return Production(self.NonterminalSymbol,
                          self.RightExpression,
                          self.DotPosition+1)
    def ToString(self):
        result=self.NonterminalSymbol+'->'
        position=1
        for data in self.RightExpression:
            if position==self.DotPosition:
                result += '●'
            result += data['type']+' '
            position += 1
        if position == self.DotPosition:
            result += '●'
        return result
class State():
    def __init__(self,name):
        self.name=name
        self.Productions=[]
        self.string=[]
    def AddProduction(self,P):
        self.Productions.append(P)
    def ToString(self):
        for Production in self.Productions:
            if Production.ToString() not in self.string:
                self.string.append(Production.ToString())
        return ";".join(sorted(self.string))
    def GetItem(self):
        result=[]
        for production in self.Productions:
            expression = production.RightExpression
            position = production.DotPosition
            if position < len(expression) + 1:
                node = expression[position - 1]
                if node not in result:
                    result.append(node)
        return result
class DFA(object):
    def __init__(self):
        self.state=[]
        self.edge=[]
    def AddState(self,Ix):
        self.state.append(Ix)
    def AddEdge(self,Ia,t,Ib):
        self.edge.append((Ia,t,Ib))
class Node(object):
    def __init__(self, value):
        self.childs = []
        self.parent = None
        self.value = value
    def addchild(self,value):
        self.childs.append(value)
    def setparent(self,value):
        self.parent=value
    def getdic(self):
        return self.value
    def traves(self):
        dic={}
        key=self.value.values()[0]
        dic[key]=[]
        for child in self.childs:
            dic[key].append(child.traves())
        return dic
def GenerateGrammer(file):
    global ProductionGroup
    global TerminalSymbolGroup
    global NonterminalSymbolGroup
    global StartProduction
    NonterminalSymbolGroup.append('S')
    TerminalSymbolGroup.append({'class':'T', 'type': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'type': 'fd'}],1)
    ProductionGroup.append(StartProduction)
    blocks=open(file).read().split('\n\n')
    Reflector={Reserved[x]:x for x in Reserved.keys()}
    NonterminalSymbolGroup=[x.split('\n')[0] for x in blocks]
    Compact = {}
    for lable in NonterminalSymbolGroup:
        code = ""
        codes = lable.split('_')
        for item in codes:
            code += item[0]
        if not code in Compact.values():
            Compact[lable] = code
        elif not code + 't' in Compact.values():
            Compact[lable] = code + 't'
        else:
            Compact[lable] = code + 'a'
    for block in blocks:
        lines=block.split('\n')
        NonterminalSymbol=lines[0]
        Expressions=[x.strip(' ')[1:] for x in lines[1:-1]]
        for expression in Expressions:
            RightExpression=[]
            items=expression.strip(' ').split(' ')
            for item in items:
                data={}
                match=re.match("\'(.+?)\'",item)
                if match:#界符或者操作符
                    for i in range(2):
                        if match.groups()[0] in regexs[i]:
                            data={'class':'T','name':type[i],'type':match.groups()[0]}
                            break
                elif item in type:#基本类型
                    data ={'class':'T','name': item, 'type': item.upper()}
                elif item in Reflector.keys():#保留字
                    data ={'class':'T','name': item, 'type': Reflector[item]}
                else:#非终结符
                    data ={'class':'NT','type':Compact[item]}
                RightExpression.append(data)
                if not data in TerminalSymbolGroup and data['class']!='NT':
                    TerminalSymbolGroup.append(data)
            ProductionGroup.append(Production(Compact[NonterminalSymbol], RightExpression))
    NonterminalSymbolGroup=Compact.values()
    return
def GenerateCompactGrammer(file):
    global ProductionGroup
    global TerminalSymbolGroup
    global NonterminalSymbolGroup
    global StartProduction
    NonterminalSymbolGroup.append('S')
    TerminalSymbolGroup.append({'class':'T','name': 'Acc', 'type': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'type': 'E'}],1)
    ProductionGroup.append(StartProduction)
    blocks=open(file).read().split('\n\n')
    NonterminalSymbolGroup=[x.split('\n')[0] for x in blocks]
    for block in blocks:
        lines=block.split('\n')
        NonterminalSymbol=lines[0]
        Expressions=[x.strip(' ')[1:] for x in lines[1:-1]]
        for expression in Expressions:
            RightExpression=[]
            items=expression.strip(' ').split(' ')
            for item in items:
                data={}
                match=re.match("\'(.+?)\'",item)
                if match:
                    data ={'class':'T', 'type': match.groups()[0]}
                else:#非终结符
                    data ={'class':'NT','type':item}
                RightExpression.append(data)
                if not data in TerminalSymbolGroup and data['class']!='NT':
                    TerminalSymbolGroup.append(data)
            ProductionGroup.append(Production(NonterminalSymbol, RightExpression))
    return
def PrintGrammer(ProductionGroup):
    for Production in ProductionGroup:
        print(Production.ToString())
def AddDot(P):
    result=[]
    temp=[Production(P.NonterminalSymbol,P.RightExpression,i+1)
          for i in range(len(P.RightExpression)+1)]
    for item in temp:
        result.append(item)
    return result
def GenerateDoted():
    global DotedProductionGroup
    for P in ProductionGroup:
        for item in AddDot(P):
            DotedProductionGroup.append(item)
def FindProduction(NT):
    result=[]
    for Production in DotedProductionGroup:
        if Production.NonterminalSymbol==NT:
            result.append(Production)
    return result
def CLOSURE(Productions):
    def expand(production):
        data=[]
        expression=production.RightExpression
        position=production.DotPosition
        if position<len(expression)+1:
            node=expression[position-1]
            if node['class']=='NT':
                productions=FindProduction(node['type'])
                for item in productions:
                    if item.DotPosition==1:
                        data.append(item)
        return data
    result=[p for p in Productions]
    procession=[p for p in Productions]
    while len(procession)>0:
        production=procession.pop()
        data=expand(production)
        for item in data:
            if item not in result:
                result.append(item)
                procession.append(item)
    return result
def GO(I,item):
    Params=[]
    for production in I.Productions:
        expression=production.RightExpression
        position=production.DotPosition
        if position<len(expression)+1:
            node=expression[position-1]
            if node==item and production.Next() not in Params:
                Params.append(production.Next())
    return CLOSURE(Params)
def GenerateDFA():
    global DFA
    StateTable={}
    Tranfer=[]
    CurrentState=0
    States=[]
    Procession=[]
    I=State('I'+str(CurrentState))
    I.Productions=CLOSURE([StartProduction])
    StateTable[I.name]=I.ToString()
    Procession.append(I)
    DFA.add_state(I)
    States.append(I)
    CurrentState+=1
    while len(Procession)>0:
        I=Procession.pop()
        Items=I.GetItem()
        for item in Items:
            temp=State('I'+str(CurrentState))
            temp.Productions= GO(I,item)
            string=temp.ToString()
            if string not in StateTable.values():
                States.append(temp)
                StateTable[temp.name] = string
                DFA.add_state(temp)
                DFA.add_edge(I, item, temp)
                Tranfer.append((I.name,item['type'],temp.name))
                Procession.append(temp)
                CurrentState += 1
            else:
                for state in States:
                    if StateTable[state.name] == string:
                        DFA.add_edge(I, item, state)
                        Tranfer.append((I.name, item['type'], state.name))
                        break
    return
def GenerateTable():
    def SearchGoToState(I,target):
        for tuple in DFA.edge:
            From, item, To = tuple
            if (From,item)==(I,target):
                return To
        return
    global ACTION
    global GOTO
    global StateIndexTable
    global TerminalIndexTable
    global NonterminalIndexTable
    global Reduce
    global Shift
    ProductionStringGroup =copy.deepcopy(ProductionGroup)
    ProductionStringGroup[0].DotPosition=0
    ProductionStringGroup=[p.ToString() for p in ProductionStringGroup]
    # for p in ProductionStringGroup:
    #     print(p)
    states=DFA.state
    edges=DFA.edge
    # for tuple in DFA.edge:
    #     From, item, To = tuple
    #     print(From.name+"+"+item['type']+"->"+To.name)
    StateIndexTable = {states[i].name:i for i in range(len(states))}
    TerminalIndexTable = {TerminalSymbolGroup[i]["type"]:i for i in range(len(TerminalSymbolGroup))}
    NonterminalIndexTable = {NonterminalSymbolGroup[i]:i for i in range(len(NonterminalSymbolGroup))}
    ACTION=[["" for x in range(len(TerminalSymbolGroup))] for y in range(len(states))]
    GOTO=[["" for x in range(len(NonterminalSymbolGroup))] for y in range(len(states))]
    for state in states:
        x = StateIndexTable[state.name]
        EndProduction = copy.deepcopy(StartProduction)
        EndProduction.DotPosition += 1
        LableGroup=[p.ToString() for p in state.Productions]
        if EndProduction.ToString() in LableGroup:
            y = TerminalIndexTable["#"]
            ACTION[x][y] = 'acc'
            continue
        for production in state.Productions:
            expression = production.RightExpression
            position = production.DotPosition
            if position < len(expression) + 1:
                node = expression[position - 1]
                if node['class'] == 'T':
                    y = TerminalIndexTable[node["type"]]
                    To = SearchGoToState(state, node)
                    index='s'+To.name[1:]
                    if ACTION[x][y]!="" and ACTION[x][y]!=index:
                        print('-------------')
                        print(index,end='->')
                        print(ACTION[x][y])
                        print('-------------')
                    ACTION[x][y] = index
                    temp=copy.deepcopy(production)
                    temp.DotPosition=0
                    Shift[index] = temp
            elif position == len(expression) + 1:
                for Terminal in TerminalIndexTable.keys():
                    y = TerminalIndexTable[Terminal]
                    temp=copy.deepcopy(production)
                    temp.DotPosition=0
                    index= 'r'+str(ProductionStringGroup.index(temp.ToString()))
                    if ACTION[x][y]!="":
                        print('-------------')
                        print(index,end='->')
                        print(ACTION[x][y])
                        print('-------------')
                    ACTION[x][y] =index
                    Reduce[index] = temp
    for tuple in edges:
        From,item,To=tuple
        if item['class']=='NT':
            x= StateIndexTable[From.name]
            y= NonterminalIndexTable[item['type']]
            if GOTO[x][y] != "":
                print('-------------------------------')
                print(To.name,end='->')
                print(GOTO[x][y])
                print('-------------------------------')
            GOTO[x][y]=To.name
    return
def PrintTable():
    title=[""]
    row=["状态"]
    for i in range(len(TerminalSymbolGroup)):
        row.append(TerminalSymbolGroup[i]['type'])
        title.append("T"+str(i))
    for i in range(len(NonterminalSymbolGroup)):
        row.append(NonterminalSymbolGroup[i])
        title.append("NT"+str(i))
    x = PrettyTable(title)
    x.add_row(row)
    for i in range(len(DFA.state)):
        row=[DFA.state[i].name]
        for j in range(len(TerminalSymbolGroup)):
            row.append(ACTION[i][j])
        for j in range(len(NonterminalSymbolGroup)):
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
    OpStack=[{'class': 'T', 'type': '#'}]
    StateStack=[DFA.state[0]]
    while True:
        CurrentState=StateStack[-1]
        Token=Tokens[0]
        x = StateIndexTable[CurrentState.name]
        y = TerminalIndexTable[Token['type']]
        Action=ACTION[x][y]
        if Action=='acc':
            step+=1
            OpStackColumn="".join([x['type'] for x in OpStack])
            TokensColumn="".join([x['type'] for x in Tokens])
            Operation="accept"
            StateStackColumn=" ".join([x.name for x in StateStack])
            row=[str(step),OpStackColumn,TokensColumn,Operation,StateStackColumn,Action,""]
            table.add_row(row)
            print(table)
            break
        elif Action[0]=='s':
            NextState=FindStateByName('I'+Action[1:])
            StateStack.append(NextState)
            OpStack.append(Tokens.pop(0))
            step += 1
            OpStackColumn="".join([x['type'] for x in OpStack])
            TokensColumn="".join([x['type'] for x in Tokens])
            Operation="shift"
            StateStackColumn=" ".join([x.name for x in StateStack])
            row=[str(step),OpStackColumn,TokensColumn,Operation,StateStackColumn,Action,""]
            table.add_row(row)
        elif Action[0]=='r':
            production=Reduce[Action]
            cnt=len(production.RightExpression)
            for i in range(cnt):
                item=production.RightExpression[cnt-i-1]
                back=OpStack[-1]
                if item!=back:
                    print("error")
                else:
                    OpStack.pop(-1)
                    StateStack.pop(-1)
            CurrentState = StateStack[-1]
            NT=production.NonterminalSymbol
            x = StateIndexTable[CurrentState.name]
            y = NonterminalIndexTable[NT]
            NextState=FindStateByName(GOTO[x][y])
            StateStack.append(NextState)
            OpStack.append({'class': 'NT', 'type': NT})
            step += 1
            OpStackColumn="".join([x['type'] for x in OpStack])
            TokensColumn="".join([x['type'] for x in Tokens])
            temp=copy.deepcopy(production)
            temp.DotPosition=0
            Operation="reduce({})".format(temp.ToString())
            StateStackColumn=" ".join([x.name for x in StateStack])
            row=[str(step),OpStackColumn,TokensColumn,Operation,StateStackColumn,Action,NextState.name]
            table.add_row(row)
    return
def ExecSimple(code):
    Tokens=[]
    for letter in code:
         Tokens.append({'class': 'T', 'type': letter})
    MakeSyntacticAnalyse(Tokens)
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
    States=DFA.state
    Edges=DFA.edge
    GraphView = Graph()
    for tuple in Edges:
        From,item,To=tuple
        GraphView.add_edge((From.name,To.name,item['type']))
    with open("temp.dot","w") as f:
        f.write(GraphView.to_string())
    os.system("dot -Tpng temp.dot -o temp.png")
    return
ProductionGroup=[]
DotedProductionGroup=[]
TerminalSymbolGroup=[]
NonterminalSymbolGroup=[]
StateIndexTable={}
TerminalIndexTable={}
NonterminalIndexTable={}
ACTION=[]
GOTO=[]
StartProduction=None
DFA=DFA()
Reduce={}
Shift={}
if __name__=='__main__':
    GenerateGrammer("grammer.txt")
    #GenerateCompactGrammer('grammer_simple.txt')
    GenerateDoted()
    #PrintGrammer(DotedProductionGroup)
    GenerateDFA()
    DrawGraph()
    GenerateTable()
    PrintTable()
    # ExecSimple("abbcde#")