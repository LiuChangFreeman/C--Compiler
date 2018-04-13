#coding:utf-8
from __future__ import print_function
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
            result += data['value']+' '
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
    TerminalSymbolGroup.append({'class':'T', 'value': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'value': 'fd'}],1)
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
                            data={'class':'T','type':type[i],'value':match.groups()[0]}
                            break
                elif item in type:#基本类型
                    data ={'class':'T','type': item, 'value': item.upper()}
                elif item in Reflector.keys():#保留字
                    data ={'class':'T','type': item, 'value': Reflector[item]}
                else:#非终结符
                    data ={'class':'NT','value':Compact[item]}
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
    TerminalSymbolGroup.append({'class':'T', 'value': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'value': 'E'}],1)
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
                match=re.match("\'(.+?)\'",item)
                if match:
                    data ={'class':'T', 'value': match.groups()[0]}
                else:#非终结符
                    data ={'class':'NT','value':item}
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
    Result=[p for p in Productions]
    for production in Productions:
        expression=production.RightExpression
        position=production.DotPosition
        if position<len(expression)+1:
            node=expression[position-1]
            if node['class']=='NT':
                productions=FindProduction(node['value'])
                for item in productions:
                    if item.DotPosition==1 and item not in Result:
                        Result.append(item)
    return Result
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
def First(Symbol):
    global FIRST
    global FOLLOW
    result=[]
    Productions=[P for P in ProductionGroup if P.NonterminalSymbol== Symbol]
    if len(Productions)==0:
        return [{'class':'T','value':Symbol}]
    EndSymbol={'class':'T','value':'$'}
    for P in Productions:
        RightExpression=P.RightExpression
        if RightExpression==[EndSymbol] and EndSymbol not in result:
            result.append(EndSymbol)
        else:
            cnt = len(RightExpression)
            if RightExpression[0]['class']=='T' and RightExpression[0] not in result:
                result.append(RightExpression[0])
                continue
            else:
                if RightExpression[0]['value']!=Symbol:
                    TempFirst=RightExpression[0]
                    if TempFirst not in result:
                        result.append(TempFirst)
            if cnt>1:
                previous=RightExpression[0]
                for i in range(1,cnt):
                    if previous['value']!=Symbol:
                        if not EndSymbol in First(previous['value']):
                            break
                        else:
                            if RightExpression[i]['value']!=Symbol:
                                TempFirst = First(RightExpression[i]['value'])
                                if TempFirst not in result:
                                    result.append(TempFirst)
                                previous=RightExpression[i]
    FIRST[Symbol]=result
    return result
def MakeUpFirst():
    def IsFirstComplete(key):
        first = FIRST[key]
        for item in first:
            if item['class'] == 'NT':
                return False
        return True
    global FIRST
    procession=[]
    for key in FIRST.keys():
        first=FIRST[key]
        for item in first:
            if item['class']=='NT':
                name=item['value']
                if IsFirstComplete(name):
                    for value in FIRST[name]:
                        if value not in first:
                            first.append(value)
                    first.remove(item)
                else:
                    procession.append(key)
                    break
    while len(procession)>0:
        for key in procession:
            temp=FIRST
            first = FIRST[key]
            for item in first:
                if item['class'] == 'NT':
                    if IsFirstComplete(item['value']):
                        for value in FIRST[item['value']]:
                            if value not in first:
                                first.append(value)
                        first.remove(item)
            if IsFirstComplete(key):
                procession.remove(key)
    return
def Follow(Symbol):
    global FOLLOW
    result = []
    EndSymbol = {'class': 'T', 'value': '$'}
    for production in ProductionGroup:
        RightExpression=production.RightExpression
        cnt = len(RightExpression)
        for i in range(cnt):
            if RightExpression[i]['value'] == Symbol:
                if i==cnt-1:
                    if production.NonterminalSymbol!=Symbol:
                        temp={}
                        if production.NonterminalSymbol == 'S':
                            temp={'class': 'T', 'value': '#'}
                        else:
                            temp={'class': 'NT', 'value': production.NonterminalSymbol}
                        if temp not in result:
                            result.append(temp)
                else:
                    next=RightExpression[i+1]
                    if next['class']=='T':
                        if next not in result:
                            result.append(next)
                    else:
                        temp=FIRST
                        for item in FIRST[next['value']]:
                            if item['value']!='$' and item not in result:
                                result.append(item)
                    if i==cnt-2 and EndSymbol in First(next['value']) and next not in result:
                        result.append(next)
    FOLLOW[Symbol] = result
    return result
