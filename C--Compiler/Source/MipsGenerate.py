#coding:utf-8
from __future__ import print_function
import os
import copy
from Definitions import *
from LexcialAnalyzer import *
regexs=[
    '{|}|[|]|(|)|,|;|.|?|:'#界符
    ,'++|+|>>=|<<=|>>|<<|--|-|+=|-=|*|*=|%|%=|->|||||||=|/|/=|>|<|>=|<=|==|!=|^=|=|!|~|&&|&|&='#操作符
]
class Node():
    def __init__(self):
        self.place=None
        self.code=[]
        self.asm = []
        self.stack = []
        self.name=None
        self.type = None
        self.data = None
        self.begin=None
        self.end=None
        self.true=None
        self.false=None
class Symbol:
    def __init__(self):
        self.name=None
        self.type=None
        self.size=None
        self.offset=None
        self.place=None
        self.function=None
class FunctionSymbol:
    def __init__(self):
        self.name = None
        self.type = None
        self.lable = None
        self.params = []
def GetFilePath(path):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, path)
def FindSymbol(name, function):
    for item in SymbolTable:
        if item.name==name and item.function == function:
            return item
    return None
def UpdateSymbolTable(symbol):
    global SymbolTable
    for item in SymbolTable:
        if item.name == symbol.name and item.function == symbol.function:
            SymbolTable.remove(item)
            break
    SymbolTable.append(symbol)
def FindFunctionByName(name):
    for item in FunctionTable:
        if item.name==name:
            return item
    return None
def UpdateFunctionTable(symbol):
    global FunctionTable
    for item in FunctionTable:
        if item.name == symbol.name:
            FunctionTable.remove(item)
            break
    FunctionTable.append(symbol)
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
    TerminalSymbolGroup.append({'class':'T', 'type': '#'})
    StartProduction = Production('S',[{'class': 'NT', 'type': 'start'}],1, terminals=['#'])
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
                            data={'class':'T','name':type[i],'type':match.groups()[0]}
                            break
                    if data=={}:
                        data = {'class': 'T', 'type': '$'}
                elif item in type and item !='operator':#基本类型
                    data ={'class':'T','name': item, 'type': item.upper()}
                elif item in Reserved.keys():#保留字
                    data ={'class':'T','name': item, 'type': item}
                else:#非终结符
                     data ={'class':'NT','type':item}
                right.append(data)
                if not data in TerminalSymbolGroup and data['class']!='NT':
                    TerminalSymbolGroup.append(data)
            ProductionGroup.append(Production(left, right, terminals=['#']))
    return
def PrintGrammer(ProductionGroup):
    for Production in ProductionGroup:
        print(Production.to_string_compact())
def AddDotToproductions(production):
    result=[]
    if len(production.right)==1 and production.right[0]['type']== '$':
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
                return FIRST[next['type']]
            else:
                return GetFirstSet(next['type'])
        if position < len(right) + 1 and right[position - 1]['class'] == 'NT':
            first=[]
            flag=True
            for i in range(position, len(right)):
                next=right[i]
                firstset=copy.deepcopy(get_first_set(next))
                eps={'class':'T','type':'$'}
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
                        first.append({'class':'T','type':item})
            productions = FindProduction(right[position - 1]['type'])
            for item in productions:
                if item.position == 1:
                    temp = copy.deepcopy(item)
                    temp.terminals =[item['type'] for item in first]
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
            if node['type']=='$' and len(expression)==1:
                continue
            if node==item and production.Next() not in params:
                params.append(production.Next())
    return CLOSURE(params)
