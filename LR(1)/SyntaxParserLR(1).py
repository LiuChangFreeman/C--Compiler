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
    def __init__(self, NonterminalSymbol, RightExpression, DotPosition=0, TerminalTail=None):
        self.NonterminalSymbol=NonterminalSymbol
        self.RightExpression=RightExpression
        self.DotPosition=DotPosition
        self.TerminalTail=TerminalTail
    def Next(self):
        return Production(self.NonterminalSymbol,
                          self.RightExpression,
                          self.DotPosition + 1,
                          self.TerminalTail)
    def ToString(self):
        result=self.NonterminalSymbol+'->'
        position=1
        for data in self.RightExpression:
            if position==self.DotPosition:
                result += '@'
            result += data['value']+' '
            position += 1
        if position == self.DotPosition:
            result += '@'
        result += ',['
        if self.TerminalTail!=None:
            if len(self.TerminalTail)>0:
                for item in sorted(self.TerminalTail):
                    result += '\''+item+'\''+','
                result= result[:-1]
        result += ']'
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
        return "\n".join(sorted(self.string))
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
def GenerateGrammer(file):
    global ProductionGroup
    global TerminalSymbolGroup
    global NonterminalSymbolGroup
    global StartProduction
    NonterminalSymbolGroup.append('S')
    TerminalSymbolGroup.append({'class':'T', 'value': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'value': 'function_definition'}],1,['#'])
    ProductionGroup.append(StartProduction)
    blocks=open(file).read().split('\n\n')
    Reflector={Reserved[x]:x for x in Reserved.keys()}
    NonterminalSymbolGroup=[x.split('\n')[0] for x in blocks]
    # Compact = {}
    # for lable in NonterminalSymbolGroup:
    #     code = ""
    #     codes = lable.split('_')
    #     for item in codes:
    #         code += item[0]
    #     if not code in Compact.values():
    #         Compact[lable] = code
    #     elif not code + 't' in Compact.values():
    #         Compact[lable] = code + 't'
    #     else:
    #         Compact[lable] = code + 'a'
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
                    if data=={}:
                        data = {'class': 'T', 'value': '$'}
                elif item in type:#基本类型
                    data ={'class':'T','type': item, 'value': item.upper()}
                elif item in Reserved.values():#保留字
                    data ={'class':'T','type': item, 'value': item.lower()}
                else:#非终结符
                     data ={'class':'NT','value':item}
                RightExpression.append(data)
                if not data in TerminalSymbolGroup and data['class']!='NT':
                    TerminalSymbolGroup.append(data)
            ProductionGroup.append(Production(NonterminalSymbol, RightExpression, TerminalTail=['#']))
    return
def GenerateCompactGrammer(file):
    global ProductionGroup
    global TerminalSymbolGroup
    global NonterminalSymbolGroup
    global StartProduction
    NonterminalSymbolGroup.append('N')
    TerminalSymbolGroup.append({'class':'T', 'value': '#'})
    StartProduction = Production('N',[{'class': 'NT', 'value': 'S'}],1,['#'])
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
            ProductionGroup.append(Production(NonterminalSymbol, RightExpression, TerminalTail=['#']))
    return
