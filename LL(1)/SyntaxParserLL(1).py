#coding:utf-8
from __future__ import print_function
import re
import copy
from prettytable import *
from Definitions import *
regexs=[
    '{|}|[|]|(|)|,|;|.|?|:'#界符
    ,'++|+|>>=|<<=|>>|<<|--|-|+=|-=|*|*=|%|%=|->|||||||=|/|/=|>|<|>=|<=|==|!=|^=|=|!|~|&&|&|&='#操作符
]
class Production():
    def __init__(self,NonterminalSymbol,RightExpression):
        self.NonterminalSymbol=NonterminalSymbol
        self.RightExpression=RightExpression
    def ToString(self):
        result=self.NonterminalSymbol+'->'
        for data in self.RightExpression:
            result += data['value']+' '
        return result
def GenerateGrammer(file):
    global ProductionGroup
    global TerminalSymbolGroup
    global NonterminalSymbolGroup
    global StartProduction
    type = [
        'seperator', 'operator', 'id', 'STRING', 'CHAR', 'INT', 'FLOAT'
    ]
    NonterminalSymbolGroup.append('S')
    TerminalSymbolGroup.append({'class':'T','value': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'value': 'ed'}])
    ProductionGroup.append(StartProduction)
    blocks = open(file).read().split('\n\n')
    Reflector = {Reserved[x]: x for x in Reserved.keys()}
    NonterminalSymbolGroup = [x.split('\n')[0] for x in blocks]
    temp = NonterminalSymbolGroup
    Compact = {}
    for lable in NonterminalSymbolGroup:
        code = ""
        codes = lable.split('_')
        for item in codes:
            code += item[0]
        while True:
            if not code in Compact.values():
                Compact[lable] = code
                break
            else:
                code += 'a'
    for block in blocks:
        lines = block.split('\n')
        NonterminalSymbol = lines[0]
        Expressions = [x.strip(' ')[1:] for x in lines[1:-1]]
        for expression in Expressions:
            RightExpression = []
            items = expression.strip(' ').split(' ')
            for item in items:
                data = {}
                match = re.match("\'(.+?)\'", item)
                if match:  # 界符或者操作符
                    for i in range(2):
                        if match.groups()[0] in regexs[i]:
                            data = {'class': 'T', 'type': type[i], 'value': match.groups()[0]}
                            break
                    if data == {}:
                        data = {'class': 'T', 'value': '$'}
                elif item in type:  # 基本类型
                    data = {'class': 'T', 'type': item, 'value': item.upper()}
                elif item in Reserved.keys():  # 保留字
                    data = {'class': 'T', 'type': item, 'value': item}
                else:  # 非终结符
                    data = {'class': 'NT', 'value': Compact[item]}
                RightExpression.append(data)
                if not data in TerminalSymbolGroup and data['class'] != 'NT':
                    TerminalSymbolGroup.append(data)
            ProductionGroup.append(Production(Compact[NonterminalSymbol], RightExpression))
    NonterminalSymbolGroup = Compact.values()
    return
def PrintGrammer(ProductionGroup):
    for Production in ProductionGroup:
        print(Production.ToString())
def First(Symbol):
    global FIRST
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
                                    result.append(TempFirst[0])
                                previous=RightExpression[i]
    FIRST[Symbol]=result
    return result
def MakeUpFirst():
    def IsFirstComplete(key):
        temp=FIRST
        first = FIRST[key]
        for item in first:
            if item['class'] == 'NT':
                return False
        return True
    global FIRST
    procession =FIRST.keys()
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
                        result.append(next)
                    else:
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
    procession=FOLLOW.keys()
    while len(procession)>0:
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
            if IsFollowComplete(key):
                procession.remove(key)
    return
def GenerateFirstAndFollow():
    for Nonterminal in NonterminalSymbolGroup:
        First(Nonterminal)
    MakeUpFirst()
    temp=FIRST
    for Nonterminal in NonterminalSymbolGroup:
        Follow(Nonterminal)
    MakeUpFollow()
    for key in FIRST.keys():
        print(key,end=':')
        print(FIRST[key])
    for key in FOLLOW.keys():
        print(key,end=':')
        print(FOLLOW[key])
    return
FIRST={}
FOLLOW={}
ProductionGroup=[]
TerminalSymbolGroup=[]
NonterminalSymbolGroup=[]
TerminalIndexTable={}
NonterminalIndexTable={}
StartProduction=None
if __name__=='__main__':
    GenerateGrammer('grammer.txt')
    #PrintGrammer(DotedProductionGroup)
    GenerateFirstAndFollow()
    temp=FOLLOW
    temp=""