def GetFirstSet(symbol):
    global FIRST
    result=[]
    productions=[production for production in ProductionGroup if production.left == symbol]
    if len(productions)==0:
        return [{'class':'T','type':symbol}]
    end_symbol={'class':'T','type':'$'}
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
                if right[0]['type']!=symbol:
                    temp_first=right[0]
                    if temp_first not in result:
                        result.append(temp_first)
            if cnt>1:
                previous=right[0]
                for i in range(1,cnt):
                    if previous['type']!=symbol:
                        if not end_symbol in GetFirstSet(previous['type']):
                            break
                        else:
                            if right[i]['type']!=symbol:
                                temp_first = GetFirstSet(right[i]['type'])
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
                    if IsFirstSetComplete(item['type']):
                        for value in FIRST[item['type']]:
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
    TerminalIndexTable = {TerminalSymbolGroup[i]["type"]:i for i in range(len(TerminalSymbolGroup))}
    NonterminalIndexTable = {LeftGroup[i]:i for i in range(len(LeftGroup))}
    ACTION=[[" " for x in range(len(TerminalSymbolGroup))] for y in range(len(states))]
    GOTO=[[" " for x in range(len(LeftGroup))] for y in range(len(states))]
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
                    y = TerminalIndexTable[node["type"]]
                    To = SearchGoToState(state, node)
                    if node['type'] != '$':
                        index='s'+To.name[1:]
                        if ACTION[x][y] != "" and ACTION[x][y] != index:
                            pass
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
                                pass
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
                        pass
                    ACTION[x][y] =index
                    Reduce[index] = temp
    for tuple in edges:
        From,item,To=tuple
        if item['class']=='NT':
            x= StateIndexTable[From.name]
            y= NonterminalIndexTable[item['type']]
            if GOTO[x][y] != "" and GOTO[x][y] != To.name:
                pass
            GOTO[x][y]=To.name
    return
def PrintTable():
    title=[""]
    for i in range(len(TerminalSymbolGroup)):
        title.append(TerminalSymbolGroup[i]['type'])
    for i in range(len(LeftGroup)):
        title.append(LeftGroup[i])
    x = [title]
    for i in range(len(DFA.state)):
        row=[DFA.state[i].name]
        for j in range(len(TerminalSymbolGroup)):
            row.append(ACTION[i][j])
        for j in range(len(LeftGroup)):
            row.append(GOTO[i][j])
        x.append(row)
    with open(GetFilePath("lr(1).table"),'w') as fd:
        for row in x:
            for colum in row:
                fd.write(colum+'\t')
            fd.write('\n')
    return
def AddTableColum(Operation, Action, State):
    global Table
    global CurrentStep
    CurrentStep += 1
    OpStackColumn = ""
    TokensColumn = ""
    if len([x['type'] for x in OpStack]) > 5:
        OpStackColumn = "...... "
    OpStackColumn += " ".join([x['type'] for x in OpStack][-5:])
    TokensColumn += " ".join([x['type'] for x in Tokens][:5])
    if len([x['type'] for x in Tokens]) > 5:
        TokensColumn += " ......"
    StateStackColumn = " ".join([x.name for x in StateStack])
    row = [str(CurrentStep), OpStackColumn, TokensColumn, Operation, StateStackColumn, Action, State]
    Table.append(row)
    return
def MakeAnalyse():
    global OpStack
    global StateStack
    global CurrentProduction
    global Table
    global Tokens
    #title=["步骤","当前栈","输入串","动作","状态栈","ACTION","GOTO"]
    #Table = [title]
    Table = []
    def FindStateByName(name):
        for state in DFA.state:
            if state.name==name:
                return state
    EndSymbol={'class': 'T', 'type': '#'}
    OpStack=[EndSymbol]
    StateStack=[DFA.state[0]]
    while True:
        CurrentState=StateStack[-1]
        if len(Tokens)==0:
            Token = EndSymbol
        else:
            Token = Tokens[0]
        x = StateIndexTable[CurrentState.name]
        y = TerminalIndexTable[Token['type']]
        Action=ACTION[x][y]
        if Action==' ':
            exit(1)
        if Action=='acc':
            Operation = "accept"
            AddTableColum(Operation,Action,"")
            with open(GetFilePath("analysis.table"), 'w') as fd:
                for row in Table:
                    for colum in row:
                        fd.write(colum + '\t')
                    fd.write('\n')
            break
        elif Action[0]=='s':
            NextState=FindStateByName('I'+Action[1:])
            StateStack.append(NextState)
            Temp =Tokens.pop(0)
            OpStack.append(Temp)
            Operation = "shift"
            AddTableColum(Operation,Action,"")
        elif Action[0]=='r':
            CurrentProduction=Reduce[Action]
            SemanticAnalysis()
            cnt=len(CurrentProduction.right)
            if cnt==1 and CurrentProduction.right[0]['type'] == '$':
                Destination = {'class': 'NT', 'type': CurrentProduction.left}
                CurrentState = StateStack[-1]
                TempState=SearchGoToState(CurrentState, Destination)
                StateStack.append(SearchGoToState(CurrentState, Destination))
                OpStack.append(Destination)
                temp = copy.deepcopy(CurrentProduction)
                temp.position = 0
                Operation = "reduce({})".format(temp.to_string())
                AddTableColum(Operation, Action, TempState.name)
                continue
            for i in range(cnt):
                    item=CurrentProduction.right[cnt-i-1]
                    back = OpStack[-1]
                    if item['class'] != back['class'] and item['type'] != back['type']:
                        print("error in parser place row:{},colum{}".format(Token['row'],Token['colum']))
                        exit(-1)
                    else:
                        OpStack.pop(-1)
                        StateStack.pop(-1)
            CurrentState = StateStack[-1]
            NT=CurrentProduction.left
            x = StateIndexTable[CurrentState.name]
            y = NonterminalIndexTable[NT]
            NextState=FindStateByName(GOTO[x][y])
            StateStack.append(NextState)
            OpStack.append({'class': 'NT', 'type': NT})
            temp = copy.deepcopy(CurrentProduction)
            temp.position = 0
            Operation = "reduce({})".format(temp.to_string())
            AddTableColum(Operation, Action,NextState.name)
    return