# def GenerateOriGrammer(file):
#     global ProductionGroup
#     global TerminalSymbolGroup
#     global NonterminalSymbolGroup
#     global StartProduction
#     NonterminalSymbolGroup.append('S')
#     TerminalSymbolGroup.append({'class':'T', 'value': '#'})
#     StartProduction = Production('S',[{'class': 'NT', 'value': 'fd'}],1,'#')
#     ProductionGroup.append(StartProduction)
#     blocks=open(file).read().split('\n\n')
#     Reflector={Reserved[x]:x for x in Reserved.keys()}
#     NonterminalSymbolGroup=[x.split('\n')[0] for x in blocks]
#     temp=NonterminalSymbolGroup
#     Compact = {}
#     for lable in NonterminalSymbolGroup:
#         code = ""
#         codes = lable.split('_')
#         for item in codes:
#             code += item[0]
#         while True:
#             if not code in Compact.values():
#                 Compact[lable] = code
#                 break
#             else:
#                 code += 'a'
#     for block in blocks:
#         lines=block.split('\n')
#         NonterminalSymbol=lines[0]
#         Expressions=[x.strip(' ')[1:] for x in lines[1:-1]]
#         for expression in Expressions:
#             RightExpression=[]
#             items=expression.strip(' ').split(' ')
#             for item in items:
#                 data={}
#                 match=re.match("\'(.+?)\'",item)
#                 if match:#界符或者操作符
#                     for i in range(2):
#                         if match.groups()[0] in regexs[i]:
#                             data={'class':'T','type':type[i],'value':match.groups()[0]}
#                             break
#                 elif item in type:#基本类型
#                     data ={'class':'T','type': item, 'value': item.upper()}
#                 elif item in Reflector.keys():#保留字
#                     data ={'class':'T','type': item, 'value': Reflector[item]}
#                 else:#非终结符
#                      data ={'class':'NT','value':Compact[item]}
#                 RightExpression.append(data)
#                 if not data in TerminalSymbolGroup and data['class']!='NT':
#                     TerminalSymbolGroup.append(data)
#             ProductionGroup.append(Production(Compact[NonterminalSymbol], RightExpression, TerminalTail='#'))
#     NonterminalSymbolGroup=Compact.values()
#     return
# def GenerateFullGrammer(file):
#     global ProductionGroup
#     global TerminalSymbolGroup
#     global NonterminalSymbolGroup
#     global StartProduction
#     NonterminalSymbolGroup.append('S')
#     TerminalSymbolGroup.append({'class':'T', 'value': '#'})
#     StartProduction = Production('S',[{'class': 'NT', 'value': 'fd'}],1,'#')
#     ProductionGroup.append(StartProduction)
#     blocks=open(file).read().split('\n\n')
#     Reflector={Reserved[x]:x for x in Reserved.keys()}
#     NonterminalSymbolGroup=[x.split('\n')[0] for x in blocks]
#     temp=NonterminalSymbolGroup
#     Compact = {}
#     for lable in NonterminalSymbolGroup:
#         code = ""
#         codes = lable.split('_')
#         for item in codes:
#             code += item[0]
#         while True:
#             if not code in Compact.values():
#                 Compact[lable] = code
#                 break
#             else:
#                 code += 'a'
#     for block in blocks:
#         lines=block.split('\n')
#         NonterminalSymbol=lines[0]
#         Expressions=[x.strip(' ')[1:] for x in lines[1:-1]]
#         for expression in Expressions:
#             RightExpression=[]
#             items=expression.strip(' ').split(' ')
#             for item in items:
#                 data={}
#                 match=re.match("\'(.+?)\'",item)
#                 if match:#界符或者操作符
#                     for i in range(2):
#                         if match.groups()[0] in regexs[i]:
#                             data={'class':'T','type':type[i],'value':match.groups()[0]}
#                             break
#                 elif item in type:#基本类型
#                     data ={'class':'T','type': item, 'value': item.upper()}
#                 elif item in Reflector.keys():#保留字
#                     data ={'class':'T','type': item, 'value': Reflector[item]}
#                 else:#非终结符
#                      data ={'class':'NT','value':Compact[item]}
#                 RightExpression.append(data)
#                 if not data in TerminalSymbolGroup and data['class']!='NT':
#                     TerminalSymbolGroup.append(data)
#             ProductionGroup.append(Production(Compact[NonterminalSymbol], RightExpression, TerminalTail='#'))
#     NonterminalSymbolGroup=Compact.values()
#     return
def GenerateNewGrammer(file):
    global ProductionGroup
    global TerminalSymbolGroup
    global NonterminalSymbolGroup
    global StartProduction
    type = [
        'seperator', 'operator', 'id', 'STRING', 'CHAR', 'INT', 'FLOAT'
    ]
    NonterminalSymbolGroup.append('S')
    TerminalSymbolGroup.append({'class':'T', 'value': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'value': 'start'}],1, TerminalTail=['#'])
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
                RightExpression.append(data)
                if not data in TerminalSymbolGroup and data['class']!='NT':
                    TerminalSymbolGroup.append(data)
    #         ProductionGroup.append(Production(Compact[NonterminalSymbol], RightExpression,TerminalSymbol='#'))
    # NonterminalSymbolGroup=Compact.values()
            ProductionGroup.append(Production(NonterminalSymbol, RightExpression, TerminalTail=['#']))
    return