def MakeUpFollow():
    def IsFollowComplete(key):
        follow = FOLLOW[key]
        for item in follow:
            if item['class'] == 'NT':
                return False
        return True
    global FOLLOW
    temp=FOLLOW
    procession=[]
    for key in FOLLOW.keys():
        follow=FOLLOW[key]
        for item in follow:
            if item['class']=='NT':
                name=item['value']
                if IsFollowComplete(name):
                    for value in FOLLOW[name]:
                        if value not in follow:
                            follow.append(value)
                    follow.remove(item)
                else:
                    procession.append(key)
                    break
    while len(procession)>0:
        change=False
        for key in procession:
            temp=FOLLOW
            follow = FOLLOW[key]
            for item in follow:
                if item['class'] == 'NT':
                    if IsFollowComplete(item['value']):
                        for value in FOLLOW[item['value']]:
                            if value not in follow:
                                follow.append(value)
                        follow.remove(item)
                        change =True
            if IsFollowComplete(key):
                procession.remove(key)
        if not change:
            break
    return
def GenerateFirstAndFollow():
    for Nonterminal in NonterminalSymbolGroup:
        First(Nonterminal)
    MakeUpFirst()
    for Nonterminal in NonterminalSymbolGroup:
        Follow(Nonterminal)
    MakeUpFollow()
    return
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
    #     print(From.name+"+"+item['value']+"->"+To.name)
    StateIndexTable = {states[i].name:i for i in range(len(states))}
    TerminalIndexTable = {TerminalSymbolGroup[i]["value"]:i for i in range(len(TerminalSymbolGroup))}
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
                    y = TerminalIndexTable[node["value"]]
                    To = SearchGoToState(state, node)
                    index='s'+To.name[1:]
                    if ACTION[x][y]!="" and ACTION[x][y]!=index:
                        print("{}包含shift-reduce冲突".format(state.name))
                        print(index,end='->')
                        print(ACTION[x][y])
                        print(state.ToString())
                        print('-------------')
                    ACTION[x][y] = index
                    temp=copy.deepcopy(production)
                    temp.DotPosition=0
                    Shift[index] = temp
            elif position == len(expression) + 1:
                def IsFollowComplete(key):
                    follow = FOLLOW[key]
                    for item in follow:
                        if item['class'] == 'NT':
                            return False
                    return True
                if IsFollowComplete(production.NonterminalSymbol):
                    items = [i for i in FOLLOW[production.NonterminalSymbol]]
                else:
                    items=TerminalSymbolGroup
                for Terminal in items:
                    Terminal=Terminal['value']
                    y = TerminalIndexTable[Terminal]
                    temp=copy.deepcopy(production)
                    temp.DotPosition=0
                    index= 'r'+str(ProductionStringGroup.index(temp.ToString()))
                    if ACTION[x][y]!="":
                        print("{}包含shift-reduce冲突".format(state.name))
                        print(index,end='->')
                        print(ACTION[x][y])
                        print(state.ToString())
                        print(temp.ToString())
                        print('-------------')
                    ACTION[x][y] =index
                    Reduce[index] = temp
    for tuple in edges:
        From,item,To=tuple
        if item['class']=='NT':
            x= StateIndexTable[From.name]
            y= NonterminalIndexTable[item['value']]
            if GOTO[x][y] != "":
                print(To.name,end='->')
                print(GOTO[x][y])
                print('-------------')
            GOTO[x][y]=To.name
    return
def PrintTable():
    title=[""]
    row=["状态"]
    for i in range(len(TerminalSymbolGroup)):
        row.append(TerminalSymbolGroup[i]['value'])
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
    OpStack=[{'class': 'T', 'value': '#'}]
    StateStack=[DFA.state[0]]
    while True:
        CurrentState=StateStack[-1]
        Token=Tokens[0]
        x = StateIndexTable[CurrentState.name]
        y = TerminalIndexTable[Token['value']]
        Action=ACTION[x][y]
        if Action=='acc':
            step+=1
            OpStackColumn="".join([x['value'] for x in OpStack])
            TokensColumn="".join([x['value'] for x in Tokens])
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
            OpStackColumn="".join([x['value'] for x in OpStack])
            TokensColumn="".join([x['value'] for x in Tokens])
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
            OpStack.append({'class': 'NT', 'value': NT})
            step += 1
            OpStackColumn="".join([x['value'] for x in OpStack])
            TokensColumn="".join([x['value'] for x in Tokens])
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
         Tokens.append({'class': 'T', 'value': letter})
    MakeSyntacticAnalyse(Tokens)
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
FIRST={}
FOLLOW={}
if __name__=='__main__':
    GenerateGrammer("grammer_compact.txt")
    #GenerateCompactGrammer('grammer_simple.txt')
    GenerateDoted()
    #PrintGrammer(ProductionGroup)
    GenerateDFA()
    GenerateFirstAndFollow()
    GenerateTable()
    PrintTable()
    Tokens=main('test.c')
    #MakeSyntacticAnalyse(tokens)