def NewLabel():
    global CurrentLable
    CurrentLable+=1
    return "l"+str(CurrentLable)
def NewFunction():
    global CurrentFunction
    CurrentFunction+=1
    return "f"+str(CurrentFunction)
def NewTemp():
    global CurrentTemp
    CurrentTemp+=1
    return "t"+str(CurrentTemp)
def SemanticAnalysis():
    LeftExpr=CurrentProduction.left
    RightExpr=CurrentProduction.right
    if LeftExpr=='operator':
        NewNode=Node()
        NewNode.name= 'operator'
        NewNode.type=''
        for i in range(len(RightExpr)):
            Token = OpStack[-(len(RightExpr)-i)]
            NewNode.type += Token['type']
        SemanticStack.append(NewNode)
    elif LeftExpr=='assignment_operator':
        NewNode=Node()
        NewNode.name= 'assignment_operator'
        NewNode.type=[]
        for i in range(len(RightExpr)):
            NewNode.type.append(RightExpr[i]['type'])
        SemanticStack.append(NewNode)
    elif LeftExpr=='type_specifier':
        NewNode=Node()
        NewNode.name= 'type_specifier'
        NewNode.type=RightExpr[0]['type']
        SemanticStack.append(NewNode)
    elif LeftExpr=='primary_expression':
        NewNode=Node()
        if RightExpr[0]['type']=='ID':
            NewNode.data=OpStack[-1]['data']
            TempNode=FindSymbol(NewNode.data, CurrentFunctionSymbol.lable)
            NewNode.place=TempNode.place
            NewNode.type=TempNode.type
        elif RightExpr[0]['type']=='number':
            NewNode.data = OpStack[-1]['data']
            NewNode.type=OpStack[-1]['name'].lower()
        elif RightExpr[1]['type']=='expression':
            NewNode=copy.deepcopy(SemanticStack.pop(-1))
        NewNode.name= 'primary_expression'
        SemanticStack.append(NewNode)
    elif LeftExpr=='arithmetic_expression':
        NewNode=Node()
        NewNode.name= 'arithmetic_expression'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=copy.deepcopy(SemanticStack.pop(-1))
            NewNode.stack.insert(0,SemanticStack.pop(-1))
            NewNode.stack.insert(0, SemanticStack.pop(-1))
        SemanticStack.append(NewNode)
    elif LeftExpr=='constant_expression':
        NewNode = SemanticStack.pop(-1)
        NewNode.stack.insert(0, SemanticStack.pop(-1))
        NewNode.name= 'constant_expression'
        if len(NewNode.stack)==1:
            NewNode=copy.deepcopy(NewNode.stack[0])
        else:
            left=NewNode.stack.pop(0)
            while len(NewNode.stack)>0:
                op=NewNode.stack.pop(0)
                right=NewNode.stack.pop(0)
                if left.place==None:
                    arg1=left.data
                else:
                    arg1 =left.place
                if right.place==None:
                    arg2=right.data
                else:
                    arg2 =right.place
                if len(left.code)>0:
                    for code in left.code:
                        NewNode.code.append(code)
                if len(right.code)>0:
                    for code in right.code:
                        NewNode.code.append(code)
                result = Node()
                result.name = 'primary_expression'
                result.place = NewTemp()
                result.type = right.type
                if left.type!=right.type:
                    Token = Tokens[0]
                    print("type error in row{}".format(Token['row']))
                code=(op.type,arg1,arg2,result.place)
                NewNode.code.append(code)
                left=result
                NewNode.type=right.type
            NewNode.place=NewNode.code[-1][3]
        SemanticStack.append(NewNode)
    elif LeftExpr=='declaration_assign':
        NewNode = Node()
        if len(RightExpr)==2:
            name=OpStack[-3]['data']
            NewNode=SemanticStack.pop(-1)
            NewNode.id=name
        else:
            name = OpStack[-1]['data']
            NewNode.id = name
        SemanticStack.append(NewNode)
    elif LeftExpr=='declaration_init':
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'declaration_init'
        SemanticStack.append(NewNode)
    elif LeftExpr=='declaration_init_list':
        NewNode = Node()
        NewNode.name = 'declaration_init_list'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
        SemanticStack.append(NewNode)
    elif LeftExpr=='declaration':
        NewNode = SemanticStack.pop(-1)
        NewNode.stack.insert(0, SemanticStack.pop(-1))
        NewNode.name= 'declaration'
        type=SemanticStack.pop(-1).type
        for node in NewNode.stack:
            symbol = FindSymbol(node.id, CurrentFunctionSymbol.lable)
            if symbol!=None and symbol.function==CurrentFunctionSymbol.lable:
                Token = Tokens[0]
                print("multiple defination of {} in row{}".format(node.id,Token['row']))
            else:
                symbol=Symbol()
            if node.place==None:
                symbol.name=node.id
                symbol.place=NewTemp()
                symbol.type=type
                symbol.function=CurrentFunctionSymbol.lable
                symbol.size = 4
                global CurrentOffset
                symbol.offset = CurrentOffset
                CurrentOffset += symbol.size
                UpdateSymbolTable(symbol)
                if node.data!=None:
                    if(node.type!=type):
                        Token = Tokens[0]
                        print("type error in row{}".format(Token['row']))
                    code=(':=',node.data,'_',symbol.place)
                    NewNode.code.append(code)
            else:
                symbol.name=node.id
                symbol.place=node.place
                symbol.type=type
                symbol.function = CurrentFunctionSymbol.lable
                symbol.size = 4
                global CurrentOffset
                symbol.offset = CurrentOffset
                CurrentOffset += symbol.size
                UpdateSymbolTable(symbol)
                for code in node.code:
                    NewNode.code.append(code)
        NewNode.stack=[]
        SemanticStack.append(NewNode)
    elif LeftExpr=='assignment_expression':
        NewNode = SemanticStack.pop(-1)
        op=SemanticStack.pop(-1)
        name=OpStack[-3]['data']
        symbol = FindSymbol(name, CurrentFunctionSymbol.lable)
        if symbol == None:
            Token = Tokens[0]
            print("none defination of {} in row{}".format(name, Token['row']))
            symbol = Symbol()
            symbol.place=NewTemp()
            symbol.name=name
            symbol.type=NewNode.type
            symbol.function = CurrentFunctionSymbol.lable
            symbol.size=4
            global CurrentOffset
            symbol.offset=CurrentOffset
            CurrentOffset+=symbol.size
            UpdateSymbolTable(symbol)
        if NewNode.place==None:
            arg=NewNode.data
        else:
            arg = NewNode.place
        if len(op.type)==1:
            code=(':=',arg,'_',symbol.place)
            NewNode.code.append(code)
        else:
            code=(op.type[0],symbol.place,arg,symbol.place)
            NewNode.code.append(code)
        NewNode.name = 'assignment_expression'
        SemanticStack.append(NewNode)
    elif LeftExpr=='assignment_expression_profix':
        NewNode = Node()
        NewNode.name = 'assignment_expression_profix'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
        SemanticStack.append(NewNode)
    elif LeftExpr=='assignment_expression_list':
        NewNode = Node()
        NewNode.name = 'assignment_expression_list'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
            for node in NewNode.stack:
                for code in reversed(node.code):
                    NewNode.code.insert(0,code)
            NewNode.stack=[]
        SemanticStack.append(NewNode)
    elif LeftExpr=='expression':
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'expression'
        SemanticStack.append(NewNode)
    elif LeftExpr=='expression_profix':
        NewNode = Node()
        NewNode.name = 'expression_profix'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
        SemanticStack.append(NewNode)
    elif LeftExpr=='expression_list':
        NewNode = Node()
        NewNode.name = 'expression_list'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
            for node in reversed(NewNode.stack):
                for code in node.code:
                    NewNode.code.insert(0,code)
            #NewNode.stack=[]
        SemanticStack.append(NewNode)
    elif LeftExpr=='expression_statement':
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'expression_statement'
        SemanticStack.append(NewNode)
    elif LeftExpr=='statement':
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'statement'
        SemanticStack.append(NewNode)
    elif LeftExpr=='statement_list':
        NewNode = Node()
        NewNode.name = 'statement_list'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
            for node in NewNode.stack:
                for code in reversed(node.code):
                    NewNode.code.insert(0,code)
            NewNode.stack=[]
        SemanticStack.append(NewNode)
    elif LeftExpr=='compound_statement':
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'compound_statement'
        SemanticStack.append(NewNode)
    elif LeftExpr=='jump_statement':
        NewNode = Node()
        NewNode.name = 'jump_statement'
        NewNode.type=RightExpr[0]['type']
        if len(RightExpr)==3:
            temp=SemanticStack.pop(-1)
            if temp.place!=None:
                result=temp.place
            else:
                result = temp.data
            NewNode.code.append((':=', result, '_', 'v0'))
        NewNode.code.append((NewNode.type, '_', '_', '_'))
        SemanticStack.append(NewNode)
    elif LeftExpr=='selection_statement':
        NewNode = Node()
        NewNode.name = 'selection_statement'
        Node.true=NewLabel()
        Node.false=NewLabel()
        Node.end = NewLabel()
        FalseStmt=SemanticStack.pop(-1)
        TrueStmt = SemanticStack.pop(-1)
        Expression=SemanticStack.pop(-1)
        for code in  Expression.code:
            NewNode.code.append(code)
        NewNode.code.append(('j>',Expression.place,'0',Node.true))
        NewNode.code.append(('j','_','_',Node.false))
        NewNode.code.append((Node.true,':','_','_'))
        for code in TrueStmt.code:
            NewNode.code.append(code)
        NewNode.code.append(('j', '_', '_', Node.end))
        NewNode.code.append((Node.false,':','_','_'))
        for code in FalseStmt.code:
            NewNode.code.append(code)
        NewNode.code.append((Node.end,':','_','_'))
        SemanticStack.append(NewNode)
    elif LeftExpr=='iteration_statement':
        NewNode = Node()
        NewNode.name = 'iteration_statement'
        Node.true = NewLabel()
        Node.false = NewLabel()
        Node.begin = NewLabel()
        Node.end = NewLabel()
        if RightExpr[0]['type']=='while':
            Statement = SemanticStack.pop(-1)
            Expression=SemanticStack.pop(-1)
            NewNode.code.append((Node.begin,':','_','_'))
            for code in  Expression.code:
                NewNode.code.append(code)
            NewNode.code.append(('j>',Expression.place,'0',Node.true))
            NewNode.code.append(('j','_','_',Node.false))
            NewNode.code.append((Node.true,':','_','_'))
            for code in Statement.code:
                if code[0]=='break':
                    NewNode.code.append(('j','_','_',Node.false))
                elif code[0]=='continue':
                    NewNode.code.append(('j','_','_',Node.begin))
                else:
                    NewNode.code.append(code)
            NewNode.code.append(('j', '_', '_', Node.begin))
            NewNode.code.append((Node.false,':','_','_'))
        elif RightExpr[0]['type']=='for':
            Statement= SemanticStack.pop(-1)
            Assign= SemanticStack.pop(-1)
            Expression=SemanticStack.pop(-1)
            Declaration=SemanticStack.pop(-1)
            for code in  Declaration.code:
                NewNode.code.append(code)
            NewNode.code.append((Node.begin,':','_','_'))
            for code in  Expression.code:
                NewNode.code.append(code)
            NewNode.code.append(('j>',Expression.place,'0',Node.true))
            NewNode.code.append(('j','_','_',Node.false))
            NewNode.code.append((Node.true,':','_','_'))
            IsContinueExisted=False
            for code in Statement.code:
                if code[0]=='break':
                    NewNode.code.append(('j','_','_',Node.false))
                elif code[0]=='continue':
                    NewNode.code.append(('j','_','_',Node.end))
                    IsContinueExisted=True
                else:
                    NewNode.code.append(code)
            if IsContinueExisted:
                NewNode.code.append((Node.end,':','_','_'))
            for code in Assign.code:
                NewNode.code.append(code)
            NewNode.code.append(('j', '_', '_', Node.begin))
            NewNode.code.append((Node.false,':','_','_'))
        SemanticStack.append(NewNode)
    elif LeftExpr=='function_declaration':
        NewNode = Node()
        NewNode.name = 'function_declaration'
        name = OpStack[-1]['data']
        NewNode.id = name
        NewNode.type=SemanticStack.pop(-1).type
        NewNode.place=NewTemp()
        SemanticStack.append(NewNode)
    elif LeftExpr=='function_declaration_suffix':
        NewNode = Node()
        NewNode.name = 'function_declaration_suffix'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
        SemanticStack.append(NewNode)
    elif LeftExpr == 'function_declaration_list':
        NewNode = Node()
        NewNode.name = 'function_declaration_list'
        if len(RightExpr) == 1:
            NewNode.stack = []
        else:
            NewNode = SemanticStack.pop(-1)
            NewNode.stack.insert(0, SemanticStack.pop(-1))
        SemanticStack.append(NewNode)
    elif LeftExpr == 'function_definition':
        global CurrentFunctionSymbol
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'function_definition'
        function=FunctionSymbol()
        Type=SemanticStack.pop(-1)
        function.type=Type.type
        function.name=OpStack[-4]['data']
        if function.name=='main':
            function.lable ='main'
        else:
            function.lable=NewFunction()
        for arg in NewNode.stack:
            symbol=Symbol()
            symbol.name=arg.id
            symbol.type=arg.type
            symbol.place=arg.place
            symbol.function = function.lable
            symbol.size=4
            global CurrentOffset
            symbol.offset=CurrentOffset
            CurrentOffset+=symbol.size
            UpdateSymbolTable(symbol)
            function.params.append((arg.id,arg.type,arg.place))
        NewNode.data=function.lable
        UpdateFunctionTable(function)
        CurrentFunctionSymbol=function
        SemanticStack.append(NewNode)
    elif LeftExpr == 'function_implement':
        NewNode = SemanticStack.pop(-1)
        Definition=SemanticStack.pop(-1)
        NewNode.name = 'function_implement'
        tempcode=[]
        tempcode.append((Definition.data,':','_','_'))
        for node in Definition.stack:
            tempcode.append(('pop','_',4*Definition.stack.index(node),node.place))
        if len(Definition.stack)>0:
            tempcode.append(('-', 'fp', 4*len(Definition.stack), 'fp'))
        for code in reversed(tempcode):
            NewNode.code.insert(0,code)
        end=NewNode.code[-1]
        if end[0][0]=='l':
            lable=end[0]
            NewNode.code.remove(end)
            for code in NewNode.code:
                if code[3]==lable:
                    NewNode.code.remove(code)
        SemanticStack.append(NewNode)
    elif LeftExpr == 'function_expression':
        function = FindFunctionByName(OpStack[-4]['data'])
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'function_expression'
        tempcode=[]
        TempList = copy.deepcopy(CurrentFunctionSymbol.params)
        tempcode.append(('-', 'sp', 4 * len(TempList)+4, 'sp'))
        tempcode.append(('store', '_', 4 * len(TempList), 'ra'))
        for node in TempList:
            tempcode.append(('store','_',4 * TempList.index(node),node[2]))
        for code in reversed(tempcode):
            NewNode.code.insert(0,code)

        if len(function.params)>0:
            NewNode.code.append(('+', 'fp', 4*len(function.params), 'fp'))
        for node in NewNode.stack:
            if node.place!=None:
                result=node.place
            else:
                result = node.data
            NewNode.code.append(('push','_',4*NewNode.stack.index(node),result))
        NewNode.code.append(('call', '_', '_', function.lable))

        TempList.reverse()
        for node in TempList:
            NewNode.code.append(('load', '_', 4 * TempList.index(node), node[2]))
        NewNode.code.append(('load', '_', 4 * len(TempList), 'ra'))
        NewNode.code.append(('+', 'sp', 4 * len(CurrentFunctionSymbol.params) + 4, 'sp'))

        NewNode.place=NewTemp()
        NewNode.code.append((':=', 'v0', '_', NewNode.place))
        SemanticStack.append(NewNode)
    elif LeftExpr =='external_declaration':
        NewNode = SemanticStack.pop(-1)
        NewNode.name = 'external_declaration'
        SemanticStack.append(NewNode)
    elif LeftExpr =='start':
        NewNode = Node()
        NewNode.name = 'start'
        if len(RightExpr)==1:
            NewNode.stack=[]
        else:
            NewNode=SemanticStack.pop(-1)
            NewNode.stack.insert(0,SemanticStack.pop(-1))
            for node in NewNode.stack:
                for code in reversed(node.code):
                    NewNode.code.insert(0,code)
            NewNode.stack=[]
        SemanticStack.append(NewNode)
    return