def PrintGrammer(ProductionGroup):
    for Production in ProductionGroup:
        print(Production.ToString())
def AddDot(P):
    result=[]
    if len(P.RightExpression)==1 and P.RightExpression[0]['value']=='$':
        result.append(Production(P.NonterminalSymbol,P.RightExpression,1))
    else:
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
    def Expand(production):
        data=[]
        right = production.RightExpression
        position = production.DotPosition
        terminal = production.TerminalTail
        def GetFirstSet(node):
            if node['class'] == 'NT':
                return FIRST[next['value']]
            else:
                return First(next['value'])
        if position < len(right) + 1 and right[position - 1]['class'] == 'NT':
            first=[]
            Flag=True
            for i in range(position, len(right)):
                next=right[i]
                firstset=copy.deepcopy(GetFirstSet(next))
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
                    Flag =False
                    break
            if Flag:
                for item in terminal:
                    if not item in first:
                        first.append({'class':'T','value':item})
            productions = FindProduction(right[position - 1]['value'])
            for item in productions:
                if item.DotPosition == 1:
                    temp = copy.deepcopy(item)
                    temp.TerminalTail =[item['value'] for item in first]
                    data.append(temp)
        return data
    cache=[p.ToString() for p in Productions]
    result=[p for p in Productions]
    procession=[p for p in Productions]
    while len(procession)>0:
        production=procession.pop()
        data=Expand(production)
        for item in data:
            if item.ToString() not in cache:
                result.append(item)
                cache.append(item.ToString())
                procession.append(item)
    return result
def GO(I,item):
    Params=[]
    for production in I.Productions:
        expression=production.RightExpression
        position=production.DotPosition
        if position<len(expression)+1:
            node=expression[position-1]
            if node['value']=='$' and len(expression)==1:
                continue
            if node==item and production.Next() not in Params:
                Params.append(production.Next())
    return CLOSURE(Params)
def First(Symbol):
    global FIRST
    result=[]
    Productions=[P for P in ProductionGroup if P.NonterminalSymbol== Symbol]
    if len(Productions)==0:
        return [{'class':'T','value':Symbol}]
    EndSymbol={'class':'T','value':'$'}
    for P in Productions:
        right=P.RightExpression
        if right==[EndSymbol] and EndSymbol not in result:
            result.append(EndSymbol)
        else:
            cnt = len(right)
            if right[0]['class']=='T' and right[0] not in result:
                result.append(right[0])
                continue
            else:
                if right[0]['value']!=Symbol:
                    TempFirst=right[0]
                    if TempFirst not in result:
                        result.append(TempFirst)
            if cnt>1:
                previous=right[0]
                for i in range(1,cnt):
                    if previous['value']!=Symbol:
                        if not EndSymbol in First(previous['value']):
                            break
                        else:
                            if right[i]['value']!=Symbol:
                                TempFirst = First(right[i]['value'])
                                if TempFirst not in result:
                                    result.append(TempFirst[0])
                                previous=right[i]
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
    procession =FIRST.keys()
    while len(procession)>0:
        for key in procession:
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
def GenerateFirst():
    for Nonterminal in NonterminalSymbolGroup:
        First(Nonterminal)
    MakeUpFirst()
    def PrintFirst():
        for key in FIRST.keys():
            item=FIRST[key]
            print(key,end='->')
            for value in item:
                print(value['value'],end=' ')
            print('')
    return