def PrintIntermediateCode(codes):
    fd=open(GetFilePath("result.middle"),'w')
    for code in codes:
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
    return
def GetReg(temp,codes):
    global Mips
    global Regs
    if str(temp)[0]!='t':
        return temp
    if temp in TempValueStatus.keys():
        if TempValueStatus[temp]=='reg':
            for key in Regs:
                if Regs[key]==temp:
                    return key
    while True:
        for key in Regs:
            if Regs[key]=='':
                Regs[key] =temp
                TempValueStatus[temp]='reg'
                return key
        FreeReg(codes)
def FreeReg(codes):
    global Regs
    used=Regs.values()
    if '' in used:
        used.remove('')
    data={}
    for code in codes:
        for item in code:
            temp=str(item)
            if temp[0]=='t':
                if temp in used:
                    if temp in data.keys():
                        data[temp]+=1
                    else:
                        data[temp] =1
    flag=False
    for item in used:
        if item not in data.keys():
            for key in Regs.keys():
                if Regs[key]==item:
                    Regs[key]=''
                    TempValueStatus[item] = 'memory'
                    flag=True
    if flag:
        return
    sorted(data.items(),key=lambda x:x[1])
    freed=data.keys()[0]
    for key in Regs:
        if Regs[key]==freed:
            for item in SymbolTable:
                if item.place==freed:
                    Mips.append('addi $at,$zero,0x{}'.format(DataSegment))
                    Mips.append('sw {},{}($at)'.format(key,item.offset))
                    Regs[key] = ''
                    TempValueStatus[freed]='memory'
                    return
def GenerateMips(codes):
    global TempValueStatus
    remain=codes
    TempValueStatus={x.place:'memory' for x in SymbolTable}
    Mips.append("addiu $sp,$zero,0x{}".format(DataSegment+StackOffset))
    Mips.append("or $fp,$sp,$zero")
    while len(remain)>0:
        tempcode=remain.pop(0)
        code=[]
        for item in tempcode:
            if item=='v0':
                code.append('$v0')
            else:
                code.append(item)
        if code[0] == ':=':
            arg1=GetReg(code[3],remain)
            arg3=GetReg(code[1],remain)
            Mips.append('add {},$zero,{}'.format(arg1, arg3))
        elif code[1] == ':':
            if code[0][0]=='f':
                Mips.append('')
            Mips.append('{}:'.format(code[0]))
        elif code[0] == 'call':
            Mips.append('jal  {}'.format(code[3]))
        elif code[0] == 'push':
            if code[3]=='ra':
                Mips.append('sw $ra,{}($fp)'.format(code[2]))
            else:
                reg=GetReg(code[3],remain)
                if str(reg)[0] != '$':
                    Mips.append("add $a0,$zero,{}".format(reg))
                    reg = '$a0'
                Mips.append('sw {},{}($fp)'.format(reg,code[2]))
        elif code[0] == 'pop':
            if code[3]=='ra':
                Mips.append('lw $ra,{}($fp)'.format(code[2]))
            else:
                reg = GetReg(code[3], remain)
                Mips.append('lw {},{}($fp)'.format(reg,code[2]))
        elif code[0] == 'store':
            if code[3]=='ra':
                Mips.append('sw $ra,{}($sp)'.format(code[2]))
            else:
                reg=GetReg(code[3],remain)
                if str(reg)[0] != '$':
                    Mips.append("add $a0,$zero,{}".format(reg))
                    reg = '$a0'
                Mips.append('sw {},{}($sp)'.format(reg,code[2]))
        elif code[0] == 'load':
            if code[3]=='ra':
                Mips.append('lw $ra,{}($sp)'.format(code[2]))
            else:
                reg = GetReg(code[3], remain)
                Mips.append('lw {},{}($sp)'.format(reg,code[2]))
        elif code[0] == 'j':
            Mips.append('j {}'.format(code[3]))
        elif code[0] == 'j>':
            arg1=GetReg(code[1],remain)
            Mips.append('bgt {},$zero,{}'.format(arg1, code[3]))
        elif code[0] == 'return':
            Mips.append('jr $ra')
        else:
            if code[0]=='+':
                if code[1]=='fp':
                    Mips.append("add $fp,$fp,{}".format(code[2]))
                elif code[1]=='sp':
                    Mips.append("add $sp,$sp,{}".format(code[2]))
                else:
                    arg1= GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0]!='$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    Mips.append("add {},{},{}".format(arg3,arg1,arg2))
            elif code[0]=='-':
                if code[1]=='fp':
                    Mips.append("sub $fp,$fp,{}".format(code[2]))
                elif code[1]=='sp':
                    Mips.append("sub $sp,$sp,{}".format(code[2]))
                else:
                    arg1= GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0]!='$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("sub {},{},{}".format(arg3,arg1,arg2))
            elif code[0]=='*':
                    arg1= GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0]!='$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("mul {},{},{}".format(arg3,arg1,arg2))
            elif code[0]=='/':
                    arg1= GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0]!='$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("div {},{},{}".format(arg3,arg1,arg2))
            elif code[0]=='%':
                    arg1= GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0]!='$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("div {},{},{}".format(arg3,arg1,arg2))
                    Mips.append("mfhi {}".format(arg3))
            elif code[0]=='<':
                    arg1= GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0]!='$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("slt {},{},{}".format(arg3,arg1,arg2))
            elif code[0]=='>':
                    arg1= GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0]!='$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1='$a1'
                    if str(arg2)[0]!='$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("sgt {},{},{}".format(arg3,arg1,arg2))
            elif code[0]=='!=':
                    arg1 = GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0] != '$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("sne {},{},{}".format(arg3, arg1, arg2))
            elif code[0]=='==':
                    arg1 = GetReg(code[1], remain)
                    arg2 = GetReg(code[2], remain)
                    arg3 = GetReg(code[3], remain)
                    if str(arg1)[0] != '$':
                        Mips.append("add $a1,$zero,{}".format(arg1))
                        arg1 = '$a1'
                    if str(arg2)[0] != '$':
                        Mips.append("add $a2,$zero,{}".format(arg2))
                        arg2 = '$a2'
                    Mips.append("seq {},{},{}".format(arg3, arg1, arg2))
    return