def GenerateDFA():
    global DFA
    def Merge(Productions):
        result=[]
        table={}
        reversed={}
        for p in Productions:
            temp=Production(p.NonterminalSymbol,p.RightExpression,p.DotPosition)
            teiminals = p.TerminalTail
            if not temp.ToString() in table.keys():
                table[temp.ToString()]=teiminals
                reversed[temp.ToString()]=temp
            else:
                for t in teiminals:
                    table[temp.ToString()].append(t)
        for key in table.keys():
            temp=reversed[key]
            temp.TerminalTail=table[key]
            result.append(temp)
        return result
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
        I=Procession.pop(0)
        # print(I.ToString(),end='\n\n')
        Items=I.GetItem()
        # for p in I.Productions:
        for item in Items:
            temp=State('I'+str(CurrentState))
            temp.Productions = Merge(GO(I, item))
            # temp.Productions=[p]
            # temp.Productions =Merge(GO(temp,item))
            string=temp.ToString()
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
    ProductionStringGroup[0].DotPosition=0
    ProductionStringGroup=[p.ToString() for p in ProductionStringGroup]
    states=DFA.state
    edges=DFA.edge
    StateIndexTable = {states[i].name:i for i in range(len(states))}
    TerminalIndexTable = {TerminalSymbolGroup[i]["value"]:i for i in range(len(TerminalSymbolGroup))}
    NonterminalIndexTable = {NonterminalSymbolGroup[i]:i for i in range(len(NonterminalSymbolGroup))}
    ACTION=[["" for x in range(len(TerminalSymbolGroup))] for y in range(len(states))]
    GOTO=[["" for x in range(len(NonterminalSymbolGroup))] for y in range(len(states))]
    for state in states:
        #print(states.index(state))
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
            eps={'calss':'T','value':'$'}
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
                            print(state.ToString())
                            print('-------------')
                        ACTION[x][y] = index
                        temp = copy.deepcopy(production)
                        temp.DotPosition = 0
                        temp.TerminalTail = ('#')
                        Shift[index] = temp
                    else:
                        for i in range(len(production.TerminalTail)):
                            y = TerminalIndexTable[production.TerminalTail[i]]
                            temp = copy.deepcopy(production)
                            temp.DotPosition = 0
                            temp.TerminalTail = ('#')
                            index = 'r' + str(ProductionStringGroup.index(temp.ToString()))
                            if ACTION[x][y] != "" and ACTION[x][y] != index:
                                print("{}包含shift-reduce冲突".format(state.name))
                                print(index, end='->')
                                print(ACTION[x][y])
                                print(state.ToString())
                                print(temp.ToString())
                                print('-------------')
                            ACTION[x][y] = index
                            Reduce[index] = temp

            elif position == len(expression) + 1:
                for i in range(len(production.TerminalTail)):
                    y = TerminalIndexTable[production.TerminalTail[i]]
                    temp=copy.deepcopy(production)
                    temp.DotPosition=0
                    temp.TerminalTail=('#')
                    index= 'r'+str(ProductionStringGroup.index(temp.ToString()))
                    if ACTION[x][y]!="" and ACTION[x][y]!=index:
                        print("{}包含shift-reduce冲突".format(state.name))
                        print(index,end='->')
                        print(ACTION[x][y])
                        print(state.ToString())
                        print(temp.ToString())
                        print('-------------')
                    ACTION[x][y] =index
                    Reduce[index] = temp
    temp=[(tuple[0].name,tuple[1]['value'],tuple[2].name)for tuple in edges]
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
    for i in range(len(NonterminalSymbolGroup)):
        title.append(NonterminalSymbolGroup[i])
    temp=title
    title.sort()
    x = PrettyTable(title)
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
            cnt=len(production.RightExpression)
            if cnt==1 and production.RightExpression[0]['value'] == '$':
                des = {'class': 'NT', 'value': production.NonterminalSymbol}
                CurrentState = StateStack[-1]
                StateStack.append(SearchGoToState(CurrentState, des))
                OpStack.append(des)
                continue
            for i in range(cnt):
                    item=production.RightExpression[cnt-i-1]
                    back = OpStack[-1]
                    if item['class'] != back['class'] and item['value'] != back['value']:
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
            OpStackColumn=""
            TokensColumn=""
            if len([x['value'] for x in OpStack])>5:
                OpStackColumn="...... "
            OpStackColumn+=" ".join([x['value'] for x in OpStack][-5:])
            TokensColumn+=" ".join([x['value'] for x in Tokens][:5])
            if len([x['value'] for x in Tokens]) > 5:
                TokensColumn += " ......"
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
        GraphView.add_edge((From.name,To.name,item['value']))
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
FIRST={}
FOLLOW={}
if __name__=='__main__':
    GenerateNewGrammer("grammer.txt")
    #GenerateGrammer("grammer_compact.txt")
    #GenerateCompactGrammer('grammer_simple.txt')
    GenerateDoted()
    #PrintGrammer(ProductionGroup)
    GenerateFirst()
    GenerateDFA()
    DrawGraph()
    GenerateTable()
    PrintTable()
    Tokens=main('source.cc')
    MakeSyntacticAnalyse(Tokens)