CurrentLable=0
CurrentTemp=0
CurrentFunction=0
CurrentStep=0
CurrentOffset=0
CurrentProduction=None
CurrentFunctionSymbol=None
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
OpStack = []
StateStack = []
Table=None
SymbolTable=[]
FunctionTable=[]
SemanticStack=[]
Tokens=[]
Regs={'$'+str(x):'' for x in range(7,26)}
TempValueStatus={}
Mips=[]
StackOffset=8000
DataSegment=10010000
def SyntaxParserTable():
    ReadGrammer(GetFilePath("grammer.txt"))
    GenerateDotedproductions()
    GenerateFirst()
    GenerateDFA()
    GenerateTable()
    PrintTable()
    return True
def MipsGenerate():
    ReadGrammer(GetFilePath("grammer.txt"))
    GenerateDotedproductions()
    GenerateFirst()
    GenerateDFA()
    GenerateTable()
    PrintTable()
    global Tokens
    Tokens=main(GetFilePath("test.c--"))
    MakeAnalyse()
    codes=SemanticStack[0].code
    codes.insert(0,('call','_','_','end'))
    codes.insert(0, ('call', '_', '_', 'main'))
    PrintIntermediateCode(codes)
    GenerateMips(codes)
    with open(GetFilePath("result.asm"),'w') as f:
        for code in Mips:
            if code == 'main:':
                f.write('\n')
            f.write(code+'\n')
        f.write('end:\n')
    return True
def BeginSemanticAnalysis():
    ReadGrammer(GetFilePath("grammer.txt"))
    GenerateDotedproductions()
    GenerateFirst()
    GenerateDFA()
    GenerateTable()
    PrintTable()
    global Tokens
    Tokens=main(GetFilePath("test.c--"))
    MakeAnalyse()
    codes=SemanticStack[0].code
    codes.insert(0,('call','_','_','end'))
    codes.insert(0, ('call', '_', '_', 'main'))
    PrintIntermediateCode(codes)
    return True